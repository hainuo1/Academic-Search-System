# ============================================================
# backend/routes/document.py —— 文献操作 API 模块
# ============================================================

import os, uuid
import pdfplumber
from flask import Blueprint, request, jsonify, send_file, current_app

from db import get_connection
from utils import process_keywords, login_required, verify_token

doc_bp = Blueprint('document', __name__)


def _get_user_id():
    auth = request.headers.get('Authorization', '')
    token = auth.replace('Bearer ', '') if auth else ''
    if not token:
        token = request.args.get('token', '')
    if token:
        payload = verify_token(token)
        if payload:
            return payload['user_id']
    return None


# ── 详情 ──────────────────────────────────────────────
@doc_bp.route('/api/document/<int:did>')
@login_required
def detail(did):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DocumentID,Title,Author,Abstract,PublishDate,Category,FilePath,ViewCount,DownloadCount FROM Documents WHERE DocumentID=%s", (did,))
    doc = cur.fetchone()
    if not doc:
        return jsonify({'code': 404, 'message': '文献不存在', 'data': None})

    cur.execute("UPDATE Documents SET ViewCount=ViewCount+1 WHERE DocumentID=%s", (did,))
    conn.commit()
    try:
        cur.execute("INSERT INTO BrowseHistory(UserID,DocumentID,ViewTime) VALUES(%s,%s,NOW())", (request.user_id, did))
        conn.commit()
    except Exception:
        pass

    cur.execute("SELECT k.KeywordName FROM Keywords k INNER JOIN DocumentKeyword dk ON k.KeywordID=dk.KeywordID WHERE dk.DocumentID=%s", (did,))
    kws = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT d.DocumentID,d.Title FROM Citation c INNER JOIN Documents d ON c.SourceDocumentID=d.DocumentID WHERE c.TargetDocumentID=%s", (did,))
    cits = [{'id': r[0], 'title': r[1]} for r in cur.fetchall()]

    cur.execute("SELECT FavoriteID FROM Favorites WHERE UserID=%s AND DocumentID=%s", (request.user_id, did))
    fav = cur.fetchone() is not None

    return jsonify({'code': 200, 'message': 'ok', 'data': {
        'document': {'id': doc.DocumentID, 'title': doc.Title, 'author': doc.Author,
                     'abstract': doc.Abstract or '', 'publish_date': str(doc.PublishDate) if doc.PublishDate else '',
                     'category': doc.Category or '', 'file_path': doc.FilePath or '',
                     'view_count': doc.ViewCount, 'download_count': doc.DownloadCount},
        'keywords': kws, 'citations': cits, 'citation_count': len(cits), 'is_favorited': fav}})


# ── 上传 ──────────────────────────────────────────────
@doc_bp.route('/api/upload', methods=['POST'])
@login_required
def upload():
    title = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    cat = request.form.get('category', '').strip()
    pd = request.form.get('publish_date', '').strip()
    kwr = request.form.get('keywords', '').strip()
    ab = request.form.get('abstract', '').strip()
    pdf = request.files.get('pdf_file')

    if not all([title, author, cat, pd, kwr, ab]):
        return jsonify({'code': 400, 'message': '所有字段都必须填写', 'data': None})
    if not pdf or pdf.filename == '':
        return jsonify({'code': 400, 'message': '请选择要上传的 PDF 文件', 'data': None})
    if not pdf.filename.lower().endswith('.pdf'):
        return jsonify({'code': 400, 'message': '只允许上传 PDF 格式的文件', 'data': None})

    fname = str(uuid.uuid4()) + '.pdf'
    spath = os.path.join(current_app.config['UPLOAD_FOLDER'], fname)
    pdf.save(spath)

    ftxt, err = "", None
    try:
        with pdfplumber.open(spath) as p:
            ftxt = "\n".join(page.extract_text() or "" for page in p.pages).strip()
    except Exception as e:
        err = str(e)

    fpath = os.path.join('uploads', fname)
    kwl = [k.strip() for k in kwr.split(';') if k.strip()]
    kwt = ';'.join(kwl)

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Documents(Title,Author,Abstract,PublishDate,Category,FilePath,UploadUserID,KeywordsText,`FullText`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (title, author, ab, pd, cat, fpath, request.user_id, kwt, ftxt))
        did = cur.lastrowid
        process_keywords(cur, did, kwl)
        conn.commit()
    except Exception as e:
        conn.rollback()
        if os.path.exists(spath): os.remove(spath)
        return jsonify({'code': 500, 'message': f'上传失败：{str(e)}', 'data': None})

    return jsonify({'code': 200, 'message': '上传成功' + (f'（PDF全文提取失败：{err}）' if err else ''), 'data': {'document_id': did}})


# ── 下载 ──────────────────────────────────────────────
def _find_pdf(file_path):
    """在多个可能路径中查找 PDF 文件，找到则返回绝对路径，否则返回 None"""
    if not file_path:
        return None

    # 路径1：相对于 backend/（current_app.root_path）
    ap = os.path.join(current_app.root_path, file_path)
    if os.path.exists(ap) and os.path.isfile(ap):
        return ap

    # 路径2：上一层目录（老数据在 3.0版本/uploads/）
    parent_ap = os.path.join(os.path.dirname(current_app.root_path), file_path)
    if os.path.exists(parent_ap) and os.path.isfile(parent_ap):
        return parent_ap

    # 路径3：uploads/ 也在 backend/ 内
    alt_ap = os.path.join(current_app.root_path, 'uploads', os.path.basename(file_path))
    if os.path.exists(alt_ap) and os.path.isfile(alt_ap):
        return alt_ap

    return None


@doc_bp.route('/api/download/<int:did>')
def download(did):
    user_id = _get_user_id()
    if not user_id:
        return jsonify({'code': 401, 'message': '请先登录', 'data': None})

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT FilePath,Title FROM Documents WHERE DocumentID=%s", (did,))
    d = cur.fetchone()
    if not d:
        return jsonify({'code': 404, 'message': '文献不存在', 'data': None})

    fp = d[0] or ''
    if not fp:
        return jsonify({'code': 404, 'message': '该文献没有上传 PDF 文件，无法下载', 'data': None})

    ap = _find_pdf(fp)
    if not ap:
        return jsonify({'code': 404, 'message': 'PDF 文件不存在，可能已被删除', 'data': None})

    cur.execute("UPDATE Documents SET DownloadCount=DownloadCount+1 WHERE DocumentID=%s", (did,))
    conn.commit()
    return send_file(ap, as_attachment=True, download_name=f"{d[1]}.pdf")


@doc_bp.route('/api/download/<int:did>/check')
@login_required
def check_download(did):
    """检查 PDF 文件是否存在（前端下载前先调这个接口验证）"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT FilePath,Title FROM Documents WHERE DocumentID=%s", (did,))
    d = cur.fetchone()
    if not d:
        return jsonify({'code': 404, 'message': '文献不存在', 'data': None})
    fp = d[0] or ''
    if not fp:
        return jsonify({'code': 400, 'message': '该文献没有上传 PDF 文件', 'data': None})
    ap = _find_pdf(fp)
    if not ap:
        return jsonify({'code': 404, 'message': 'PDF 文件不存在，可能已被删除', 'data': None})
    return jsonify({'code': 200, 'message': 'ok', 'data': None})


# ── 我的文献 ──────────────────────────────────────────
@doc_bp.route('/api/my_documents')
@login_required
def my_docs():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DocumentID,Title,Author,PublishDate,Category FROM Documents WHERE UploadUserID=%s ORDER BY UploadTime DESC", (request.user_id,))
    docs = [{'id': r.DocumentID, 'title': r.Title, 'author': r.Author,
             'publish_date': str(r.PublishDate) if r.PublishDate else '', 'category': r.Category or ''}
            for r in cur.fetchall()]
    return jsonify({'code': 200, 'message': 'ok', 'data': {'documents': docs}})


# ── 删除 ──────────────────────────────────────────────
@doc_bp.route('/api/document/<int:did>', methods=['DELETE'])
@login_required
def delete(did):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT UploadUserID,FilePath FROM Documents WHERE DocumentID=%s", (did,))
    d = cur.fetchone()
    if not d:
        return jsonify({'code': 404, 'message': '文献不存在', 'data': None})
    if d[0] != request.user_id:
        return jsonify({'code': 403, 'message': '你没有权限删除这篇文献', 'data': None})

    # 删除物理文件
    ap = _find_pdf(d[1]) if d[1] else None

    try:
        cur.execute("DELETE FROM Citation WHERE SourceDocumentID=%s OR TargetDocumentID=%s", (did, did))
        cur.execute("DELETE FROM BrowseHistory WHERE DocumentID=%s", (did,))
        cur.execute("DELETE FROM Favorites WHERE DocumentID=%s", (did,))
        cur.execute("DELETE FROM DocumentKeyword WHERE DocumentID=%s", (did,))
        cur.execute("DELETE FROM Documents WHERE DocumentID=%s", (did,))
        cur.execute("DELETE FROM Keywords WHERE KeywordID NOT IN (SELECT DISTINCT KeywordID FROM DocumentKeyword)")
        conn.commit()
        if ap and os.path.exists(ap): os.remove(ap)
    except Exception as e:
        conn.rollback()
        return jsonify({'code': 500, 'message': f'删除失败：{str(e)}', 'data': None})
    return jsonify({'code': 200, 'message': '文献已成功删除', 'data': None})


# ── 编辑 ──────────────────────────────────────────────
@doc_bp.route('/api/document/<int:did>', methods=['GET', 'PUT'])
@login_required
def edit(did):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT UploadUserID FROM Documents WHERE DocumentID=%s", (did,))
    dc = cur.fetchone()
    if not dc:
        return jsonify({'code': 404, 'message': '文献不存在', 'data': None})
    if dc[0] != request.user_id:
        return jsonify({'code': 403, 'message': '你没有权限编辑此文献', 'data': None})

    if request.method == 'GET':
        cur.execute("SELECT DocumentID,Title,Author,Abstract,PublishDate,Category,KeywordsText FROM Documents WHERE DocumentID=%s", (did,))
        d = cur.fetchone()
        return jsonify({'code': 200, 'message': 'ok', 'data': {'document': {
            'id': d.DocumentID, 'title': d.Title, 'author': d.Author,
            'abstract': d.Abstract or '', 'publish_date': str(d.PublishDate) if d.PublishDate else '',
            'category': d.Category or '', 'keywords': d.KeywordsText or ''}}})

    d = request.get_json() or {}
    t, a, c, pd, kr, ab = d.get('title', '').strip(), d.get('author', '').strip(), d.get('category', '').strip(), d.get('publish_date', '').strip(), d.get('keywords', '').strip(), d.get('abstract', '').strip()
    if not all([t, a, c, pd, kr, ab]):
        return jsonify({'code': 400, 'message': '所有字段都必须填写', 'data': None})
    kwl = [k.strip() for k in kr.split(';') if k.strip()]
    if not kwl:
        return jsonify({'code': 400, 'message': '至少需要填写一个关键词', 'data': None})

    try:
        cur.execute("UPDATE Documents SET Title=%s,Author=%s,Abstract=%s,PublishDate=%s,Category=%s,KeywordsText=%s WHERE DocumentID=%s",
                    (t, a, ab, pd, c, ';'.join(kwl), did))
        cur.execute("DELETE FROM DocumentKeyword WHERE DocumentID=%s", (did,))
        process_keywords(cur, did, kwl)
        cur.execute("DELETE FROM Keywords WHERE KeywordID NOT IN (SELECT DISTINCT KeywordID FROM DocumentKeyword)")
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'code': 500, 'message': f'保存失败：{str(e)}', 'data': None})
    return jsonify({'code': 200, 'message': '保存成功', 'data': None})
