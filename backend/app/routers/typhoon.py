"""
台风分析路由 —— 列表 / 详情 / 路径点 / 年度统计 / AI 分析
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.security import get_current_user
from app.services import call_deepseek

router = APIRouter(prefix="/api/typhoon", tags=["typhoon"])


# ── 列表 ──────────────────────────────────────────────
@router.get("/list")
def typhoon_list(
    year: str = Query(default=""),
    keyword: str = Query(default=""),
    min_wind: str = Query(default=""),
    page: int = Query(default=1),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pp = 20

    years_rows = db.execute(text("SELECT DISTINCT season FROM typhoon_info ORDER BY season DESC")).fetchall()
    available_years = [r[0] for r in years_rows]

    conds = []
    params = {}
    if year:
        try:
            conds.append("season = :yr")
            params["yr"] = int(year)
        except ValueError:
            return {"code": 400, "message": "年份参数无效", "data": None}
    if keyword:
        conds.append("typhoon_name ILIKE :kw")
        params["kw"] = f"%{keyword}%"
    if min_wind:
        try:
            conds.append("max_wind >= :mw")
            params["mw"] = float(min_wind)
        except ValueError:
            return {"code": 400, "message": "最低风速参数无效", "data": None}

    where = ("WHERE " + " AND ".join(conds)) if conds else ""
    total = db.execute(text(f"SELECT COUNT(*) FROM typhoon_info {where}"), params).scalar()
    tp = max(1, (total + pp - 1) // pp)
    page = max(1, min(page, tp))
    off = (page - 1) * pp

    rows = db.execute(text(
        f"SELECT typhoon_id, typhoon_name, season, basin, max_wind, min_pressure, total_points, start_time, end_time "
        f"FROM typhoon_info {where} ORDER BY max_wind DESC, season DESC LIMIT :lim OFFSET :off"
    ), {**params, "lim": pp, "off": off}).fetchall()

    typhoons = [
        {
            "typhoon_id": r.typhoon_id, "typhoon_name": r.typhoon_name,
            "season": r.season, "basin": r.basin, "max_wind": r.max_wind,
            "min_pressure": r.min_pressure, "total_points": r.total_points,
            "start_time": r.start_time.strftime("%Y-%m-%d %H:%M") if r.start_time else "",
            "end_time": r.end_time.strftime("%Y-%m-%d %H:%M") if r.end_time else "",
        }
        for r in rows
    ]
    return {"code": 200, "message": "查询成功", "data": {"typhoons": typhoons, "total_count": total, "page": page, "total_pages": tp, "available_years": available_years}}


# ── 详情 ──────────────────────────────────────────────
@router.get("/{typhoon_id}")
def typhoon_detail(typhoon_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    r = db.execute(text(
        "SELECT typhoon_id, typhoon_name, season, basin, max_wind, min_pressure, total_points, start_time, end_time, "
        "ST_X(ST_Centroid(track_geom)) AS lon, ST_Y(ST_Centroid(track_geom)) AS lat "
        "FROM typhoon_info WHERE typhoon_id = :tid"
    ), {"tid": typhoon_id}).fetchone()
    if not r:
        raise HTTPException(status_code=404, detail="台风不存在")

    # PostGIS 空间密度分析：500km 范围内统计（使用 geography 类型确保真实公里距离）
    spatial_stats = None
    try:
        ss = db.execute(text("""
            SELECT
                COUNT(*) AS nearby_typhoons,
                COALESCE(ROUND(AVG(max_wind), 1), 0) AS nearby_avg_wind,
                MAX(max_wind) AS nearby_max_wind,
                COALESCE(ROUND(AVG(min_pressure), 1), 0) AS nearby_avg_pressure,
                MIN(min_pressure) AS nearby_min_pressure
            FROM typhoon_info
            WHERE typhoon_id != :tid
              AND track_geom IS NOT NULL
              AND ST_DWithin(
                  (SELECT track_geom::geography FROM typhoon_info WHERE typhoon_id = :tid2),
                  track_geom::geography,
                  500000
              )
        """), {"tid": typhoon_id, "tid2": typhoon_id}).fetchone()
        if ss and ss.nearby_typhoons > 0:
            spatial_stats = {
                "radius_km": 500,
                "nearby_count": ss.nearby_typhoons,
                "avg_wind": ss.nearby_avg_wind,
                "max_wind": ss.nearby_max_wind,
                "avg_pressure": ss.nearby_avg_pressure,
                "min_pressure": ss.nearby_min_pressure,
            }
    except Exception:
        pass  # PostGIS 未启用或无数据时静默跳过

    return {"code": 200, "message": "查询成功", "data": {
        "typhoon_id": r.typhoon_id, "typhoon_name": r.typhoon_name,
        "season": r.season, "basin": r.basin, "max_wind": r.max_wind,
        "min_pressure": r.min_pressure, "total_points": r.total_points,
        "start_time": r.start_time.strftime("%Y-%m-%d %H:%M") if r.start_time else "",
        "end_time": r.end_time.strftime("%Y-%m-%d %H:%M") if r.end_time else "",
        "spatial_stats": spatial_stats,
    }}


# ── 路径点 ────────────────────────────────────────────
@router.get("/{typhoon_id}/track")
def typhoon_track(typhoon_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.execute(text(
        "SELECT track_id, typhoon_id, date_time, latitude, longitude, max_sustained_wind, min_pressure, storm_category, "
        "wind_radius7_ne, wind_radius7_se, wind_radius7_sw, wind_radius7_nw, "
        "wind_radius10_ne, wind_radius10_se, wind_radius10_sw, wind_radius10_nw "
        "FROM typhoon_track WHERE typhoon_id = :tid ORDER BY date_time ASC"
    ), {"tid": typhoon_id}).fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="该台风无路径数据")

    points = [
        {
            "track_id": r.track_id,
            "datetime": r.date_time.strftime("%Y-%m-%d %H:%M:%S") if r.date_time else "",
            "latitude": r.latitude, "longitude": r.longitude,
            "max_wind": r.max_sustained_wind, "min_pressure": r.min_pressure,
            "storm_category": r.storm_category,
            "wind_radius_7": {"ne": r.wind_radius7_ne, "se": r.wind_radius7_se, "sw": r.wind_radius7_sw, "nw": r.wind_radius7_nw},
            "wind_radius_10": {"ne": r.wind_radius10_ne, "se": r.wind_radius10_se, "sw": r.wind_radius10_sw, "nw": r.wind_radius10_nw},
        }
        for r in rows
    ]
    return {"code": 200, "message": "查询成功", "data": {"points": points}}


# ── 年度统计 ──────────────────────────────────────────
@router.get("/stats/yearly")
def yearly_stats(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.execute(text(
        "SELECT season, COUNT(*) AS total_count, ROUND(AVG(max_wind), 1) AS avg_wind, "
        "MAX(max_wind) AS max_wind, ROUND(AVG(min_pressure), 1) AS avg_pressure, "
        "MIN(min_pressure) AS min_pressure FROM typhoon_info "
        "GROUP BY season ORDER BY season DESC LIMIT 50"
    )).fetchall()
    stats = [
        {"season": r.season, "total_count": r.total_count, "avg_wind": r.avg_wind,
         "max_wind": r.max_wind, "avg_pressure": r.avg_pressure, "min_pressure": r.min_pressure}
        for r in rows
    ]
    return {"code": 200, "message": "查询成功", "data": {"yearly_stats": stats}}


# ── AI 分析 ───────────────────────────────────────────
@router.post("/ai_analysis")
def ai_analysis(body: dict, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    typhoon_id = body.get("typhoon_id", "").strip()
    analysis_type = body.get("analysis_type", "trend").strip()

    if not typhoon_id:
        raise HTTPException(status_code=400, detail="缺少 typhoon_id")

    # 查缓存
    cached = db.execute(text(
        "SELECT content FROM typhoon_ai_analysis WHERE typhoon_id = :tid AND analysis_type = :at"
    ), {"tid": typhoon_id, "at": analysis_type}).fetchone()
    if cached:
        return {"code": 200, "message": "AI 分析完成（缓存）", "data": {"analysis_type": analysis_type, "typhoon_name": "", "content": cached.content, "cached": True}}

    info = db.execute(text(
        "SELECT typhoon_id, typhoon_name, season, max_wind, min_pressure FROM typhoon_info WHERE typhoon_id = :tid"
    ), {"tid": typhoon_id}).fetchone()
    if not info:
        raise HTTPException(status_code=404, detail="台风不存在")

    prompts = {
        "trend": ("你是气象学家。请用100-150字的中文回复。",
                   f"台风：{info.typhoon_name}（{info.season}年），最大风速{info.max_wind}kts，最低气压{info.min_pressure}hPa。分析路径走向与强度演变特征。"),
        "compare": ("你是台风气候学家。请用100-150字的中文回复。",
                     f"台风：{info.typhoon_name}（{info.season}年），最大风速{info.max_wind}kts，最低气压{info.min_pressure}hPa。对比历史上相似台风的异同。"),
        "impact": ("你是气象灾害评估专家。请用100-150字的中文回复。",
                    f"台风：{info.typhoon_name}（{info.season}年），最大风速{info.max_wind}kts，最低气压{info.min_pressure}hPa。评估潜在影响。"),
        "travel": ("你是气象安全顾问。请用100-150字的中文回复。",
                    f"台风：{info.typhoon_name}（{info.season}年），最大风速{info.max_wind}kts，最低气压{info.min_pressure}hPa。给出出行建议。"),
    }
    sp, up = prompts.get(analysis_type, prompts["trend"])
    ai_text = call_deepseek(sp, up)

    if ai_text is None:
        raise HTTPException(status_code=500, detail="DeepSeek API Key 未配置或调用失败")

    db.execute(text(
        "INSERT INTO typhoon_ai_analysis (typhoon_id, analysis_type, content) VALUES (:tid, :at, :ct)"
    ), {"tid": typhoon_id, "at": analysis_type, "ct": ai_text})
    db.commit()
    return {"code": 200, "message": "AI 分析完成", "data": {"analysis_type": analysis_type, "typhoon_name": info.typhoon_name, "content": ai_text, "cached": False}}
