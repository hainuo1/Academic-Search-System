"""
引用关系路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/api", tags=["citation"])


@router.get("/citation/{did}")
def get_cit(did: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    d = db.execute(text("SELECT document_id, title, upload_user_id FROM documents WHERE document_id = :did"), {"did": did}).fetchone()
    if not d:
        raise HTTPException(status_code=404, detail="文献不存在")
    if d.upload_user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="你没有权限设置此文献的引用关系")
    sids = db.execute(text("SELECT target_document_id FROM citation WHERE source_document_id = :did"), {"did": did}).fetchall()
    return {"code": 200, "message": "ok", "data": {"current_doc": {"id": d.document_id, "title": d.title}, "selected_ids": [r[0] for r in sids]}}


@router.get("/search_citation")
def search_cit(
    keyword: str = Query(default=""),
    doc_id: int = Query(default=0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not keyword:
        return {"code": 200, "message": "ok", "data": {"results": []}}
    rows = db.execute(text(
        "SELECT document_id, title, author FROM documents WHERE title ILIKE :kw AND document_id != :did ORDER BY document_id DESC LIMIT 20"
    ), {"kw": f"%{keyword}%", "did": doc_id}).fetchall()
    return {"code": 200, "message": "ok", "data": {"results": [{"id": r[0], "title": r[1], "author": r[2]} for r in rows]}}


@router.post("/save_citation/{did}")
def save_cit(did: int, body: dict, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    d = db.execute(text("SELECT upload_user_id FROM documents WHERE document_id = :did"), {"did": did}).fetchone()
    if not d or d.upload_user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="你没有权限修改此文献的引用关系")

    tids = body.get("target_doc_ids", [])
    try:
        tids = [int(x) for x in tids]
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="无效的文献ID格式")

    if tids:
        ph = ",".join([":tid" + str(i) for i in range(len(tids))])
        param_dict = {f"tid{i}": tids[i] for i in range(len(tids))}
        ex_rows = db.execute(text(f"SELECT document_id FROM documents WHERE document_id IN ({ph})"), param_dict).fetchall()
        ex = {r[0] for r in ex_rows}
        inv = set(tids) - ex
        if inv:
            raise HTTPException(status_code=400, detail=f"以下文献不存在：{list(inv)}")

    try:
        db.execute(text("DELETE FROM citation WHERE source_document_id = :did"), {"did": did})
        for tid in tids:
            if tid != did:
                db.execute(text("INSERT INTO citation(source_document_id, target_document_id) VALUES(:s, :t)"), {"s": did, "t": tid})
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存失败：{str(e)}")
    return {"code": 200, "message": "引用关系保存成功", "data": None}
