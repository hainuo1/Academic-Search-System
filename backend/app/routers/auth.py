"""
认证路由 —— 登录 / 注册 / 找回密码 / 验证码
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash

from app.core.database import get_db
from app.core.security import create_access_token, get_current_user
from app.schemas import (
    LoginRequest, RegisterRequest, ForgotPasswordStep1, ForgotPasswordStep2,
)
from app.services import generate_captcha

router = APIRouter(prefix="/api", tags=["auth"])


def _lock_minutes(until):
    if not until:
        return 0
    now = datetime.now()
    if until <= now:
        return 0
    return int((until - now).total_seconds() // 60) + 1


# ── 登录 ──────────────────────────────────────────────
@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    u = db.execute(
        text("SELECT user_id, user_name, password, failed_attempts, lockout_until FROM users WHERE user_name = :un"),
        {"un": body.username},
    ).fetchone()
    if not u:
        raise HTTPException(status_code=401, detail="账号不存在，请检查用户名或前往注册")

    m = _lock_minutes(u.lockout_until)
    if m > 0:
        return {"code": 403, "message": f"账户已被锁定，请 {m} 分钟后重试", "data": None}

    if check_password_hash(u.password, body.password):
        db.execute(
            text("UPDATE users SET failed_attempts=0, lockout_until=NULL WHERE user_id=:uid"),
            {"uid": u.user_id},
        )
        db.commit()
        token = create_access_token(u.user_id, u.user_name)
        return {
            "code": 200, "message": "登录成功",
            "data": {"token": token, "user_id": u.user_id, "username": u.user_name},
        }

    fails = (u.failed_attempts or 0) + 1
    lock = datetime.now() + timedelta(minutes=30) if fails >= 5 else None
    db.execute(
        text("UPDATE users SET failed_attempts=:f, lockout_until=:l WHERE user_id=:uid"),
        {"f": fails, "l": lock, "uid": u.user_id},
    )
    db.commit()
    if fails >= 5:
        return {"code": 403, "message": "密码错误次数过多，账户已被锁定30分钟", "data": None}
    return {"code": 401, "message": f"用户名或密码错误，剩余 {5 - fails} 次尝试机会", "data": None}


# ── 注册 ──────────────────────────────────────────────
@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    import re

    if len(body.username) < 2 or len(body.username) > 20:
        raise HTTPException(status_code=400, detail="用户名必须2-20个字符")
    if not re.match(r"^[a-zA-Z0-9_一-鿿]+$", body.username):
        raise HTTPException(status_code=400, detail="用户名只能包含字母、数字、下划线或中文")
    if len(body.password) < 8 or len(body.password) > 50:
        raise HTTPException(status_code=400, detail="密码必须8-50个字符")
    if " " in body.password:
        raise HTTPException(status_code=400, detail="密码不能包含空格")
    if body.password != body.confirm_password:
        raise HTTPException(status_code=400, detail="两次输入的密码不一致")
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", body.email):
        raise HTTPException(status_code=400, detail="邮箱格式不正确")

    existing = db.execute(
        text("SELECT user_id FROM users WHERE user_name = :un OR email = :em"),
        {"un": body.username, "em": body.email},
    ).fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")

    db.execute(
        text("INSERT INTO users (user_name, password, email, question1, answer1_hash, question2, answer2_hash) "
             "VALUES (:un, :pw, :em, :q1, :a1, :q2, :a2)"),
        {
            "un": body.username, "pw": generate_password_hash(body.password),
            "em": body.email, "q1": body.question1, "a1": generate_password_hash(body.answer1),
            "q2": body.question2, "a2": generate_password_hash(body.answer2),
        },
    )
    db.commit()
    return {"code": 200, "message": "注册成功，请登录", "data": None}


# ── 找回密码 ──────────────────────────────────────────
@router.post("/forgot_password")
def forgot_password(body: ForgotPasswordStep1 | ForgotPasswordStep2 | dict, request: Request, db: Session = Depends(get_db)):
    # FastAPI 不能直接区分两个 body 类型，我们通过 step 字段手动判断
    if isinstance(body, dict):
        step = body.get("step", "1")
    else:
        step = body.step if hasattr(body, "step") else "1"

    username = body.get("username", "").strip() if isinstance(body, dict) else body.username

    if step == "1":
        captcha = body.get("captcha", "").strip() if isinstance(body, dict) else body.captcha
        if not captcha:
            return {"code": 400, "message": "请输入验证码", "data": None}
        expected = request.cookies.get("captcha_text", "")
        if captcha.upper() != expected.upper():
            return {"code": 400, "message": "验证码错误", "data": None}

    u = db.execute(
        text("SELECT user_id, question1, answer1_hash, question2, answer2_hash, failed_attempts, lockout_until FROM users WHERE user_name = :un"),
        {"un": username},
    ).fetchone()
    if not u:
        return {"code": 404, "message": "用户名不存在", "data": None}

    m = _lock_minutes(u.lockout_until)
    if m > 0:
        return {"code": 403, "message": f"账户已被锁定，请 {m} 分钟后重试", "data": None}

    if not u.question1 or not u.question2:
        return {"code": 400, "message": "该账户未设置安全问题", "data": None}

    if step == "1":
        return {"code": 200, "message": "验证码验证通过", "data": {"username": username, "questions": [u.question1, u.question2]}}

    # step 2
    a1 = body.get("answer1", "").strip() if isinstance(body, dict) else (body.answer1 or "")
    a2 = body.get("answer2", "").strip() if isinstance(body, dict) else (body.answer2 or "")
    npw = body.get("new_password", "") if isinstance(body, dict) else (body.new_password or "")
    cpw = body.get("confirm_password", "") if isinstance(body, dict) else (body.confirm_password or "")

    if not a1 or not a2:
        return {"code": 400, "message": "请回答两个安全问题", "data": None}
    if len(npw) < 8 or len(npw) > 50:
        return {"code": 400, "message": "密码必须8-50个字符", "data": None}
    if " " in npw:
        return {"code": 400, "message": "密码不能包含空格", "data": None}
    if npw != cpw:
        return {"code": 400, "message": "两次输入的密码不一致", "data": None}

    if check_password_hash(u.answer1_hash, a1) and check_password_hash(u.answer2_hash, a2):
        db.execute(
            text("UPDATE users SET password=:pw, failed_attempts=0, lockout_until=NULL WHERE user_id=:uid"),
            {"pw": generate_password_hash(npw), "uid": u.user_id},
        )
        db.commit()
        return {"code": 200, "message": "密码重置成功，请重新登录", "data": None}

    fails = (u.failed_attempts or 0) + 1
    lock = datetime.now() + timedelta(minutes=30) if fails >= 3 else None
    db.execute(
        text("UPDATE users SET failed_attempts=:f, lockout_until=:l WHERE user_id=:uid"),
        {"f": fails, "l": lock, "uid": u.user_id},
    )
    db.commit()
    if fails >= 3:
        return {"code": 403, "message": "账户已被锁定，请30分钟后重试", "data": None}
    return {"code": 401, "message": f"答案错误，剩余 {3 - fails} 次尝试机会", "data": None}


# ── 退出 ──────────────────────────────────────────────
@router.post("/logout")
def logout():
    return {"code": 200, "message": "已退出登录", "data": None}


# ── 验证码 ────────────────────────────────────────────
@router.get("/captcha")
def captcha():
    buf, text = generate_captcha()
    sr = StreamingResponse(buf, media_type="image/png")
    sr.set_cookie(key="captcha_text", value=text, max_age=300, httponly=True, samesite="lax")
    return sr


# ── 当前用户信息 ──────────────────────────────────────
@router.get("/user/me")
def me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    u = db.execute(
        text("SELECT user_name, email FROM users WHERE user_id = :uid"),
        {"uid": current_user["user_id"]},
    ).fetchone()
    if not u:
        return {"code": 404, "message": "用户不存在", "data": None}
    lp, dp = u.email.split("@")
    masked = (lp[0] + "*" * (len(lp) - 2) + lp[-1] + "@" + dp) if len(lp) > 2 else ("*" * len(lp) + "@" + dp)
    return {"code": 200, "message": "ok", "data": {"user_id": current_user["user_id"], "username": u.user_name, "email": masked}}
