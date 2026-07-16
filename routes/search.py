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
from utils import get_pagination

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
        conditions.append("d.Category = %s")
        params.append(effective_category)

    if title_filter:
        conditions.append("d.Title LIKE %s")
        params.append('%' + title_filter + '%')

    if author_filter:
        conditions.append("d.Author LIKE %s")
        params.append('%' + author_filter + '%')

    if fulltext_filter:
        conditions.append("d.`FullText` LIKE %s")
        params.append('%' + fulltext_filter + '%')

    if start_date:
        conditions.append("d.PublishDate >= %s")
        params.append(start_date)

    if end_date:
        conditions.append("d.PublishDate <= %s")
        params.append(end_date)

    # ---------- 3. 关键词相关条件 ----------
    keyword_join = ""
    keyword_condition = ""
    keyword_params = []
    need_distinct = False  # 是否需要 COUNT(DISTINCT) 和 SELECT DISTINCT

    if keyword:
        if search_type == 'keyword':
            keyword_join = """
                INNER JOIN DocumentKeyword dk ON d.DocumentID = dk.DocumentID
                INNER JOIN Keywords k ON dk.KeywordID = k.KeywordID
            """
            keyword_condition = "k.KeywordName LIKE %s"
            keyword_params = ['%' + keyword + '%']
            need_distinct = True
        elif search_type == 'title':
            keyword_condition = "d.Title LIKE %s"
            keyword_params = ['%' + keyword + '%']
        elif search_type == 'author':
            keyword_condition = "d.Author LIKE %s"
            keyword_params = ['%' + keyword + '%']
        elif search_type == 'category':
            keyword_condition = "d.Category LIKE %s"
            keyword_params = ['%' + keyword + '%']
        elif search_type == 'fulltext':
            keyword_condition = "d.`FullText` LIKE %s"
            keyword_params = ['%' + keyword + '%']
        else:
            keyword_condition = "d.Title LIKE %s"
            keyword_params = ['%' + keyword + '%']

    # Bug #2 修复：keyword_filter 参与筛选（通过 DocumentKeyword + Keywords 表）
    if keyword_filter:
        keyword_join = """
            INNER JOIN DocumentKeyword dk ON d.DocumentID = dk.DocumentID
            INNER JOIN Keywords k ON dk.KeywordID = k.KeywordID
        """
        conditions.append("k.KeywordName LIKE %s")
        params.append('%' + keyword_filter + '%')
        need_distinct = True

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

    # Bug #3 修复：当 JOIN 了关键词表时，使用 COUNT(DISTINCT) 防止重复计数
    count_expr = "COUNT(DISTINCT d.DocumentID)" if need_distinct else "COUNT(*)"
    count_sql = f"SELECT {count_expr} {from_clause} {where_clause}"

    # Bug #3 + #9 修复：使用 SELECT DISTINCT 防止重复行，并加入 KeywordsText 显示关键词
    select_fields = "d.DocumentID, d.Title, d.Author, d.PublishDate, d.Category, d.Abstract, d.KeywordsText"
    distinct_prefix = "DISTINCT" if need_distinct else ""
    select_sql = f"""
        SELECT {distinct_prefix} {select_fields}
        {from_clause}
        {where_clause}
        ORDER BY d.DocumentID DESC
        LIMIT %s OFFSET %s
    """

    # ---------- 5. 执行查询 ----------
    try:
        if keyword:
            cursor.execute("""
                INSERT INTO SearchHistory (UserID, SearchKeyword, SearchTime)
                VALUES (%s, %s, NOW())
            """, (session['user_id'], keyword))

            # 保留最近100条检索历史
            cursor.execute("""
                DELETE FROM SearchHistory
                WHERE UserID = %s
                AND HistoryID NOT IN (
                    SELECT HistoryID FROM (
                        SELECT HistoryID
                        FROM SearchHistory
                        WHERE UserID = %s
                        ORDER BY SearchTime DESC
                        LIMIT 100
                    ) AS tmp
                )
            """, (session['user_id'], session['user_id']))

            cursor.execute("""
                INSERT INTO UserSearchCount (UserID, SearchCount)
                VALUES (%s, 1)
                ON DUPLICATE KEY UPDATE SearchCount = SearchCount + 1
            """, (session['user_id'],))

            cursor.execute("""
                INSERT INTO KeywordSearchCount (Keyword, SearchCount)
                VALUES (%s, 1)
                ON DUPLICATE KEY UPDATE SearchCount = SearchCount + 1
            """, (keyword,))

        # 计数
        cursor.execute(count_sql, all_params)
        total_count = cursor.fetchone()[0]

        # 分页
        page_param = request.args.get('page')
        page, offset, total_pages = get_pagination(page_param, total_count, page_size)

        # 查询数据
        query_params = all_params + [page_size, offset]
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
    # Bug #7 修复：检索历史和浏览历史使用独立的分页参数
    search_page_param = request.args.get('search_page')
    browse_page_param = request.args.get('browse_page')

    conn = get_connection()
    cursor = conn.cursor()

    # ---------- 1. 检索历史 ----------
    cursor.execute("SELECT COUNT(*) FROM SearchHistory WHERE UserID = %s", (session['user_id'],))
    search_total = cursor.fetchone()[0]
    search_page, search_offset, search_pages = get_pagination(search_page_param, search_total, per_page)

    cursor.execute("""
        SELECT SearchKeyword, SearchTime
        FROM SearchHistory
        WHERE UserID = %s
        ORDER BY SearchTime DESC
        LIMIT %s OFFSET %s
    """, (session['user_id'], per_page, search_offset))
    search_raw = cursor.fetchall()

    search_histories = []
    for keyword_val, dt in search_raw:
        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S') if dt else ''
        search_histories.append((keyword_val, formatted_time))

    # ---------- 2. 浏览历史 ----------
    cursor.execute("SELECT COUNT(*) FROM BrowseHistory WHERE UserID = %s", (session['user_id'],))
    browse_total = cursor.fetchone()[0]
    browse_page, browse_offset, browse_pages = get_pagination(browse_page_param, browse_total, per_page)

    cursor.execute("""
        SELECT b.DocumentID, b.ViewTime, d.Title, d.Author
        FROM BrowseHistory b
        INNER JOIN Documents d ON b.DocumentID = d.DocumentID
        WHERE b.UserID = %s
        ORDER BY b.ViewTime DESC
        LIMIT %s OFFSET %s
    """, (session['user_id'], per_page, browse_offset))
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
        search_page=search_page,
        browse_page=browse_page,
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
    cursor.execute("DELETE FROM SearchHistory WHERE UserID = %s", (session['user_id'],))
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
    cursor.execute("DELETE FROM BrowseHistory WHERE UserID = %s", (session['user_id'],))
    conn.commit()

    flash('所有浏览历史已清空', 'success')
    return redirect(url_for('search.history'))
