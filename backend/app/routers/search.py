"""
检索路由 —— 多字段 / 多种检索类型 / 分页 + PostgreSQL 全文检索
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/api", tags=["search"])

PAGE_SIZE = 10


def _build_rank_clause(search_type: str, keyword: str, fulltext_filter: str) -> tuple[str, str, dict]:
    """构建全文检索相关子句，返回 (extra_select, extra_where, params)。
    优先级：tsvector 主搜索 + ILIKE 中文兜底，确保中英文混合检索命中率。
    """
    extra_select = ""
    extra_where = ""
    params = {}

    # 全文检索 filter
    if fulltext_filter:
        extra_where += (
            " AND (d.full_text_tsv @@ plainto_tsquery('simple', :ft_q)"
            " OR d.full_text ILIKE :ft_like)"
        )
        params["ft_q"] = fulltext_filter
        params["ft_like"] = f"%{fulltext_filter}%"

    # 主搜索关键词
    if keyword:
        if search_type == "fulltext":
            # tsvector 主搜索 + ILIKE 中文兜底
            extra_select = (
                ", ts_rank_cd(d.full_text_tsv, plainto_tsquery('simple', :kw_q)) AS rank"
            )
            extra_where += (
                " AND (d.full_text_tsv @@ plainto_tsquery('simple', :kw_q)"
                " OR d.full_text ILIKE :kw_like)"
            )
            params["kw_q"] = keyword
            params["kw_like"] = f"%{keyword}%"
        elif search_type == "keyword":
            extra_where += " AND k.keyword_name ILIKE :kw"
            params["kw"] = f"%{keyword}%"
        elif search_type == "title":
            extra_where += " AND d.title ILIKE :kw"
            params["kw"] = f"%{keyword}%"
        elif search_type == "author":
            extra_where += " AND d.author ILIKE :kw"
            params["kw"] = f"%{keyword}%"
        elif search_type == "category":
            extra_where += " AND d.category ILIKE :kw"
            params["kw"] = f"%{keyword}%"
        else:
            extra_where += " AND d.title ILIKE :kw"
            params["kw"] = f"%{keyword}%"

    return extra_select, extra_where, params


@router.get("/search")
def search(
    keyword: str = Query(default=""),
    search_type: str = Query(default="title"),
    category: str = Query(default=""),
    title: str = Query(default=""),
    author: str = Query(default=""),
    category_filter: str = Query(default=""),
    keyword_filter: str = Query(default=""),
    fulltext_filter: str = Query(default=""),
    start_date: str = Query(default=""),
    end_date: str = Query(default=""),
    page: int = Query(default=1),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 可用分类
    cats_rows = db.execute(text(
        "SELECT DISTINCT category FROM documents WHERE category IS NOT NULL AND category != '' ORDER BY category"
    )).fetchall()
    all_cats = [r[0] for r in cats_rows]

    # 普通筛选条件
    base_where = ""
    base_params = {}

    ec = category or category_filter
    if ec:
        base_where += " AND d.category = :cat"
        base_params["cat"] = ec
    if title:
        base_where += " AND d.title ILIKE :tf"
        base_params["tf"] = f"%{title}%"
    if author:
        base_where += " AND d.author ILIKE :af"
        base_params["af"] = f"%{author}%"
    if start_date:
        base_where += " AND d.publish_date >= :sd"
        base_params["sd"] = start_date
    if end_date:
        base_where += " AND d.publish_date <= :ed"
        base_params["ed"] = end_date

    # 全文检索 / 关键词搜索 条件
    extra_select, extra_where, extra_params = _build_rank_clause(
        search_type, keyword, fulltext_filter
    )

    # keyword_filter 独立走关键词表 JOIN
    kwf_join = ""
    kwf_where = ""
    need_distinct = False
    if keyword_filter:
        kwf_join = (
            " JOIN document_keyword dk ON d.document_id = dk.document_id"
            " JOIN keywords k ON dk.keyword_id = k.keyword_id"
        )
        kwf_where += " AND k.keyword_name ILIKE :kf"
        base_params["kf"] = f"%{keyword_filter}%"
        need_distinct = True

    if search_type == "keyword":
        kwf_join = (
            " JOIN document_keyword dk ON d.document_id = dk.document_id"
            " JOIN keywords k ON dk.keyword_id = k.keyword_id"
        )
        need_distinct = True

    where_clause = " WHERE d.document_id > 0" + base_where + extra_where + kwf_where

    # 合并所有参数
    all_params = {**base_params, **extra_params}

    # COUNT（全文检索 DISTINCT 不计 rank）
    cnt_sql = "SELECT COUNT(DISTINCT d.document_id)" if need_distinct else "SELECT COUNT(*)"
    cnt_sql += f" FROM documents d {kwf_join} {where_clause}"
    total = db.execute(text(cnt_sql), all_params).scalar()

    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(1, min(page, total_pages))
    offset = (page - 1) * PAGE_SIZE

    # SELECT：全文检索时附加 rank 排序
    sel_fields = "d.document_id, d.title, d.author, d.publish_date, d.category, d.abstract, d.keywords_text"
    order_by = "ORDER BY d.document_id DESC"
    if keyword and search_type == "fulltext":
        sel_fields += extra_select
        order_by = "ORDER BY rank DESC, d.document_id DESC"

    sel_sql = (
        f"SELECT {'DISTINCT' if need_distinct else ''} {sel_fields}"
        f" FROM documents d {kwf_join} {where_clause}"
        f" {order_by} LIMIT :lim OFFSET :off"
    )

    all_params["lim"] = PAGE_SIZE
    all_params["off"] = offset
    rows = db.execute(text(sel_sql), all_params).fetchall()

    # 记录搜索历史
    if keyword:
        try:
            db.execute(text(
                "INSERT INTO search_history(user_id, search_keyword, search_time) VALUES(:uid,:kw,NOW())"
            ), {"uid": current_user["user_id"], "kw": keyword})
            db.execute(text(
                "DELETE FROM search_history WHERE user_id=:uid AND history_id NOT IN "
                "(SELECT history_id FROM search_history WHERE user_id=:uid ORDER BY search_time DESC LIMIT 100)"
            ), {"uid": current_user["user_id"]})
            db.execute(text(
                "INSERT INTO user_search_count(user_id, search_count) VALUES(:uid, 1) "
                "ON CONFLICT (user_id) DO UPDATE SET search_count = user_search_count.search_count + 1"
            ), {"uid": current_user["user_id"]})
            db.execute(text(
                "INSERT INTO keyword_search_count(keyword, search_count) VALUES(:kw, 1) "
                "ON CONFLICT (keyword) DO UPDATE SET search_count = keyword_search_count.search_count + 1"
            ), {"kw": keyword})
            db.commit()
        except Exception:
            db.rollback()

    papers = [
        {
            "id": r.document_id, "title": r.title, "author": r.author,
            "publish_date": str(r.publish_date) if r.publish_date else "",
            "category": r.category or "", "abstract": r.abstract or "",
            "keywords": r.keywords_text or "",
        }
        for r in rows
    ]

    return {
        "code": 200, "message": "查询成功",
        "data": {
            "papers": papers, "total_count": total, "page": page,
            "total_pages": total_pages, "all_categories": all_cats,
        },
    }


# ── 检索历史 + 浏览历史 ──────────────────────────────
@router.get("/history")
def history(
    search_page: int = Query(default=1),
    browse_page: int = Query(default=1),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user["user_id"]
    pp = 15

    stotal = db.execute(text("SELECT COUNT(*) FROM search_history WHERE user_id=:uid"), {"uid": uid}).scalar()
    sp = max(1, min(search_page, max(1, (stotal + pp - 1) // pp)))
    so = (sp - 1) * pp
    s_rows = db.execute(text(
        "SELECT search_keyword, search_time FROM search_history WHERE user_id=:uid ORDER BY search_time DESC LIMIT :lim OFFSET :off"
    ), {"uid": uid, "lim": pp, "off": so}).fetchall()
    sh = [{"keyword": r.search_keyword, "time": r.search_time.strftime("%Y-%m-%d %H:%M:%S") if r.search_time else ""} for r in s_rows]

    btotal = db.execute(text("SELECT COUNT(*) FROM browse_history WHERE user_id=:uid"), {"uid": uid}).scalar()
    bp = max(1, min(browse_page, max(1, (btotal + pp - 1) // pp)))
    bo = (bp - 1) * pp
    b_rows = db.execute(text(
        "SELECT b.document_id, b.view_time, d.title, d.author FROM browse_history b "
        "JOIN documents d ON b.document_id = d.document_id "
        "WHERE b.user_id=:uid ORDER BY b.view_time DESC LIMIT :lim OFFSET :off"
    ), {"uid": uid, "lim": pp, "off": bo}).fetchall()
    bh = [
        {
            "document_id": r.document_id,
            "view_time": r.view_time.strftime("%Y-%m-%d %H:%M:%S") if r.view_time else "",
            "title": r.title, "author": r.author,
        }
        for r in b_rows
    ]

    return {
        "code": 200, "message": "ok",
        "data": {
            "search_histories": sh, "browse_histories": bh,
            "search_total": stotal, "browse_total": btotal,
            "search_pages": max(1, (stotal + pp - 1) // pp),
            "browse_pages": max(1, (btotal + pp - 1) // pp),
            "search_page": sp, "browse_page": bp,
        },
    }
