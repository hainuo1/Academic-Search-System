"""
个人中心路由 —— 查看 / 修改邮箱 / 修改密码 / 修改安全问题
"""
import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas import ChangeEmailRequest, ChangePasswordRequest, ChangeSecurityRequest

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("")
def get_profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    u = db.execute(
        text("SELECT user_name, email, question1, question2 FROM users WHERE user_id = :uid"),
        {"uid": current_user["user_id"]},
    ).fetchone()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")
    lp, dp = u.email.split("@")
    masked = (lp[0] + "*" * (len(lp) - 2) + lp[-1] + "@" + dp) if len(lp) > 2 else ("*" * len(lp) + "@" + dp)
    return {"code": 200, "message": "ok", "data": {
        "username": u.user_name, "email": masked,
        "question1": u.question1 or "", "question2": u.question2 or "",
    }}


@router.put("/email")
def change_email(body: ChangeEmailRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if body.new_email != body.confirm_new_email:
        raise HTTPException(status_code=400, detail="两次输入的新邮箱不一致")
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", body.new_email):
        raise HTTPException(status_code=400, detail="新邮箱格式不正确")

    u = db.execute(text("SELECT password FROM users WHERE user_id = :uid"), {"uid": current_user["user_id"]}).fetchone()
    if not check_password_hash(u.password, body.current_password):
        raise HTTPException(status_code=401, detail="当前密码错误")

    exist = db.execute(text("SELECT user_id FROM users WHERE email = :em AND user_id != :uid"),
                       {"em": body.new_email, "uid": current_user["user_id"]}).fetchone()
    if exist:
        raise HTTPException(status_code=400, detail="该邮箱已被其他账号绑定")

    db.execute(text("UPDATE users SET email = :em WHERE user_id = :uid"), {"em": body.new_email, "uid": current_user["user_id"]})
    db.commit()
    return {"code": 200, "message": "邮箱修改成功", "data": None}


@router.put("/password")
def change_password(body: ChangePasswordRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if body.new_password != body.confirm_new_password:
        raise HTTPException(status_code=400, detail="两次输入的新密码不一致")
    if len(body.new_password) < 8 or len(body.new_password) > 50:
        raise HTTPException(status_code=400, detail="新密码必须8-50个字符")
    if " " in body.new_password:
        raise HTTPException(status_code=400, detail="密码不能包含空格")

    u = db.execute(text("SELECT password FROM users WHERE user_id = :uid"), {"uid": current_user["user_id"]}).fetchone()
    if not check_password_hash(u.password, body.current_password):
        raise HTTPException(status_code=401, detail="当前密码错误")

    db.execute(text("UPDATE users SET password = :pw WHERE user_id = :uid"),
               {"pw": generate_password_hash(body.new_password), "uid": current_user["user_id"]})
    db.commit()
    return {"code": 200, "message": "密码修改成功", "data": None}


@router.put("/security")
def change_security(body: ChangeSecurityRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if len(body.question1) < 2 or len(body.question1) > 100 or len(body.answer1) < 1 or len(body.answer1) > 30:
        raise HTTPException(status_code=400, detail="安全问题1或答案格式不正确")
    if len(body.question2) < 2 or len(body.question2) > 100 or len(body.answer2) < 1 or len(body.answer2) > 30:
        raise HTTPException(status_code=400, detail="安全问题2或答案格式不正确")

    u = db.execute(text("SELECT password FROM users WHERE user_id = :uid"), {"uid": current_user["user_id"]}).fetchone()
    if not check_password_hash(u.password, body.current_password):
        raise HTTPException(status_code=401, detail="当前密码错误")

    db.execute(text(
        "UPDATE users SET question1=:q1, answer1_hash=:a1, question2=:q2, answer2_hash=:a2 WHERE user_id=:uid"
    ), {
        "q1": body.question1, "a1": generate_password_hash(body.answer1),
        "q2": body.question2, "a2": generate_password_hash(body.answer2),
        "uid": current_user["user_id"],
    })
    db.commit()
    return {"code": 200, "message": "安全问题修改成功", "data": None}
