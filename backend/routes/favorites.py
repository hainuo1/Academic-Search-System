from flask import Blueprint, request, jsonify
from db import get_connection
from utils import get_pagination, login_required

fav_bp = Blueprint('favorites', __name__)


@fav_bp.route('/api/favorites')
@login_required
def list_fav():
    pp = 10
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Favorites WHERE UserID=%s", (request.user_id,))
    total = cur.fetchone()[0]
    page, offset, pages = get_pagination(request.args.get('page'), total, pp)
    cur.execute("SELECT d.DocumentID,d.Title,d.Author,d.PublishDate FROM Favorites f INNER JOIN Documents d ON f.DocumentID=d.DocumentID WHERE f.UserID=%s ORDER BY f.CreateTime DESC LIMIT %s OFFSET %s", (request.user_id, pp, offset))
    docs = [{'id': r.DocumentID, 'title': r.Title, 'author': r.Author,
             'publish_date': str(r.PublishDate) if r.PublishDate else ''} for r in cur.fetchall()]
    return jsonify({'code': 200, 'message': 'ok', 'data': {'documents': docs, 'total_count': total, 'page': page, 'total_pages': pages}})


@fav_bp.route('/api/toggle_favorite', methods=['POST'])
@login_required
def toggle():
    d = request.get_json() or {}
    did = d.get('document_id')
    if not did:
        return jsonify({'code': 400, 'message': '参数错误', 'data': None})

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DocumentID FROM Documents WHERE DocumentID=%s", (did,))
    if not cur.fetchone():
        return jsonify({'code': 404, 'message': '该文献不存在', 'data': None})

    cur.execute("SELECT FavoriteID FROM Favorites WHERE UserID=%s AND DocumentID=%s", (request.user_id, did))
    ex = cur.fetchone()
    if ex:
        cur.execute("DELETE FROM Favorites WHERE FavoriteID=%s", (ex[0],))
        fav = False
    else:
        cur.execute("INSERT INTO Favorites(UserID,DocumentID) VALUES(%s,%s)", (request.user_id, did))
        fav = True
    conn.commit()
    return jsonify({'code': 200, 'message': '已收藏' if fav else '已取消收藏', 'data': {'is_favorited': fav}})
