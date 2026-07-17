from flask import Blueprint, request, jsonify
from db import get_connection
from utils import login_required

cit_bp = Blueprint('citation', __name__)


@cit_bp.route('/api/citation/<int:did>')
@login_required
def get_cit(did):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DocumentID,Title,UploadUserID FROM Documents WHERE DocumentID=%s", (did,))
    d = cur.fetchone()
    if not d:
        return jsonify({'code': 404, 'message': '文献不存在', 'data': None})
    if d[2] != request.user_id:
        return jsonify({'code': 403, 'message': '你没有权限设置此文献的引用关系', 'data': None})
    cur.execute("SELECT TargetDocumentID FROM Citation WHERE SourceDocumentID=%s", (did,))
    sids = [r[0] for r in cur.fetchall()]
    return jsonify({'code': 200, 'message': 'ok', 'data': {'current_doc': {'id': d[0], 'title': d[1]}, 'selected_ids': sids}})


@cit_bp.route('/api/search_citation')
@login_required
def search_cit():
    kw = request.args.get('keyword', '').strip()
    did = request.args.get('doc_id', type=int)
    if not kw:
        return jsonify({'code': 200, 'message': 'ok', 'data': {'results': []}})
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DocumentID,Title,Author FROM Documents WHERE Title LIKE %s AND DocumentID!=%s ORDER BY DocumentID DESC LIMIT 20",
                ('%' + kw + '%', did))
    return jsonify({'code': 200, 'message': 'ok', 'data': {'results': [{'id': r[0], 'title': r[1], 'author': r[2]} for r in cur.fetchall()]}})


@cit_bp.route('/api/save_citation/<int:did>', methods=['POST'])
@login_required
def save_cit(did):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT UploadUserID FROM Documents WHERE DocumentID=%s", (did,))
    d = cur.fetchone()
    if not d or d[0] != request.user_id:
        return jsonify({'code': 403, 'message': '你没有权限修改此文献的引用关系', 'data': None})

    data = request.get_json() or {}
    tids = data.get('target_doc_ids', [])
    try:
        tids = [int(x) for x in tids]
    except (ValueError, TypeError):
        return jsonify({'code': 400, 'message': '无效的文献ID格式', 'data': None})

    if tids:
        ph = ','.join(['%s'] * len(tids))
        cur.execute(f"SELECT DocumentID FROM Documents WHERE DocumentID IN ({ph})", tids)
        ex = {r[0] for r in cur.fetchall()}
        inv = set(tids) - ex
        if inv:
            return jsonify({'code': 400, 'message': f'以下文献不存在：{list(inv)}', 'data': None})

    try:
        cur.execute("DELETE FROM Citation WHERE SourceDocumentID=%s", (did,))
        for tid in tids:
            if tid != did:
                cur.execute("INSERT INTO Citation(SourceDocumentID,TargetDocumentID) VALUES(%s,%s)", (did, tid))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'code': 500, 'message': f'保存失败：{str(e)}', 'data': None})
    return jsonify({'code': 200, 'message': '引用关系保存成功', 'data': None})
