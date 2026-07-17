from flask import Blueprint, jsonify
from db import get_connection
from utils import login_required

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/api/stats')
@login_required
def stats():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT Keyword,SearchCount FROM KeywordSearchCount ORDER BY SearchCount DESC LIMIT 10")
    kw = [{'keyword': r[0], 'count': r[1]} for r in cur.fetchall()]

    cur.execute("SELECT u.UserName,usc.SearchCount FROM UserSearchCount usc INNER JOIN Users u ON usc.UserID=u.UserID ORDER BY usc.SearchCount DESC LIMIT 10")
    ur = [{'username': r[0], 'count': r[1]} for r in cur.fetchall()]

    cur.execute("SELECT d.DocumentID,d.Title,COUNT(*) AS cnt FROM Citation c INNER JOIN Documents d ON c.TargetDocumentID=d.DocumentID GROUP BY d.DocumentID,d.Title ORDER BY cnt DESC LIMIT 10")
    cr = [{'id': r[0], 'title': r[1], 'count': r[2]} for r in cur.fetchall()]

    cur.execute("SELECT DocumentID,Title,ViewCount FROM Documents ORDER BY ViewCount DESC LIMIT 10")
    vr = [{'id': r[0], 'title': r[1], 'view_count': r[2]} for r in cur.fetchall()]

    cur.execute("SELECT DocumentID,Title,DownloadCount FROM Documents ORDER BY DownloadCount DESC LIMIT 10")
    dr = [{'id': r[0], 'title': r[1], 'download_count': r[2]} for r in cur.fetchall()]

    cur.execute("SELECT d.DocumentID,d.Title,COUNT(f.FavoriteID) AS cnt FROM Favorites f INNER JOIN Documents d ON f.DocumentID=d.DocumentID GROUP BY d.DocumentID,d.Title ORDER BY cnt DESC LIMIT 10")
    fr = [{'id': r[0], 'title': r[1], 'count': r[2]} for r in cur.fetchall()]

    return jsonify({'code': 200, 'message': 'ok', 'data': {
        'keyword_rank': kw, 'user_rank': ur, 'citation_rank': cr,
        'view_rank': vr, 'download_rank': dr, 'favorite_rank': fr}})
