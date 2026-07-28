"""
收藏夹路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/api", tags=["favorites"])


@router.get("/favorites")
def list_fav(
    page: int = Query(default=1),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pp = 10
    total = db.execute(text("SELECT COUNT(*) FROM favorites WHERE user_id = :uid"), {"uid": current_user["user_id"]}).scalar()
    total_pages = max(1, (total + pp - 1) // pp)
    page = max(1, min(page, total_pages))
    offset = (page - 1) * pp

    rows = db.execute(text(
        "SELECT d.document_id, d.title, d.author, d.publish_date FROM favorites f "
        "JOIN documents d ON f.document_id = d.document_id "
        "WHERE f.user_id = :uid ORDER BY f.create_time DESC LIMIT :lim OFFSET :off"
    ), {"uid": current_user["user_id"], "lim": pp, "off": offset}).fetchall()

    docs = [{"id": r.document_id, "title": r.title, "author": r.author, "publish_date": str(r.publish_date) if r.publish_date else ""} for r in rows]
    return {"code": 200, "message": "ok", "data": {"documents": docs, "total_count": total, "page": page, "total_pages": total_pages}}


@router.post("/toggle_favorite")
def toggle(body: dict, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    did = body.get("document_id")
    if not did:
        raise HTTPException(status_code=400, detail="参数错误")

    exists_doc = db.execute(text("SELECT document_id FROM documents WHERE document_id = :did"), {"did": did}).fetchone()
    if not exists_doc:
        raise HTTPException(status_code=404, detail="该文献不存在")

    fav = db.execute(text(
        "SELECT favorite_id FROM favorites WHERE user_id = :uid AND document_id = :did"
    ), {"uid": current_user["user_id"], "did": did}).fetchone()

    if fav:
        db.execute(text("DELETE FROM favorites WHERE favorite_id = :fid"), {"fid": fav.favorite_id})
        is_fav = False
    else:
        db.execute(text("INSERT INTO favorites(user_id, document_id) VALUES(:uid, :did)"), {"uid": current_user["user_id"], "did": did})
        is_fav = True
    db.commit()
    return {"code": 200, "message": "已收藏" if is_fav else "已取消收藏", "data": {"is_favorited": is_fav}}
