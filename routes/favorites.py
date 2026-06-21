# ============================================================
# routes/favorites.py —— 收藏功能模块
# ============================================================

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    jsonify
)
from db import get_connection
from utils import get_pagination   # 导入分页工具

favorites_bp = Blueprint('favorites', __name__)


@favorites_bp.route('/favorites')
def favorites():
    if 'user_id' not in session:
        return redirect('/login')

    per_page = 10
    user_id = session['user_id']

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Favorites WHERE UserID = ?", (user_id,))
    total_count = cursor.fetchone()[0]

    page_param = request.args.get('page')
    page, offset, total_pages = get_pagination(page_param, total_count, per_page)

    cursor.execute("""
        SELECT d.DocumentID, d.Title, d.Author, d.PublishDate
        FROM Favorites f
        INNER JOIN Documents d ON f.DocumentID = d.DocumentID
        WHERE f.UserID = ?
        ORDER BY f.CreateTime DESC
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """, (user_id, offset, per_page))
    documents = cursor.fetchall()

    return render_template(
        'favorites.html',
        documents=documents,
        total_count=total_count,
        page=page,
        total_pages=total_pages
    )


@favorites_bp.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': '未登录'})

    data = request.get_json()
    doc_id = data.get('document_id')
    user_id = session['user_id']

    if not doc_id:
        return jsonify({'success': False, 'error': '参数错误'})

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DocumentID FROM Documents WHERE DocumentID = ?", (doc_id,))
    if not cursor.fetchone():
        return jsonify({'success': False, 'error': '该文献不存在或已被删除'})

    cursor.execute("""
        SELECT FavoriteID FROM Favorites
        WHERE UserID = ? AND DocumentID = ?
    """, (user_id, doc_id))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("DELETE FROM Favorites WHERE FavoriteID = ?", (existing[0],))
        is_favorited = False
    else:
        cursor.execute("INSERT INTO Favorites (UserID, DocumentID) VALUES (?, ?)", (user_id, doc_id))
        is_favorited = True

    conn.commit()

    return jsonify({'success': True, 'is_favorited': is_favorited})