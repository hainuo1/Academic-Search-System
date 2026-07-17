from flask import Blueprint, request, jsonify

from db import get_connection
from utils import get_pagination, login_required

search_bp = Blueprint('search', __name__)


@search_bp.route('/api/search')
@login_required
def search():
    kw = request.args.get('keyword', '').strip()
    st = request.args.get('search_type', 'title').strip()
    cb = request.args.get('category', '').strip()

    tf = request.args.get('title', '').strip()
    af = request.args.get('author', '').strip()
    cf = request.args.get('category_filter', '').strip()
    kf = request.args.get('keyword_filter', '').strip()
    ff = request.args.get('fulltext_filter', '').strip()
    sd = request.args.get('start_date', '').strip()
    ed = request.args.get('end_date', '').strip()

    page_size = 10
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT Category FROM Documents WHERE Category IS NOT NULL AND Category != '' ORDER BY Category")
    all_cats = [r[0] for r in cur.fetchall()]

    conds, params = [], []
    ec = cb or cf
    if ec:
        conds.append("d.Category=%s"); params.append(ec)
    if tf:
        conds.append("d.Title LIKE %s"); params.append('%' + tf + '%')
    if af:
        conds.append("d.Author LIKE %s"); params.append('%' + af + '%')
    if ff:
        conds.append("d.`FullText` LIKE %s"); params.append('%' + ff + '%')
    if sd:
        conds.append("d.PublishDate>=%s"); params.append(sd)
    if ed:
        conds.append("d.PublishDate<=%s"); params.append(ed)

    kjoin, kcond, kpar, nd = "", "", [], False
    if kw:
        if st == 'keyword':
            kjoin = " INNER JOIN DocumentKeyword dk ON d.DocumentID=dk.DocumentID INNER JOIN Keywords k ON dk.KeywordID=k.KeywordID"
            kcond = "k.KeywordName LIKE %s"; kpar = ['%' + kw + '%']; nd = True
        elif st == 'title':
            kcond = "d.Title LIKE %s"; kpar = ['%' + kw + '%']
        elif st == 'author':
            kcond = "d.Author LIKE %s"; kpar = ['%' + kw + '%']
        elif st == 'category':
            kcond = "d.Category LIKE %s"; kpar = ['%' + kw + '%']
        elif st == 'fulltext':
            kcond = "d.`FullText` LIKE %s"; kpar = ['%' + kw + '%']
        else:
            kcond = "d.Title LIKE %s"; kpar = ['%' + kw + '%']

    if kf:
        kjoin = " INNER JOIN DocumentKeyword dk ON d.DocumentID=dk.DocumentID INNER JOIN Keywords k ON dk.KeywordID=k.KeywordID"
        conds.append("k.KeywordName LIKE %s"); params.append('%' + kf + '%'); nd = True

    fr = "FROM Documents d" + (" " + kjoin if kjoin else "")
    wp, ap = [], []
    if kcond:
        wp.append(kcond); ap.extend(kpar)
    if conds:
        wp.extend(conds); ap.extend(params)
    wc = ("WHERE " + " AND ".join(wp)) if wp else ""

    cnt_expr = "COUNT(DISTINCT d.DocumentID)" if nd else "COUNT(*)"
    cnt_sql = f"SELECT {cnt_expr} {fr} {wc}"

    fields = "d.DocumentID,d.Title,d.Author,d.PublishDate,d.Category,d.Abstract,d.KeywordsText"
    dist = "DISTINCT" if nd else ""
    sel_sql = f"SELECT {dist} {fields} {fr} {wc} ORDER BY d.DocumentID DESC LIMIT %s OFFSET %s"

    try:
        if kw:
            cur.execute("INSERT INTO SearchHistory(UserID,SearchKeyword,SearchTime) VALUES(%s,%s,NOW())", (request.user_id, kw))
            cur.execute("DELETE FROM SearchHistory WHERE UserID=%s AND HistoryID NOT IN (SELECT * FROM (SELECT HistoryID FROM SearchHistory WHERE UserID=%s ORDER BY SearchTime DESC LIMIT 100) t)", (request.user_id, request.user_id))
            cur.execute("INSERT INTO UserSearchCount(UserID,SearchCount) VALUES(%s,1) ON DUPLICATE KEY UPDATE SearchCount=SearchCount+1", (request.user_id,))
            cur.execute("INSERT INTO KeywordSearchCount(Keyword,SearchCount) VALUES(%s,1) ON DUPLICATE KEY UPDATE SearchCount=SearchCount+1", (kw,))

        cur.execute(cnt_sql, ap)
        total = cur.fetchone()[0]
        page, offset, total_pages = get_pagination(request.args.get('page'), total, page_size)
        cur.execute(sel_sql, ap + [page_size, offset])
        rows = cur.fetchall()
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'code': 500, 'message': f'搜索失败：{str(e)}', 'data': None})

    papers = [{'id': r.DocumentID, 'title': r.Title, 'author': r.Author,
               'publish_date': str(r.PublishDate) if r.PublishDate else '',
               'category': r.Category or '', 'abstract': r.Abstract or '',
               'keywords': r.KeywordsText or ''} for r in rows]

    return jsonify({'code': 200, 'message': '查询成功', 'data': {
        'papers': papers, 'total_count': total, 'page': page,
        'total_pages': total_pages, 'all_categories': all_cats}})


# ── 检索历史 + 浏览历史 ──────────────────────────────
@search_bp.route('/api/history')
@login_required
def history():
    pp = 15
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM SearchHistory WHERE UserID=%s", (request.user_id,))
    stotal = cur.fetchone()[0]
    sp, so, sps = get_pagination(request.args.get('search_page'), stotal, pp)
    cur.execute("SELECT SearchKeyword,SearchTime FROM SearchHistory WHERE UserID=%s ORDER BY SearchTime DESC LIMIT %s OFFSET %s", (request.user_id, pp, so))
    sh = [{'keyword': kw, 'time': dt.strftime('%Y-%m-%d %H:%M:%S') if dt else ''} for kw, dt in cur.fetchall()]

    cur.execute("SELECT COUNT(*) FROM BrowseHistory WHERE UserID=%s", (request.user_id,))
    btotal = cur.fetchone()[0]
    bp, bo, bps = get_pagination(request.args.get('browse_page'), btotal, pp)
    cur.execute("SELECT b.DocumentID,b.ViewTime,d.Title,d.Author FROM BrowseHistory b INNER JOIN Documents d ON b.DocumentID=d.DocumentID WHERE b.UserID=%s ORDER BY b.ViewTime DESC LIMIT %s OFFSET %s", (request.user_id, pp, bo))
    bh = [{'document_id': did, 'view_time': dt.strftime('%Y-%m-%d %H:%M:%S') if dt else '', 'title': t, 'author': a}
          for did, dt, t, a in cur.fetchall()]

    return jsonify({'code': 200, 'message': 'ok', 'data': {
        'search_histories': sh, 'browse_histories': bh,
        'search_total': stotal, 'browse_total': btotal,
        'search_pages': sps, 'browse_pages': bps,
        'search_page': sp, 'browse_page': bp}})
