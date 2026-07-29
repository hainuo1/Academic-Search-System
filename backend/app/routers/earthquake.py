"""
地震分析路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.security import get_current_user
from app.services import call_deepseek

router = APIRouter(prefix="/api/earthquake", tags=["earthquake"])


@router.get("/list")
def earthquake_list(
    year: str = Query(default=""),
    min_mag: str = Query(default=""),
    keyword: str = Query(default=""),
    page: int = Query(default=1),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pp = 20
    conds = []
    params = {}
    if year:
        try:
            conds.append("EXTRACT(YEAR FROM date_time) = :yr")
            params["yr"] = int(year)
        except ValueError:
            return {"code": 400, "message": "年份参数无效", "data": None}
    if min_mag:
        try:
            conds.append("magnitude >= :mm")
            params["mm"] = float(min_mag)
        except ValueError:
            return {"code": 400, "message": "最低震级参数无效", "data": None}
    if keyword:
        conds.append("place ILIKE :kw")
        params["kw"] = f"%{keyword}%"

    where = ("WHERE " + " AND ".join(conds)) if conds else ""
    total = db.execute(text(f"SELECT COUNT(*) FROM earthquake_info {where}"), params).scalar()
    tp = max(1, (total + pp - 1) // pp)
    page = max(1, min(page, tp))
    off = (page - 1) * pp

    rows = db.execute(text(
        f"SELECT event_id, date_time, latitude, longitude, depth, magnitude, mag_type, place, nst, mag_nst "
        f"FROM earthquake_info {where} ORDER BY magnitude DESC, date_time DESC LIMIT :lim OFFSET :off"
    ), {**params, "lim": pp, "off": off}).fetchall()

    quakes = [
        {"event_id": r.event_id, "datetime": r.date_time.strftime("%Y-%m-%d %H:%M:%S") if r.date_time else "",
         "latitude": r.latitude, "longitude": r.longitude, "depth": r.depth, "magnitude": r.magnitude,
         "mag_type": r.mag_type, "place": r.place, "nst": r.nst, "mag_nst": r.mag_nst or 0}
        for r in rows
    ]

    years_rows = db.execute(text("SELECT DISTINCT EXTRACT(YEAR FROM date_time) AS y FROM earthquake_info ORDER BY y DESC")).fetchall()
    return {"code": 200, "message": "查询成功", "data": {
        "earthquakes": quakes, "total_count": total, "page": page, "total_pages": tp,
        "available_years": [int(r.y) for r in years_rows],
    }}


@router.get("/{event_id}")
def earthquake_detail(event_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.execute(text(
        "SELECT event_id, date_time, latitude, longitude, depth, magnitude, mag_type, place, status, tsunami, alert, "
        "gap, dmin, rms, nst, horizontal_error, depth_error, mag_error, mag_nst FROM earthquake_info WHERE event_id = :eid"
    ), {"eid": event_id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="地震事件不存在")

    detail = {
        "event_id": row.event_id, "datetime": row.date_time.strftime("%Y-%m-%d %H:%M:%S") if row.date_time else "",
        "latitude": row.latitude, "longitude": row.longitude, "depth": row.depth, "magnitude": row.magnitude,
        "mag_type": row.mag_type, "place": row.place, "status": row.status, "tsunami": row.tsunami,
        "alert": row.alert,
        "gap": row.gap, "dmin": row.dmin,
        "rms": row.rms, "nst": row.nst or 0, "mag_nst": row.mag_nst or 0,
        "horizontal_error": row.horizontal_error, "depth_error": row.depth_error,
        "mag_error": row.mag_error,
    }

    # 取全部邻近地震，当前事件居中
    nearby_before = db.execute(text(
        "SELECT date_time, magnitude, depth, place, horizontal_error FROM earthquake_info "
        "WHERE ABS(latitude - :lat) < 3 AND ABS(longitude - :lon) < 3 AND event_id != :eid AND date_time <= :dt "
        "ORDER BY date_time DESC"
    ), {"lat": row.latitude, "lon": row.longitude, "eid": event_id, "dt": row.date_time}).fetchall()
    nearby_after = db.execute(text(
        "SELECT date_time, magnitude, depth, place, horizontal_error FROM earthquake_info "
        "WHERE ABS(latitude - :lat) < 3 AND ABS(longitude - :lon) < 3 AND event_id != :eid AND date_time > :dt "
        "ORDER BY date_time ASC"
    ), {"lat": row.latitude, "lon": row.longitude, "eid": event_id, "dt": row.date_time}).fetchall()

    def _to_nearby(r):
        return {"datetime": r.date_time.strftime("%Y-%m-%d %H:%M:%S") if r.date_time else "",
                "magnitude": r.magnitude, "depth": r.depth, "place": r.place,
                "horizontal_error": r.horizontal_error or 0}

    nearby = [_to_nearby(r) for r in reversed(nearby_before)] + [_to_nearby(r) for r in nearby_after]

    # PostGIS 空间密度分析：300km 范围内统计（geography 类型确保真实公里）
    spatial_stats = None
    try:
        ss = db.execute(text("""
            SELECT
                COUNT(*) AS nearby_count,
                COALESCE(ROUND(AVG(magnitude), 1), 0) AS avg_mag,
                MAX(magnitude) AS max_mag,
                COALESCE(ROUND(AVG(depth), 1), 0) AS avg_depth,
                SUM(CASE WHEN magnitude >= 6.0 THEN 1 ELSE 0 END) AS strong_count,
                SUM(CASE WHEN magnitude >= 7.0 THEN 1 ELSE 0 END) AS major_count
            FROM earthquake_info
            WHERE event_id != :eid
              AND ST_DWithin(
                  epicenter::geography,
                  (SELECT epicenter::geography FROM earthquake_info WHERE event_id = :eid2),
                  300000
              )
        """), {"eid": event_id, "eid2": event_id}).fetchone()
        if ss and ss.nearby_count > 0:
            spatial_stats = {
                "radius_km": 300,
                "nearby_count": ss.nearby_count,
                "avg_magnitude": ss.avg_mag,
                "max_magnitude": ss.max_mag,
                "avg_depth": ss.avg_depth,
                "strong_count": ss.strong_count,
                "major_count": ss.major_count,
            }
    except Exception:
        pass  # PostGIS 未启用时静默跳过

    return {"code": 200, "message": "查询成功", "data": {"detail": detail, "nearby": nearby, "spatial_stats": spatial_stats}}


@router.get("/stats/yearly")
def yearly_stats(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.execute(text(
        "SELECT EXTRACT(YEAR FROM date_time) AS yr, COUNT(*) AS total_count, ROUND(AVG(magnitude), 1) AS avg_mag, "
        "MAX(magnitude) AS max_mag, ROUND(AVG(depth), 1) AS avg_depth, "
        "SUM(CASE WHEN magnitude >= 6.0 THEN 1 ELSE 0 END) AS strong_count, "
        "SUM(CASE WHEN magnitude >= 7.0 THEN 1 ELSE 0 END) AS major_count "
        "FROM earthquake_info GROUP BY yr ORDER BY yr DESC LIMIT 30"
    )).fetchall()
    stats = [
        {"year": int(r.yr), "total_count": r.total_count, "avg_mag": r.avg_mag, "max_mag": r.max_mag,
         "avg_depth": r.avg_depth, "strong_count": r.strong_count, "major_count": r.major_count}
        for r in rows
    ]
    return {"code": 200, "message": "查询成功", "data": {"yearly_stats": stats}}


@router.post("/ai_analysis")
def ai_analysis(body: dict, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    event_id = body.get("event_id", "").strip()
    at = body.get("analysis_type", "trend").strip()
    if not event_id:
        raise HTTPException(status_code=400, detail="缺少 event_id")

    cached = db.execute(text(
        "SELECT content FROM earthquake_ai_analysis WHERE event_id = :eid AND analysis_type = :at"
    ), {"eid": event_id, "at": at}).fetchone()
    if cached:
        return {"code": 200, "message": "AI 分析完成（缓存）", "data": {"analysis_type": at, "content": cached.content, "cached": True}}

    eq = db.execute(text(
        "SELECT event_id, date_time, latitude, longitude, depth, magnitude, place FROM earthquake_info WHERE event_id = :eid"
    ), {"eid": event_id}).fetchone()
    if not eq:
        raise HTTPException(status_code=404, detail="地震事件不存在")

    summary = f"地震：{eq.place}，发震时间 {eq.date_time}，震级 M{eq.magnitude}，震源深度 {eq.depth}km，坐标 ({eq.latitude}°N, {eq.longitude}°E)"
    prompts = {
        "trend": ("你是地震学家。请用100-150字中文回复。", f"{summary}。分析该区域地震活动趋势。"),
        "risk": ("你是地震灾害评估专家。请用100-150字中文回复。", f"{summary}。评估可能的风险。"),
        "impact": ("你是应急救援管理专家。请用100-150字中文回复。", f"{summary}。评估影响和应对建议。"),
    }
    sp, up = prompts.get(at, prompts["trend"])
    ai_text = call_deepseek(sp, up)
    if ai_text is None:
        raise HTTPException(status_code=500, detail="AI 服务不可用")

    db.execute(text(
        "INSERT INTO earthquake_ai_analysis (event_id, analysis_type, content) VALUES (:eid, :at, :ct)"
    ), {"eid": event_id, "at": at, "ct": ai_text})
    db.commit()
    return {"code": 200, "message": "AI 分析完成", "data": {"analysis_type": at, "content": ai_text, "cached": False}}


@router.delete("/ai_cache")
def clear_ai_cache(body: dict, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """删除指定地震事件的 AI 分析缓存"""
    event_id = body.get("event_id", "").strip()
    at = body.get("analysis_type", "").strip()
    if not event_id:
        raise HTTPException(status_code=400, detail="缺少 event_id")
    if at:
        db.execute(text(
            "DELETE FROM earthquake_ai_analysis WHERE event_id = :eid AND analysis_type = :at"
        ), {"eid": event_id, "at": at})
    else:
        db.execute(text(
            "DELETE FROM earthquake_ai_analysis WHERE event_id = :eid"
        ), {"eid": event_id})
    db.commit()
    return {"code": 200, "message": "缓存已清理", "data": None}
