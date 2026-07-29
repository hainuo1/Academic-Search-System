"""
文献操作路由 —— 详情 / 上传 / 下载 / 我的文献 / 删除 / 编辑
"""
import os, re, uuid
import pdfplumber
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings

router = APIRouter(prefix="/api", tags=["document"])


def _find_pdf(file_path: str) -> str | None:
    if not file_path:
        return None
    # 相对于 backend/
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = os.path.join(backend_dir, file_path)
    if os.path.exists(ap) and os.path.isfile(ap):
        return ap
    # uploads/ 子目录
    alt = os.path.join(backend_dir, "uploads", os.path.basename(file_path))
    if os.path.exists(alt) and os.path.isfile(alt):
        return alt
    return None


def _process_keywords(db: Session, doc_id: int, keywords_list: list[str]):
    for kw in keywords_list:
        row = db.execute(text("SELECT keyword_id FROM keywords WHERE keyword_name=:kw"), {"kw": kw}).fetchone()
        if row:
            kid = row.keyword_id
        else:
            result = db.execute(text("INSERT INTO keywords (keyword_name) VALUES (:kw) RETURNING keyword_id"), {"kw": kw})
            kid = result.scalar()
        db.execute(
            text("INSERT INTO document_keyword (document_id, keyword_id, tf_idf) VALUES (:did, :kid, 1.0) ON CONFLICT DO NOTHING"),
            {"did": doc_id, "kid": kid},
        )


# ── 详情 ──────────────────────────────────────────────
@router.get("/document/{did}")
def detail(did: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.execute(text(
        "SELECT document_id, title, author, abstract, publish_date, category, file_path, view_count, download_count "
        "FROM documents WHERE document_id = :did"
    ), {"did": did}).fetchone()
    if not doc:
        raise HTTPException(status_code=404, detail="文献不存在")

    db.execute(text("UPDATE documents SET view_count = view_count + 1 WHERE document_id = :did"), {"did": did})
    db.commit()
    try:
        db.execute(text("INSERT INTO browse_history(user_id, document_id, view_time) VALUES(:uid, :did, NOW())"),
                   {"uid": current_user["user_id"], "did": did})
        db.commit()
    except Exception:
        pass

    # 关键词
    kw_rows = db.execute(text(
        "SELECT k.keyword_name FROM keywords k JOIN document_keyword dk ON k.keyword_id = dk.keyword_id WHERE dk.document_id = :did"
    ), {"did": did}).fetchall()
    kws = [r[0] for r in kw_rows]

    # 引用 —— 两个方向都要查
    # 被哪些文献引用（当前文献是 target）
    cited_by_rows = db.execute(text(
        "SELECT d.document_id, d.title FROM citation c JOIN documents d ON c.source_document_id = d.document_id WHERE c.target_document_id = :did ORDER BY d.document_id DESC LIMIT 20"
    ), {"did": did}).fetchall()
    cited_by = [{"id": r[0], "title": r[1]} for r in cited_by_rows]

    # 引用了哪些文献（当前文献是 source）
    cites_rows = db.execute(text(
        "SELECT d.document_id, d.title FROM citation c JOIN documents d ON c.target_document_id = d.document_id WHERE c.source_document_id = :did ORDER BY d.document_id DESC LIMIT 20"
    ), {"did": did}).fetchall()
    cites = [{"id": r[0], "title": r[1]} for r in cites_rows]

    # 是否已收藏
    fav = db.execute(text(
        "SELECT favorite_id FROM favorites WHERE user_id = :uid AND document_id = :did"
    ), {"uid": current_user["user_id"], "did": did}).fetchone()

    return {"code": 200, "message": "ok", "data": {
        "document": {
            "id": doc.document_id, "title": doc.title, "author": doc.author,
            "abstract": doc.abstract or "", "publish_date": str(doc.publish_date) if doc.publish_date else "",
            "category": doc.category or "", "file_path": doc.file_path or "",
            "view_count": doc.view_count, "download_count": doc.download_count,
        },
        "keywords": kws,
        "citations": cited_by, "cites": cites,
        "cited_by_count": len(cited_by), "cites_count": len(cites),
        "is_favorited": fav is not None,
    }}


# ── 上传 ──────────────────────────────────────────────
@router.post("/upload")
def upload(
    title: str = Form(...),
    author: str = Form(...),
    category: str = Form(...),
    publish_date: str = Form(...),
    keywords: str = Form(...),
    abstract: str = Form(...),
    pdf_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not all([title, author, category, publish_date, keywords, abstract]):
        raise HTTPException(status_code=400, detail="所有字段都必须填写")
    if not pdf_file.filename or not pdf_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="只允许上传 PDF 格式的文件")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    fname = str(uuid.uuid4()) + ".pdf"
    spath = os.path.join(settings.UPLOAD_DIR, fname)

    with open(spath, "wb") as f:
        f.write(pdf_file.file.read())

    ftxt, err = "", None
    try:
        with pdfplumber.open(spath) as p:
            ftxt = "\n".join(page.extract_text() or "" for page in p.pages).strip()
    except Exception as e:
        err = str(e)

    fpath = os.path.join("uploads", fname)
    kwl = [k.strip() for k in keywords.split(";") if k.strip()]
    kwt = ";".join(kwl)

    try:
        result = db.execute(text(
            "INSERT INTO documents (title, author, abstract, publish_date, category, file_path, upload_user_id, keywords_text, full_text) "
            "VALUES (:t, :a, :ab, :pd, :cat, :fp, :uid, :kwt, :ft) RETURNING document_id"
        ), {
            "t": title, "a": author, "ab": abstract, "pd": publish_date,
            "cat": category, "fp": fpath, "uid": current_user["user_id"],
            "kwt": kwt, "ft": ftxt,
        })
        did = result.scalar()
        _process_keywords(db, did, kwl)
        db.commit()
    except Exception as e:
        db.rollback()
        if os.path.exists(spath):
            os.remove(spath)
        raise HTTPException(status_code=500, detail=f"上传失败：{str(e)}")

    return {"code": 200, "message": "上传成功" + (f"（PDF全文提取失败：{err}）" if err else ""), "data": {"document_id": did}}


# ── 下载 ──────────────────────────────────────────────
@router.get("/download/{did}")
def download(did: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    d = db.execute(text("SELECT file_path, title, author FROM documents WHERE document_id = :did"), {"did": did}).fetchone()
    if not d:
        raise HTTPException(status_code=404, detail="文献不存在")
    if not d.file_path:
        raise HTTPException(status_code=404, detail="该文献没有上传 PDF 文件")

    ap = _find_pdf(d.file_path)
    if not ap:
        raise HTTPException(status_code=404, detail="PDF 文件不存在，可能已被删除")

    db.execute(text("UPDATE documents SET download_count = download_count + 1 WHERE document_id = :did"), {"did": did})
    db.commit()
    safe_name = re.sub(r'[\\/:*?"<>|]', '_', f"{d.title}-{d.author}")
    return FileResponse(ap, filename=f"{safe_name}.pdf", media_type="application/pdf")


@router.get("/download/{did}/check")
def check_download(did: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    d = db.execute(text("SELECT file_path, title FROM documents WHERE document_id = :did"), {"did": did}).fetchone()
    if not d:
        raise HTTPException(status_code=404, detail="文献不存在")
    if not d.file_path:
        return {"code": 400, "message": "该文献没有上传 PDF 文件", "data": None}
    ap = _find_pdf(d.file_path)
    if not ap:
        raise HTTPException(status_code=404, detail="PDF 文件不存在，可能已被删除")
    return {"code": 200, "message": "ok", "data": None}


# ── 我的文献 ──────────────────────────────────────────
@router.get("/my_documents")
def my_docs(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.execute(text(
        "SELECT document_id, title, author, publish_date, category FROM documents "
        "WHERE upload_user_id = :uid ORDER BY upload_time DESC"
    ), {"uid": current_user["user_id"]}).fetchall()
    docs = [
        {"id": r.document_id, "title": r.title, "author": r.author,
         "publish_date": str(r.publish_date) if r.publish_date else "", "category": r.category or ""}
        for r in rows
    ]
    return {"code": 200, "message": "ok", "data": {"documents": docs}}


# ── 删除 ──────────────────────────────────────────────
@router.delete("/document/{did}")
def delete(did: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    d = db.execute(text("SELECT upload_user_id, file_path FROM documents WHERE document_id = :did"), {"did": did}).fetchone()
    if not d:
        raise HTTPException(status_code=404, detail="文献不存在")
    if d.upload_user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="你没有权限删除这篇文献")

    ap = _find_pdf(d.file_path) if d.file_path else None
    try:
        db.execute(text("DELETE FROM citation WHERE source_document_id = :did OR target_document_id = :did"), {"did": did})
        db.execute(text("DELETE FROM browse_history WHERE document_id = :did"), {"did": did})
        db.execute(text("DELETE FROM favorites WHERE document_id = :did"), {"did": did})
        db.execute(text("DELETE FROM document_keyword WHERE document_id = :did"), {"did": did})
        db.execute(text("DELETE FROM documents WHERE document_id = :did"), {"did": did})
        db.execute(text("DELETE FROM keywords WHERE keyword_id NOT IN (SELECT DISTINCT keyword_id FROM document_keyword)"))
        db.commit()
        if ap and os.path.exists(ap):
            os.remove(ap)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败：{str(e)}")
    return {"code": 200, "message": "文献已成功删除", "data": None}


# ── 编辑 ── 使用独立路径避免与详情接口冲突
@router.get("/document/{did}/edit-data")
def edit_data(did: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取文献编辑数据（仅上传者本人可访问）"""
    d_owner = db.execute(text("SELECT upload_user_id FROM documents WHERE document_id = :did"), {"did": did}).fetchone()
    if not d_owner:
        raise HTTPException(status_code=404, detail="文献不存在")
    if d_owner.upload_user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="你没有权限编辑此文献")

    d = db.execute(text(
        "SELECT document_id, title, author, abstract, publish_date, category, keywords_text FROM documents WHERE document_id = :did"
    ), {"did": did}).fetchone()
    return {"code": 200, "message": "ok", "data": {"document": {
        "id": d.document_id, "title": d.title, "author": d.author,
        "abstract": d.abstract or "", "publish_date": str(d.publish_date) if d.publish_date else "",
        "category": d.category or "", "keywords": d.keywords_text or "",
    }}}


@router.put("/document/{did}")
def update_document(
    did: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    body: dict = None,
):
    """更新文献元数据（仅上传者本人）"""
    d_owner = db.execute(text("SELECT upload_user_id FROM documents WHERE document_id = :did"), {"did": did}).fetchone()
    if not d_owner:
        raise HTTPException(status_code=404, detail="文献不存在")
    if d_owner.upload_user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="你没有权限编辑此文献")
    t = body.get("title", "").strip()
    a = body.get("author", "").strip()
    c = body.get("category", "").strip()
    pd = body.get("publish_date", "").strip()
    kr = body.get("keywords", "").strip()
    ab = body.get("abstract", "").strip()

    if not all([t, a, c, pd, kr, ab]):
        raise HTTPException(status_code=400, detail="所有字段都必须填写")
    kwl = [k.strip() for k in kr.split(";") if k.strip()]
    if not kwl:
        raise HTTPException(status_code=400, detail="至少需要填写一个关键词")

    try:
        db.execute(text(
            "UPDATE documents SET title=:t, author=:a, abstract=:ab, publish_date=:pd, category=:c, keywords_text=:kt WHERE document_id=:did"
        ), {"t": t, "a": a, "ab": ab, "pd": pd, "c": c, "kt": ";".join(kwl), "did": did})
        db.execute(text("DELETE FROM document_keyword WHERE document_id = :did"), {"did": did})
        _process_keywords(db, did, kwl)
        db.execute(text("DELETE FROM keywords WHERE keyword_id NOT IN (SELECT DISTINCT keyword_id FROM document_keyword)"))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存失败：{str(e)}")
    return {"code": 200, "message": "保存成功", "data": None}
