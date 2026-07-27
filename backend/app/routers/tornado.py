"""
龙卷风分析路由
"""
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.security import get_current_user
from app.services import call_deepseek

router = APIRouter(prefix="/api/tornado", tags=["tornado"])


def _parse_damage(raw):
    if not raw:
        return raw
    if not re.search(r"\b(length|width|loss):", raw, re.IGNORECASE):
        return raw
    parts = []
    m_len = re.search(r"length:\s*([\d.]+)\s*mi", raw, re.IGNORECASE)
    if m_len:
        mi = float(m_len.group(1))
        km = mi * 1.60934
        parts.append(f"路径长度 {mi:.1f} mi（约{km:.1f} km）")
    m_wid = re.search(r"width:\s*([\d.]+)\s*yd", raw, re.IGNORECASE)
    if m_wid:
        yd = float(m_wid.group(1))
        km_w = yd * 0.0009144
        parts.append(f"宽度 {yd:.0f} yd（约{km_w:.2f} km）")
    m_loss = re.search(r"loss:\s*([\d.]+)", raw, re.IGNORECASE)
    if m_loss:
        loss_val = float(m_loss.group(1))
        if loss_val >= 1_000_000:
            parts.append(f"经济损失 ${loss_val/1_000_000:.1f}M")
        elif loss_val >= 1_000:
            parts.append(f"经济损失 ${loss_val:,.0f}")
        else:
            parts.append(f"经济损失 ${loss_val:.0f}")
    return " · ".join(parts) if parts else raw


@router.get("/list")
def tornado_list(
    year: str = Query(default=""),
    keyword: str = Query(default=""),
    min_ef: str = Query(default=""),
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
    if keyword:
        conds.append("place ILIKE :kw")
        params["kw"] = f"%{keyword}%"
    if min_ef:
        try:
            conds.append("magnitude >= :me")
            params["me"] = int(min_ef)
        except ValueError:
            return {"code": 400, "message": "EF等级参数无效，请输入数字", "data": None}

    where = ("WHERE " + " AND ".join(conds)) if conds else ""
    total = db.execute(text(f"SELECT COUNT(*) FROM tornado_info {where}"), params).scalar()
    tp = max(1, (total + pp - 1) // pp)
    page = max(1, min(page, tp))
    off = (page - 1) * pp

    rows = db.execute(text(
        f"SELECT event_id, date_time, place, province, ef_scale, magnitude, casualties, deaths, injuries, damage "
        f"FROM tornado_info {where} ORDER BY magnitude DESC, deaths DESC, date_time DESC LIMIT :lim OFFSET :off"
    ), {**params, "lim": pp, "off": off}).fetchall()

    tornadoes = [
        {"event_id": r.event_id, "datetime": r.date_time.strftime("%Y-%m-%d %H:%M") if r.date_time else "",
         "place": r.place, "province": r.province, "ef_scale": r.ef_scale, "magnitude": r.magnitude,
         "casualties": r.casualties, "deaths": r.deaths, "injuries": r.injuries}
        for r in rows
    ]

    years_rows = db.execute(text("SELECT DISTINCT EXTRACT(YEAR FROM date_time) AS y FROM tornado_info ORDER BY y DESC")).fetchall()
    prov_rows = db.execute(text("SELECT DISTINCT province FROM tornado_info WHERE province != '' ORDER BY province")).fetchall()
    return {"code": 200, "message": "查询成功", "data": {
        "tornadoes": tornadoes, "total_count": total, "page": page, "total_pages": tp,
        "available_years": [int(r.y) for r in years_rows],
        "available_provinces": [r[0] for r in prov_rows],
    }}


@router.get("/{event_id}")
def tornado_detail(event_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.execute(text(
        "SELECT event_id, date_time, latitude, longitude, place, province, ef_scale, magnitude, casualties, deaths, injuries, damage "
        "FROM tornado_info WHERE event_id = :eid"
    ), {"eid": event_id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="龙卷风事件不存在")

    detail = {
        "event_id": row.event_id, "datetime": row.date_time.strftime("%Y-%m-%d %H:%M") if row.date_time else "",
        "latitude": row.latitude, "longitude": row.longitude, "place": row.place, "province": row.province,
        "ef_scale": row.ef_scale, "magnitude": row.magnitude, "casualties": row.casualties,
        "deaths": row.deaths, "injuries": row.injuries, "damage": _parse_damage(row.damage),
    }

    nearby_rows = db.execute(text(
        "SELECT date_time, ef_scale, magnitude, place, casualties, deaths FROM tornado_info "
        "WHERE province = :prov AND event_id != :eid ORDER BY date_time DESC LIMIT 200"
    ), {"prov": row.province, "eid": event_id}).fetchall()
    nearby = [
        {"datetime": r.date_time.strftime("%Y-%m-%d %H:%M") if r.date_time else "", "ef_scale": r.ef_scale,
         "magnitude": r.magnitude, "place": r.place, "casualties": r.casualties, "deaths": r.deaths}
        for r in nearby_rows
    ]

    # PostGIS 空间密度分析：100km 范围内统计（geography 类型确保真实公里）
    spatial_stats = None
    try:
        ss = db.execute(text("""
            SELECT
                COUNT(*) AS nearby_count,
                SUM(casualties) AS total_casualties,
                SUM(deaths) AS total_deaths,
                SUM(injuries) AS total_injuries,
                COALESCE(ROUND(AVG(magnitude), 1), 0) AS avg_mag,
                MAX(magnitude) AS max_mag
            FROM tornado_info
            WHERE event_id != :eid
              AND ST_DWithin(
                  geom::geography,
                  (SELECT geom::geography FROM tornado_info WHERE event_id = :eid2),
                  100000
              )
        """), {"eid": event_id, "eid2": event_id}).fetchone()
        if ss and ss.nearby_count > 0:
            spatial_stats = {
                "radius_km": 100,
                "nearby_count": ss.nearby_count,
                "total_casualties": ss.total_casualties or 0,
                "total_deaths": ss.total_deaths or 0,
                "total_injuries": ss.total_injuries or 0,
                "avg_magnitude": ss.avg_mag,
                "max_magnitude": ss.max_mag,
            }
    except Exception:
        pass  # PostGIS 未启用时静默跳过

    return {"code": 200, "message": "查询成功", "data": {"detail": detail, "nearby": nearby, "spatial_stats": spatial_stats}}


@router.post("/ai_analysis")
def ai_analysis(body: dict, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    event_id = body.get("event_id")
    at = body.get("analysis_type", "trend").strip()
    if not event_id:
        raise HTTPException(status_code=400, detail="缺少 event_id")

    cached = db.execute(text(
        "SELECT content FROM tornado_ai_analysis WHERE event_id = :eid AND analysis_type = :at"
    ), {"eid": event_id, "at": at}).fetchone()
    if cached:
        return {"code": 200, "message": "AI 分析完成（缓存）", "data": {"analysis_type": at, "content": cached.content, "cached": True}}

    tr = db.execute(text(
        "SELECT event_id, date_time, place, province, ef_scale, magnitude, casualties, deaths, injuries, damage "
        "FROM tornado_info WHERE event_id = :eid"
    ), {"eid": event_id}).fetchone()
    if not tr:
        raise HTTPException(status_code=404, detail="龙卷风事件不存在")

    summary = f"龙卷风：{tr.date_time} {tr.ef_scale}，发生于{tr.province}。死亡{tr.deaths or 0}人，受伤{tr.injuries or 0}人。{_parse_damage(tr.damage) or ''}"
    prompts = {
        "trend": ("你是气象学家。请用100-150字中文回复。", f"{summary}。分析该龙卷风的活动趋势。"),
        "risk": ("你是灾害评估专家。请用100-150字中文回复。", f"{summary}。评估风险等级与防范建议。"),
        "climate": ("你是气候学家。请用100-150字中文回复。", f"{summary}。分析该区域龙卷风气候特征。"),
    }
    sp, up = prompts.get(at, prompts["trend"])
    ai_text = call_deepseek(sp, up)
    if ai_text is None:
        raise HTTPException(status_code=500, detail="AI 服务不可用")

    db.execute(text(
        "INSERT INTO tornado_ai_analysis (event_id, analysis_type, content) VALUES (:eid, :at, :ct)"
    ), {"eid": event_id, "at": at, "ct": ai_text})
    db.commit()
    return {"code": 200, "message": "AI 分析完成", "data": {"analysis_type": at, "content": ai_text, "cached": False}}
