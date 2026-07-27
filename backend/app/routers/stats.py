"""
统计路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats")
def stats(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    kw_rows = db.execute(text("SELECT keyword, search_count FROM keyword_search_count ORDER BY search_count DESC LIMIT 10")).fetchall()
    kw = [{"keyword": r[0], "count": r[1]} for r in kw_rows]

    ur_rows = db.execute(text(
        "SELECT u.user_name, usc.search_count FROM user_search_count usc "
        "JOIN users u ON usc.user_id = u.user_id ORDER BY usc.search_count DESC LIMIT 10"
    )).fetchall()
    ur = [{"username": r[0], "count": r[1]} for r in ur_rows]

    cr_rows = db.execute(text(
        "SELECT d.document_id, d.title, COUNT(*) AS cnt FROM citation c "
        "JOIN documents d ON c.target_document_id = d.document_id "
        "GROUP BY d.document_id, d.title ORDER BY cnt DESC LIMIT 10"
    )).fetchall()
    cr = [{"id": r[0], "title": r[1], "count": r[2]} for r in cr_rows]

    vr_rows = db.execute(text("SELECT document_id, title, view_count FROM documents ORDER BY view_count DESC LIMIT 10")).fetchall()
    vr = [{"id": r[0], "title": r[1], "view_count": r[2]} for r in vr_rows]

    dr_rows = db.execute(text("SELECT document_id, title, download_count FROM documents ORDER BY download_count DESC LIMIT 10")).fetchall()
    dr = [{"id": r[0], "title": r[1], "download_count": r[2]} for r in dr_rows]

    fr_rows = db.execute(text(
        "SELECT d.document_id, d.title, COUNT(f.favorite_id) AS cnt FROM favorites f "
        "JOIN documents d ON f.document_id = d.document_id "
        "GROUP BY d.document_id, d.title ORDER BY cnt DESC LIMIT 10"
    )).fetchall()
    fr = [{"id": r[0], "title": r[1], "count": r[2]} for r in fr_rows]

    return {"code": 200, "message": "ok", "data": {
        "keyword_rank": kw, "user_rank": ur, "citation_rank": cr,
        "view_rank": vr, "download_rank": dr, "favorite_rank": fr,
    }}
