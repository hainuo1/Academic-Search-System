# ============================================================
# routes/search.py —— 搜索与检索历史模块
# ============================================================

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash,
    url_for
)
from db import get_connection
from utils import get_pagination   # 导入分页工具

search_bp = Blueprint('search', __name__)


# ============================================================
# 文献检索
# ============================================================
@search_bp.route('/search')
def search():
    if 'user_id' not in session:
        return redirect('/login')

    # ---------- 获取参数 ----------
    keyword = request.args.get('keyword', '').strip()
    search_type = request.args.get('search_type', 'title').strip()
    category_browse = request.args.get('category', '').strip()

    title_filter = request.args.get('title', '').strip()
    author_filter = request.args.get('author', '').strip()
    category_filter = request.args.get('category_filter', '').strip()
    keyword_filter = request.args.get('keyword_filter', '').strip()
    fulltext_filter = request.args.get('fulltext_filter', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    page_size = 10

    # ---------- 1. 获取所有分类 ----------
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT Category 
        FROM Documents 
        WHERE Category IS NOT NULL AND Category != ''
        ORDER BY Category
    """)
    all_categories = [row[0] for row in cursor.fetchall()]

    # ---------- 2. 构建筛选条件 ----------
    conditions = []
    params = []

    effective_category = category_browse or category_filter
    if effective_category:
        conditions.append("Category = ?")
        params.append(effective_category)

    if title_filter:
        conditions.append("Title LIKE ?")
        params.append('%' + title_filter + '%')

    if author_filter:
        conditions.append("Author LIKE ?")
        params.append('%' + author_filter + '%')

    if fulltext_filter:
        conditions.append("FullText LIKE ?")
        params.append('%' + fulltext_filter + '%')

    if start_date:
        conditions.append("PublishDate >= ?")
        params.append(start_date)

    if end_date:
        conditions.append("PublishDate <= ?")
        params.append(end_date)

    # ---------- 3. 关键词相关条件 ----------
    keyword_join = ""
    keyword_condition = ""
    keyword_params = []

    if keyword:
        if search_type == 'keyword':
            keyword_join = """
                INNER JOIN DocumentKeyword dk ON d.DocumentID = dk.DocumentID
                INNER JOIN Keywords k ON dk.KeywordID = k.KeywordID
            """
            keyword_condition = "k.KeywordName LIKE ?"
            keyword_params = ['%' + keyword + '%']
        elif search_type == 'title':
            keyword_condition = "d.Title LIKE ?"
            keyword_params = ['%' + keyword + '%']
        elif search_type == 'author':
            keyword_condition = "d.Author LIKE ?"
            keyword_params = ['%' + keyword + '%']
        elif search_type == 'category':
            keyword_condition = "d.Category LIKE ?"
            keyword_params = ['%' + keyword + '%']
        elif search_type == 'fulltext':
            keyword_condition = "d.FullText LIKE ?"
            keyword_params = ['%' + keyword + '%']
        else:
            keyword_condition = "d.Title LIKE ?"
            keyword_params = ['%' + keyword + '%']

    # ---------- 4. 组合 SQL ----------
    from_clause = "FROM Documents d"
    if keyword_join:
        from_clause += " " + keyword_join

    where_parts = []
    all_params = []

    if keyword_condition:
        where_parts.append(keyword_condition)
        all_params.extend(keyword_params)

    if conditions:
        where_parts.extend(conditions)
        all_params.extend(params)

    where_clause = ""
    if where_parts:
        where_clause = "WHERE " + " AND ".join(where_parts)

    count_sql = f"SELECT COUNT(*) {from_clause} {where_clause}"
    select_sql = f"""
        SELECT d.DocumentID, d.Title, d.Author, d.PublishDate, d.Category, d.Abstract
        {from_clause}
        {where_clause}
        ORDER BY d.DocumentID DESC
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """

    # ---------- 5. 执行查询 ----------
    try:
        if keyword:
            cursor.execute("""
                INSERT INTO SearchHistory (UserID, SearchKeyword, SearchTime)
                VALUES (?, ?, GETDATE())
            """, (session['user_id'], keyword))

            cursor.execute("""
                DELETE FROM SearchHistory
                WHERE UserID = ?
                AND HistoryID NOT IN (
                    SELECT TOP 100 HistoryID
                    FROM SearchHistory
                    WHERE UserID = ?
                    ORDER BY SearchTime DESC
                )
            """, (session['user_id'], session['user_id']))

            cursor.execute("""
                MERGE INTO UserSearchCount AS target
                USING (SELECT ? AS UserID) AS source
                ON target.UserID = source.UserID
                WHEN MATCHED THEN
                    UPDATE SET SearchCount = SearchCount + 1
                WHEN NOT MATCHED THEN
                    INSERT (UserID, SearchCount) VALUES (source.UserID, 1);
            """, (session['user_id'],))

            cursor.execute("""
                MERGE INTO KeywordSearchCount AS target
                USING (SELECT ? AS Keyword) AS source
                ON target.Keyword = source.Keyword
                WHEN MATCHED THEN
                    UPDATE SET SearchCount = SearchCount + 1
                WHEN NOT MATCHED THEN
                    INSERT (Keyword, SearchCount) VALUES (source.Keyword, 1);
            """, (keyword,))

        # 计数
        cursor.execute(count_sql, all_params)
        total_count = cursor.fetchone()[0]

        # 分页
        page_param = request.args.get('page')
        page, offset, total_pages = get_pagination(page_param, total_count, page_size)

        # 查询数据
        query_params = all_params + [offset, page_size]
        cursor.execute(select_sql, query_params)
        results = cursor.fetchall()

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    return render_template(
        'search.html',
        results=results,
        keyword=keyword,
        search_type=search_type,
        title_filter=title_filter,
        author_filter=author_filter,
        category_filter=category_filter,
        keyword_filter=keyword_filter,
        fulltext_filter=fulltext_filter,
        start_date=start_date,
        end_date=end_date,
        page=page,
        total_pages=total_pages,
        total_count=total_count,
        all_categories=all_categories,
        active_category=effective_category
    )


# ============================================================
# 检索历史 + 浏览历史
# ============================================================
@search_bp.route('/history')
def history():
    if 'user_id' not in session:
        return redirect('/login')

    per_page = 15
    page_param = request.args.get('page')
    conn = get_connection()
    cursor = conn.cursor()

    # ---------- 1. 检索历史 ----------
    cursor.execute("SELECT COUNT(*) FROM SearchHistory WHERE UserID = ?", (session['user_id'],))
    search_total = cursor.fetchone()[0]
    page, offset, search_pages = get_pagination(page_param, search_total, per_page)

    cursor.execute("""
        SELECT SearchKeyword, SearchTime
        FROM SearchHistory
        WHERE UserID = ?
        ORDER BY SearchTime DESC
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """, (session['user_id'], offset, per_page))
    search_raw = cursor.fetchall()

    search_histories = []
    for keyword, dt in search_raw:
        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S') if dt else ''
        search_histories.append((keyword, formatted_time))

    # ---------- 2. 浏览历史 ----------
    cursor.execute("SELECT COUNT(*) FROM BrowseHistory WHERE UserID = ?", (session['user_id'],))
    browse_total = cursor.fetchone()[0]
    _, _, browse_pages = get_pagination(page_param, browse_total, per_page)  # 复用同一页码

    cursor.execute("""
        SELECT b.DocumentID, b.ViewTime, d.Title, d.Author
        FROM BrowseHistory b
        INNER JOIN Documents d ON b.DocumentID = d.DocumentID
        WHERE b.UserID = ?
        ORDER BY b.ViewTime DESC
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """, (session['user_id'], offset, per_page))
    browse_raw = cursor.fetchall()

    browse_histories = []
    for doc_id, dt, title, author in browse_raw:
        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S') if dt else ''
        browse_histories.append({
            'DocumentID': doc_id,
            'ViewTime': formatted_time,
            'Title': title,
            'Author': author
        })

    return render_template(
        'history.html',
        search_histories=search_histories,
        browse_histories=browse_histories,
        search_total=search_total,
        browse_total=browse_total,
        search_pages=search_pages,
        browse_pages=browse_pages,
        page=page,
        per_page=per_page
    )


# ============================================================
# 清空所有检索历史
# ============================================================
@search_bp.route('/clear_history', methods=['POST'])
def clear_history():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM SearchHistory WHERE UserID = ?", (session['user_id'],))
    conn.commit()

    flash('所有检索历史已清空', 'success')
    return redirect(url_for('search.history'))


# ============================================================
# 清空所有浏览历史
# ============================================================
@search_bp.route('/clear_browse_history', methods=['POST'])
def clear_browse_history():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM BrowseHistory WHERE UserID = ?", (session['user_id'],))
    conn.commit()

    flash('所有浏览历史已清空', 'success')
    return redirect(url_for('search.history'))