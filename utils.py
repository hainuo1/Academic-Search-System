# ============================================================
# utils.py —— 公共工具函数
# ============================================================

def process_keywords(cursor, doc_id, keywords_list):
    """
    处理文献关键词：插入或复用 Keywords 表，并建立 DocumentKeyword 关联。

    参数:
        cursor: 数据库游标（已在外部事务中）
        doc_id: 文献ID
        keywords_list: 关键词列表（已分割、去空）

    返回:
        None（直接在游标上执行插入，由外部统一提交/回滚）
    """
    for keyword in keywords_list:
        # 查询关键词是否存在
        cursor.execute("SELECT KeywordID FROM Keywords WHERE KeywordName = ?", (keyword,))
        row = cursor.fetchone()
        if row:
            keyword_id = row[0]
        else:
            # 不存在则插入
            cursor.execute("INSERT INTO Keywords (KeywordName) VALUES (?)", (keyword,))
            cursor.execute("SELECT SCOPE_IDENTITY()")
            keyword_id = int(cursor.fetchone()[0])

        # 关联文献与关键词
        cursor.execute("""
            INSERT INTO DocumentKeyword (DocumentID, KeywordID, TF_IDF)
            VALUES (?, ?, ?)
        """, (doc_id, keyword_id, 1.0))


def get_pagination(page_param, total_count, per_page=10):
    """
    计算分页参数，返回 (page, offset, total_pages)

    参数:
        page_param: 原始页码（可能为 None 或非数字）
        total_count: 总记录数
        per_page: 每页记录数（默认10）

    返回:
        (page, offset, total_pages) 均为整数
    """
    try:
        page = int(page_param) if page_param else 1
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1

    total_pages = max(1, (total_count + per_page - 1) // per_page)
    if page > total_pages:
        page = total_pages
    offset = (page - 1) * per_page
    return page, offset, total_pages