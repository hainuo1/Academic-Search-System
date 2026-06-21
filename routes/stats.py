# ============================================================
# routes/stats.py —— 数据统计模块
# ============================================================

from flask import Blueprint, render_template, redirect, session
from db import get_connection

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/stats')
def stats():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()

    # 热门关键词排行（TOP 10）
    cursor.execute("""
        SELECT TOP 10 Keyword AS SearchKeyword, SearchCount AS cnt
        FROM KeywordSearchCount
        ORDER BY SearchCount DESC
    """)
    keyword_rank = cursor.fetchall()

    # 活跃用户排行（TOP 10）
    cursor.execute("""
        SELECT TOP 10 u.UserName, usc.SearchCount AS cnt
        FROM UserSearchCount usc
        INNER JOIN Users u ON usc.UserID = u.UserID
        ORDER BY usc.SearchCount DESC
    """)
    user_rank = cursor.fetchall()

    # 高被引文献排行（TOP 10）
    cursor.execute("""
        SELECT TOP 10 d.DocumentID, d.Title, COUNT(*) AS cnt
        FROM Citation c
        INNER JOIN Documents d ON c.TargetDocumentID = d.DocumentID
        GROUP BY d.DocumentID, d.Title
        ORDER BY cnt DESC
    """)
    citation_rank = cursor.fetchall()

    # 热门文献（按浏览次数）
    cursor.execute("""
        SELECT TOP 10 DocumentID, Title, ViewCount
        FROM Documents
        ORDER BY ViewCount DESC
    """)
    view_rank = cursor.fetchall()

    # 热门文献（按下载次数）
    cursor.execute("""
        SELECT TOP 10 DocumentID, Title, DownloadCount
        FROM Documents
        ORDER BY DownloadCount DESC
    """)
    download_rank = cursor.fetchall()

    # 热门收藏文献排行
    cursor.execute("""
        SELECT TOP 10 d.DocumentID, d.Title, COUNT(f.FavoriteID) AS cnt
        FROM Favorites f
        INNER JOIN Documents d ON f.DocumentID = d.DocumentID
        GROUP BY d.DocumentID, d.Title
        ORDER BY cnt DESC
    """)
    favorite_rank = cursor.fetchall()

    # 不再手动关闭连接

    return render_template(
        'stats.html',
        keyword_rank=keyword_rank,
        user_rank=user_rank,
        citation_rank=citation_rank,
        view_rank=view_rank,
        download_rank=download_rank,
        favorite_rank=favorite_rank
    )