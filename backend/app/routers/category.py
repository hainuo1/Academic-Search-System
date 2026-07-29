"""
文献分类标签路由 —— 分类标签表 CRUD + 检索 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/api", tags=["category"])


@router.get("/categories")
def list_categories(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取所有可用的分类标签"""
    rows = db.execute(text(
        "SELECT category_id, category_name, sort_order FROM literature_categories ORDER BY sort_order, category_name"
    )).fetchall()
    cats = [
        {"id": r.category_id, "name": r.category_name, "sort_order": r.sort_order}
        for r in rows
    ]
    return {"code": 200, "message": "ok", "data": {"categories": cats}}


@router.post("/categories")
def add_category(
    name: str = "",
    sort_order: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """添加分类标签"""
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="分类名称不能为空")
    try:
        db.execute(text(
            "INSERT INTO literature_categories (category_name, sort_order) VALUES (:n, :o)"
        ), {"n": name, "o": sort_order})
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="该分类已存在")
    return {"code": 200, "message": "添加成功", "data": None}


@router.delete("/categories/{cat_id}")
def delete_category(
    cat_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除分类标签"""
    r = db.execute(text(
        "SELECT category_name FROM literature_categories WHERE category_id = :cid"
    ), {"cid": cat_id}).fetchone()
    if not r:
        raise HTTPException(status_code=404, detail="分类不存在")
    db.execute(text(
        "DELETE FROM literature_categories WHERE category_id = :cid"
    ), {"cid": cat_id})
    db.commit()
    return {"code": 200, "message": f"分类「{r.category_name}」已删除", "data": None}


@router.post("/categories/seed")
def seed_categories(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """导入预设分类标签"""
    default_categories = [
        ("人工智能", 1),
        ("机器学习", 2),
        ("深度学习", 3),
        ("自然语言处理", 4),
        ("计算机视觉", 5),
        ("数据挖掘", 6),
        ("数据库", 7),
        ("信息检索", 8),
        ("软件工程", 9),
        ("操作系统", 10),
        ("计算机网络", 11),
        ("网络安全", 12),
        ("物联网", 13),
        ("云计算", 14),
        ("大数据", 15),
        ("遥感技术", 16),
        ("地理信息系统", 17),
        ("气象科学", 18),
        ("大气物理学", 19),
        ("海洋科学", 20),
        ("地震学", 21),
        ("地质学", 22),
        ("环境科学", 23),
        ("统计学", 24),
        ("数学", 25),
        ("物理学", 26),
        ("化学", 27),
        ("生物学", 28),
        ("医学", 29),
    ]
    added = 0
    for name, order in default_categories:
        exists = db.execute(text(
            "SELECT category_id FROM literature_categories WHERE category_name = :n"
        ), {"n": name}).fetchone()
        if not exists:
            db.execute(text(
                "INSERT INTO literature_categories (category_name, sort_order) VALUES (:n, :o)"
            ), {"n": name, "o": order})
            added += 1
    db.commit()
    return {"code": 200, "message": f"预设分类导入完成，新增 {added} 个", "data": {"added": added}}


@router.get("/categories/search")
def search_categories(
    q: str = "",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """检索分类标签（供选择器使用）"""
    if q.strip():
        rows = db.execute(text(
            "SELECT category_id, category_name, sort_order FROM literature_categories "
            "WHERE category_name ILIKE :q ORDER BY sort_order, category_name"
        ), {"q": f"%{q.strip()}%"}).fetchall()
    else:
        rows = db.execute(text(
            "SELECT category_id, category_name, sort_order FROM literature_categories ORDER BY sort_order, category_name"
        )).fetchall()
    cats = [
        {"id": r.category_id, "name": r.category_name, "sort_order": r.sort_order}
        for r in rows
    ]
    return {"code": 200, "message": "ok", "data": {"categories": cats}}
