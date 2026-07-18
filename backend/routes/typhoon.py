"""台风分析模块 Blueprint —— 气象学术科研平台 v4.1"""
import json
from flask import Blueprint, request, jsonify

from db import get_connection
from utils import get_pagination, login_required
from config import Config

typhoon_bp = Blueprint('typhoon', __name__)

# ═══════════════════════════════════════════════════════════
# 1. 台风列表查询
# ═══════════════════════════════════════════════════════════

@typhoon_bp.route('/api/typhoon/list')
@login_required
def typhoon_list():
    """台风列表：支持按年份、名称搜索、强度筛选、分页"""
    year = request.args.get('year', '').strip()
    keyword = request.args.get('keyword', '').strip()
    min_wind = request.args.get('min_wind', '').strip()
    page_size = 20

    conn = get_connection()
    cur = conn.cursor()

    # 获取可用年份
    cur.execute("SELECT DISTINCT Season FROM TyphoonInfo ORDER BY Season DESC")
    available_years = [r[0] for r in cur.fetchall()]

    conds, params = [], []

    if year:
        conds.append("Season = %s")
        params.append(int(year))
    if keyword:
        conds.append("TyphoonName LIKE %s")
        params.append('%' + keyword + '%')
    if min_wind:
        conds.append("MaxWind >= %s")
        params.append(float(min_wind))

    wc = ("WHERE " + " AND ".join(conds)) if conds else ""

    try:
        cnt_sql = f"SELECT COUNT(*) FROM TyphoonInfo {wc}"
        cur.execute(cnt_sql, params)
        total = cur.fetchone()[0]
        page, offset, total_pages = get_pagination(request.args.get('page'), total, page_size)

        sel_sql = f"""
            SELECT TyphoonID, TyphoonName, Season, Basin, MaxWind, MinPressure,
                   TotalPoints, StartTime, EndTime
            FROM TyphoonInfo {wc}
            ORDER BY MaxWind DESC, Season DESC
            LIMIT %s OFFSET %s
        """
        cur.execute(sel_sql, params + [page_size, offset])
        rows = cur.fetchall()
    except Exception as e:
        return jsonify({'code': 500, 'message': f'查询失败：{str(e)}', 'data': None})

    typhoons = [{
        'typhoon_id': r.TyphoonID,
        'typhoon_name': r.TyphoonName,
        'season': r.Season,
        'basin': r.Basin,
        'max_wind': r.MaxWind,
        'min_pressure': r.MinPressure,
        'total_points': r.TotalPoints,
        'start_time': r.StartTime.strftime('%Y-%m-%d %H:%M') if r.StartTime else '',
        'end_time': r.EndTime.strftime('%Y-%m-%d %H:%M') if r.EndTime else '',
    } for r in rows]

    return jsonify({'code': 200, 'message': '查询成功', 'data': {
        'typhoons': typhoons,
        'total_count': total,
        'page': page,
        'total_pages': total_pages,
        'available_years': available_years,
    }})


# ═══════════════════════════════════════════════════════════
# 2. 单个台风详情
# ═══════════════════════════════════════════════════════════

@typhoon_bp.route('/api/typhoon/<typhoon_id>')
@login_required
def typhoon_detail(typhoon_id):
    """获取单个台风的基本信息"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT TyphoonID, TyphoonName, Season, Basin, MaxWind, MinPressure,
               TotalPoints, StartTime, EndTime
        FROM TyphoonInfo WHERE TyphoonID = %s
    """, (typhoon_id,))
    row = cur.fetchone()

    if not row:
        return jsonify({'code': 404, 'message': '台风不存在', 'data': None})

    info = {
        'typhoon_id': row.TyphoonID,
        'typhoon_name': row.TyphoonName,
        'season': row.Season,
        'basin': row.Basin,
        'max_wind': row.MaxWind,
        'min_pressure': row.MinPressure,
        'total_points': row.TotalPoints,
        'start_time': row.StartTime.strftime('%Y-%m-%d %H:%M') if row.StartTime else '',
        'end_time': row.EndTime.strftime('%Y-%m-%d %H:%M') if row.EndTime else '',
    }

    return jsonify({'code': 200, 'message': '查询成功', 'data': info})


# ═══════════════════════════════════════════════════════════
# 3. 台风路径点数据
# ═══════════════════════════════════════════════════════════

@typhoon_bp.route('/api/typhoon/<typhoon_id>/track')
@login_required
def typhoon_track(typhoon_id):
    """获取某个台风的所有路径点（按时间排序）"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT TrackID, TyphoonID, DateTime, Latitude, Longitude,
               MaxSustainedWind, MinPressure, StormCategory,
               WindRadius7NE, WindRadius7SE, WindRadius7SW, WindRadius7NW,
               WindRadius10NE, WindRadius10SE, WindRadius10SW, WindRadius10NW
        FROM TyphoonTrack
        WHERE TyphoonID = %s
        ORDER BY DateTime ASC
    """, (typhoon_id,))
    rows = cur.fetchall()

    if not rows:
        return jsonify({'code': 404, 'message': '该台风无路径数据', 'data': None})

    points = [{
        'track_id': r.TrackID,
        'datetime': r.DateTime.strftime('%Y-%m-%d %H:%M:%S') if r.DateTime else '',
        'latitude': r.Latitude,
        'longitude': r.Longitude,
        'max_wind': r.MaxSustainedWind,
        'min_pressure': r.MinPressure,
        'storm_category': r.StormCategory,
        'wind_radius_7': {
            'ne': r.WindRadius7NE,
            'se': r.WindRadius7SE,
            'sw': r.WindRadius7SW,
            'nw': r.WindRadius7NW,
        },
        'wind_radius_10': {
            'ne': r.WindRadius10NE,
            'se': r.WindRadius10SE,
            'sw': r.WindRadius10SW,
            'nw': r.WindRadius10NW,
        },
    } for r in rows]

    return jsonify({'code': 200, 'message': '查询成功', 'data': {'points': points}})


# ═══════════════════════════════════════════════════════════
# 4. 年度台风统计
# ═══════════════════════════════════════════════════════════

@typhoon_bp.route('/api/typhoon/stats/yearly')
@login_required
def yearly_stats():
    """年度台风统计：每年台风数量、平均强度等"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT Season,
               COUNT(*) AS total_count,
               ROUND(AVG(MaxWind), 1) AS avg_wind,
               MAX(MaxWind) AS max_wind,
               ROUND(AVG(MinPressure), 1) AS avg_pressure,
               MIN(MinPressure) AS min_pressure
        FROM TyphoonInfo
        GROUP BY Season
        ORDER BY Season DESC
        LIMIT 50
    """)
    rows = cur.fetchall()

    stats = [{
        'season': r.Season,
        'total_count': r.total_count,
        'avg_wind': r.avg_wind,
        'max_wind': r.max_wind,
        'avg_pressure': r.avg_pressure,
        'min_pressure': r.min_pressure,
    } for r in rows]

    return jsonify({'code': 200, 'message': '查询成功', 'data': {'yearly_stats': stats}})


# ═══════════════════════════════════════════════════════════
# 5. AI 分析接口（DeepSeek）
# ═══════════════════════════════════════════════════════════

@typhoon_bp.route('/api/typhoon/ai_analysis', methods=['POST'])
@login_required
def ai_analysis():
    """
    使用 DeepSeek API 进行台风 AI 分析（结果缓存到数据库）
    body: {
        "typhoon_id": "1984001N11141",
        "analysis_type": "trend" | "compare" | "impact" | "travel"
    }
    """
    data = request.get_json(silent=True) or {}
    typhoon_id = data.get('typhoon_id', '').strip()
    analysis_type = data.get('analysis_type', 'trend').strip()

    if not typhoon_id:
        return jsonify({'code': 400, 'message': '缺少 typhoon_id', 'data': None})

    conn = get_connection()
    cur = conn.cursor()

    # 先查缓存
    cur.execute("""
        SELECT Content FROM TyphoonAIAnalysis
        WHERE TyphoonID = %s AND AnalysisType = %s
    """, (typhoon_id, analysis_type))
    cached = cur.fetchone()
    if cached:
        return jsonify({'code': 200, 'message': 'AI 分析完成（缓存）', 'data': {
            'analysis_type': analysis_type,
            'typhoon_name': '',
            'content': cached.Content,
            'cached': True,
        }})

    # 获取台风基本信息
    cur.execute("""
        SELECT TyphoonID, TyphoonName, Season, MaxWind, MinPressure,
               TotalPoints, StartTime, EndTime
        FROM TyphoonInfo WHERE TyphoonID = %s
    """, (typhoon_id,))
    info = cur.fetchone()
    if not info:
        return jsonify({'code': 404, 'message': '台风不存在', 'data': None})

    # 分析类型对应的 system prompt
    system_prompts = {
        'trend': '你是气象学家。请用100-150字的中文回复，简洁专业地分析台风。',
        'compare': '你是台风气候学家。请用100-150字的中文回复，简洁专业地分析台风。',
        'impact': '你是气象灾害评估专家。请用100-150字的中文回复，简洁专业地分析台风。',
        'travel': '你是气象安全顾问。请用100-150字的中文回复，简洁专业地给出建议。',
    }

    analysis_prompts = {
        'trend': f"""台风：{info.TyphoonName}（{info.Season}年），最大风速{info.MaxWind}kts，最低气压{info.MinPressure}hPa。
请用100-150字中文分析该台风：1)路径总体走向与关键拐点 2)强度演变的各阶段特征 3)影响其路径和强度的气象因素 4)此类台风的典型特征。""",

        'compare': f"""台风：{info.TyphoonName}（{info.Season}年），最大风速{info.MaxWind}kts，最低气压{info.MinPressure}hPa。
请用100-150字中文分析：该台风在路径形态、强度演变方面与历史上相似台风的异同对比，以及由此得出的启示。""",

        'impact': f"""台风：{info.TyphoonName}（{info.Season}年），最大风速{info.MaxWind}kts，最低气压{info.MinPressure}hPa。
请用100-150字中文评估：1)可能受影响的沿海地区及影响程度 2)基于风圈范围的影响区域判断 3)潜在的降水、风暴潮等次生灾害风险。""",

        'travel': f"""台风：{info.TyphoonName}（{info.Season}年），最大风速{info.MaxWind}kts，最低气压{info.MinPressure}hPa。
请用100-150字中文给出：1)受影响沿海城市风险等级划分 2)各等级城市的出行安全建议 3)台风期间及过后的安全注意事项。""",
    }

    system_prompt = system_prompts.get(analysis_type, system_prompts['trend'])
    user_prompt = analysis_prompts.get(analysis_type, analysis_prompts['trend'])

    # 调用 DeepSeek API
    api_key = Config.DEEPSEEK_API_KEY
    if not api_key:
        return jsonify({
            'code': 500,
            'message': 'DeepSeek API Key 未配置，请在环境变量 DEEPSEEK_API_KEY 中设置',
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

        # 写入缓存
        cur.execute("""
            INSERT INTO TyphoonAIAnalysis (TyphoonID, AnalysisType, Content)
            VALUES (%s, %s, %s)
        """, (typhoon_id, analysis_type, ai_text))
        conn.commit()

        return jsonify({'code': 200, 'message': 'AI 分析完成', 'data': {
            'analysis_type': analysis_type,
            'typhoon_name': info.TyphoonName,
            'content': ai_text,
            'cached': False,
        }})

    except requests.exceptions.Timeout:
        return jsonify({'code': 500, 'message': 'AI 服务请求超时，请稍后重试', 'data': None})
    except requests.exceptions.RequestException as e:
        return jsonify({'code': 500, 'message': f'AI 服务请求失败：{str(e)}', 'data': None})
    except Exception as e:
        return jsonify({'code': 500, 'message': f'AI 分析异常：{str(e)}', 'data': None})
