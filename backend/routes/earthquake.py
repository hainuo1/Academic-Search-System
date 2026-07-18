"""地震分析模块 Blueprint —— 气象科学研究数据平台"""
from flask import Blueprint, request, jsonify

from db import get_connection
from utils import get_pagination, login_required
from config import Config

earthquake_bp = Blueprint('earthquake', __name__)


# ═══════════════════════════════════════════════════
# 1. 地震列表查询
# ═══════════════════════════════════════════════════

@earthquake_bp.route('/api/earthquake/list')
@login_required
def earthquake_list():
    """地震列表：支持按年份、震级、关键词搜索、分页"""
    year = request.args.get('year', '').strip()
    min_mag = request.args.get('min_mag', '').strip()
    keyword = request.args.get('keyword', '').strip()
    page_size = 20

    conn = get_connection()
    cur = conn.cursor()

    # 获取可用年份
    cur.execute("SELECT DISTINCT YEAR(DateTime) AS y FROM EarthquakeInfo ORDER BY y DESC")
    available_years = [r[0] for r in cur.fetchall()]

    conds, params = [], []

    if year:
        conds.append("YEAR(DateTime) = %s")
        params.append(int(year))
    if min_mag:
        conds.append("Magnitude >= %s")
        params.append(float(min_mag))
    if keyword:
        conds.append("Place LIKE %s")
        params.append('%' + keyword + '%')

    wc = ("WHERE " + " AND ".join(conds)) if conds else ""

    try:
        cnt_sql = f"SELECT COUNT(*) FROM EarthquakeInfo {wc}"
        cur.execute(cnt_sql, params)
        total = cur.fetchone()[0]
        page, offset, total_pages = get_pagination(request.args.get('page'), total, page_size)

        sel_sql = f"""
            SELECT EventID, DateTime, Latitude, Longitude, Depth, Magnitude,
                   MagType, Place, Significance
            FROM EarthquakeInfo {wc}
            ORDER BY Magnitude DESC, DateTime DESC
            LIMIT %s OFFSET %s
        """
        cur.execute(sel_sql, params + [page_size, offset])
        rows = cur.fetchall()
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败：{str(e)}', 'data': None})

    quakes = [{
        'event_id':     r.EventID,
        'datetime':     r.DateTime.strftime('%Y-%m-%d %H:%M:%S') if r.DateTime else '',
        'latitude':     r.Latitude,
        'longitude':    r.Longitude,
        'depth':        r.Depth,
        'magnitude':    r.Magnitude,
        'mag_type':     r.MagType,
        'place':        r.Place,
        'significance': r.Significance,
    } for r in rows]

    return jsonify({'code': 200, 'message': '查询成功', 'data': {
        'earthquakes':   quakes,
        'total_count':   total,
        'page':          page,
        'total_pages':   total_pages,
        'available_years': available_years,
    }})


# ═══════════════════════════════════════════════════
# 2. 单条地震详情
# ═══════════════════════════════════════════════════

@earthquake_bp.route('/api/earthquake/<event_id>')
@login_required
def earthquake_detail(event_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT EventID, DateTime, Latitude, Longitude, Depth, Magnitude,
               MagType, Place, Status, Tsunami, Alert, Significance,
               Gap, Dmin, Rms, Nst, HorizontalError, DepthError, MagError, MagNst
        FROM EarthquakeInfo WHERE EventID = %s
    """, (event_id,))
    row = cur.fetchone()
    if not row:
        return jsonify({'code': 404, 'message': '地震事件不存在', 'data': None})

    detail = {
        'event_id':        row.EventID,
        'datetime':        row.DateTime.strftime('%Y-%m-%d %H:%M:%S') if row.DateTime else '',
        'latitude':        row.Latitude,
        'longitude':       row.Longitude,
        'depth':           row.Depth,
        'magnitude':       row.Magnitude,
        'mag_type':        row.MagType,
        'place':           row.Place,
        'status':          row.Status,
        'tsunami':         row.Tsunami,
        'alert':           row.Alert,
        'significance':    row.Significance,
        'gap':             row.Gap,
        'dmin':            row.Dmin,
        'rms':             row.Rms,
        'nst':             row.Nst,
        'horizontal_error': row.HorizontalError,
        'depth_error':     row.DepthError,
        'mag_error':       row.MagError,
        'mag_nst':         row.MagNst,
    }

    # 同区域邻近地震（±3°范围，带回 significance）
    cur.execute("""
        SELECT DateTime, Magnitude, Depth, Place, Significance
        FROM EarthquakeInfo
        WHERE ABS(Latitude - %s) < 3 AND ABS(Longitude - %s) < 3
          AND EventID != %s
        ORDER BY DateTime DESC
        LIMIT 30
    """, (row.Latitude, row.Longitude, event_id))
    nearby = [{
        'datetime':     r.DateTime.strftime('%Y-%m-%d %H:%M:%S') if r.DateTime else '',
        'magnitude':    r.Magnitude,
        'depth':        r.Depth,
        'place':        r.Place,
        'significance': r.Significance,
    } for r in cur.fetchall()]

    return jsonify({'code': 200, 'message': '查询成功', 'data': {
        'detail': detail, 'nearby': nearby,
    }})


# ═══════════════════════════════════════════════════
# 3. 年度地震统计
# ═══════════════════════════════════════════════════

@earthquake_bp.route('/api/earthquake/stats/yearly')
@login_required
def yearly_stats():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT YEAR(DateTime) AS yr,
               COUNT(*) AS total_count,
               ROUND(AVG(Magnitude), 1) AS avg_mag,
               MAX(Magnitude) AS max_mag,
               ROUND(AVG(Depth), 1) AS avg_depth,
               SUM(CASE WHEN Magnitude >= 6.0 THEN 1 ELSE 0 END) AS strong_count,
               SUM(CASE WHEN Magnitude >= 7.0 THEN 1 ELSE 0 END) AS major_count
        FROM EarthquakeInfo
        GROUP BY yr
        ORDER BY yr DESC
        LIMIT 30
    """)
    rows = cur.fetchall()

    stats = [{
        'year':         r.yr,
        'total_count':  r.total_count,
        'avg_mag':      r.avg_mag,
        'max_mag':      r.max_mag,
        'avg_depth':    r.avg_depth,
        'strong_count': r.strong_count,
        'major_count':  r.major_count,
    } for r in rows]

    return jsonify({'code': 200, 'message': '查询成功', 'data': {'yearly_stats': stats}})


# ═══════════════════════════════════════════════════
# 4. AI 分析接口（DeepSeek + 缓存）
# ═══════════════════════════════════════════════════

@earthquake_bp.route('/api/earthquake/ai_analysis', methods=['POST'])
@login_required
def ai_analysis():
    data = request.get_json(silent=True) or {}
    event_id = data.get('event_id', '').strip()
    analysis_type = data.get('analysis_type', 'trend').strip()

    if not event_id:
        return jsonify({'code': 400, 'message': '缺少 event_id', 'data': None})

    conn = get_connection()
    cur = conn.cursor()

    # 先查缓存
    cur.execute("""
        SELECT Content FROM EarthquakeAIAnalysis
        WHERE EventID = %s AND AnalysisType = %s
    """, (event_id, analysis_type))
    cached = cur.fetchone()
    if cached:
        return jsonify({'code': 200, 'message': 'AI 分析完成（缓存）', 'data': {
            'analysis_type': analysis_type,
            'content': cached.Content,
            'cached': True,
        }})

    # 获取地震信息
    cur.execute("""
        SELECT EventID, DateTime, Latitude, Longitude, Depth, Magnitude,
               MagType, Place, Significance
        FROM EarthquakeInfo WHERE EventID = %s
    """, (event_id,))
    eq = cur.fetchone()
    if not eq:
        return jsonify({'code': 404, 'message': '地震事件不存在', 'data': None})

    eq_summary = (
        f"地震：{eq.Place}，发震时间 {eq.DateTime}，震级 M{eq.Magnitude}，"
        f"震源深度 {eq.Depth}km，坐标 ({eq.Latitude}°N, {eq.Longitude}°E)，"
        f"显著性 {eq.Significance}"
    )

    system_prompts = {
        'trend': '你是地震学家。请用100-150字的中文回复，简洁专业地分析地震。',
        'risk': '你是地震灾害评估专家。请用100-150字的中文回复，简洁专业地分析地震风险。',
        'impact': '你是应急救援管理专家。请用100-150字的中文回复，简洁专业地评估地震影响。',
    }

    analysis_prompts = {
        'trend': f"""{eq_summary}。
请用100-150字中文分析：1)该区域地震活动趋势 2)该震级在这一地区的地质构造背景下属于什么水平 3)历史类似地震的对比。""",

        'risk': f"""{eq_summary}。
请用100-150字中文评估：1)该震级可能造成的破坏程度 2)震中附近主要城市及人口密集区的风险 3)需要警惕的次生灾害类型。""",

        'impact': f"""{eq_summary}。
请用100-150字中文给出：1)震中周边可能受影响的区域范围 2)应急响应的优先级建议 3)震区群众应注意的安全事项。""",
    }

    system_prompt = system_prompts.get(analysis_type, system_prompts['trend'])
    user_prompt = analysis_prompts.get(analysis_type, analysis_prompts['trend'])

    api_key = Config.DEEPSEEK_API_KEY
    if not api_key:
        return jsonify({
            'code': 500,
            'message': 'DeepSeek API Key 未配置',
            'data': None,
        })

    try:
        import requests

        resp = requests.post(
            f"{Config.DEEPSEEK_API_BASE}/chat/completions",
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': Config.DEEPSEEK_MODEL,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ],
                'temperature': 0.3,
                'max_tokens': 350,
            },
            timeout=60,
        )
        resp.raise_for_status()
        result = resp.json()
        ai_text = result['choices'][0]['message']['content']

        cur.execute("""
            INSERT INTO EarthquakeAIAnalysis (EventID, AnalysisType, Content)
            VALUES (%s, %s, %s)
        """, (event_id, analysis_type, ai_text))
        conn.commit()

        return jsonify({'code': 200, 'message': 'AI 分析完成', 'data': {
            'analysis_type': analysis_type,
            'content': ai_text,
            'cached': False,
        }})

    except requests.exceptions.Timeout:
        return jsonify({'code': 500, 'message': 'AI 服务请求超时', 'data': None})
    except requests.exceptions.RequestException as e:
        return jsonify({'code': 500, 'message': f'AI 服务请求失败：{str(e)}', 'data': None})
    except Exception as e:
        return jsonify({'code': 500, 'message': f'AI 分析异常：{str(e)}', 'data': None})
