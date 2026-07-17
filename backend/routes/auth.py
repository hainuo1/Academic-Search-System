import re
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash

from captcha import generate
from db import get_connection
from utils import create_token, login_required

auth_bp = Blueprint('auth', __name__)


def _lock_minutes(until):
    if not until: return 0
    now = datetime.now()
    if until <= now: return 0
    return int((until - now).total_seconds() // 60) + 1


# ── 登录 ──────────────────────────────────────────────
@auth_bp.route('/api/login', methods=['POST'])
def login():
    d = request.get_json() or {}
    username = d.get('username', '').strip()
    password = d.get('password', '').strip()
    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空', 'data': None})

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT UserID,UserName,Password,FailedAttempts,LockoutUntil FROM Users WHERE UserName=%s", (username,))
    u = cur.fetchone()
    if not u:
        return jsonify({'code': 401, 'message': '用户名或密码错误', 'data': None})

    m = _lock_minutes(u.LockoutUntil)
    if m > 0:
        return jsonify({'code': 403, 'message': f'账户已被锁定，请 {m} 分钟后重试', 'data': None})

    if check_password_hash(u.Password, password):
        cur.execute("UPDATE Users SET FailedAttempts=0,LockoutUntil=NULL WHERE UserID=%s", (u.UserID,))
        conn.commit()
        token = create_token(u.UserID, u.UserName)
        return jsonify({'code': 200, 'message': '登录成功', 'data': {'token': token, 'user_id': u.UserID, 'username': u.UserName}})

    fails = (u.FailedAttempts or 0) + 1
    lock = datetime.now() + timedelta(minutes=30) if fails >= 5 else None
    cur.execute("UPDATE Users SET FailedAttempts=%s,LockoutUntil=%s WHERE UserID=%s", (fails, lock, u.UserID))
    conn.commit()
    if fails >= 5:
        return jsonify({'code': 403, 'message': '密码错误次数过多，账户已被锁定30分钟', 'data': None})
    return jsonify({'code': 401, 'message': f'用户名或密码错误，剩余 {5 - fails} 次尝试机会', 'data': None})


# ── 注册 ──────────────────────────────────────────────
@auth_bp.route('/api/register', methods=['POST'])
def register():
    d = request.get_json() or {}
    username = d.get('username', '').strip()
    password = d.get('password', '')
    cp = d.get('confirm_password', '')
    email = d.get('email', '').strip()
    q1, a1 = d.get('question1', '').strip(), d.get('answer1', '').strip()
    q2, a2 = d.get('question2', '').strip(), d.get('answer2', '').strip()

    if len(username) < 2 or len(username) > 20:
        return jsonify({'code': 400, 'message': '用户名必须2-20个字符', 'data': None})
    if not re.match(r'^[a-zA-Z0-9_一-龥]+$', username):
        return jsonify({'code': 400, 'message': '用户名只能包含字母、数字、下划线或中文', 'data': None})
    if len(password) < 8 or len(password) > 50:
        return jsonify({'code': 400, 'message': '密码必须8-50个字符', 'data': None})
    if ' ' in password:
        return jsonify({'code': 400, 'message': '密码不能包含空格', 'data': None})
    if password != cp:
        return jsonify({'code': 400, 'message': '两次输入的密码不一致', 'data': None})
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({'code': 400, 'message': '邮箱格式不正确', 'data': None})
    if len(q1) < 2 or len(q1) > 100 or len(a1) < 1 or len(a1) > 30:
        return jsonify({'code': 400, 'message': '安全问题1或答案格式不正确', 'data': None})
    if len(q2) < 2 or len(q2) > 100 or len(a2) < 1 or len(a2) > 30:
        return jsonify({'code': 400, 'message': '安全问题2或答案格式不正确', 'data': None})

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT UserID FROM Users WHERE UserName=%s OR Email=%s", (username, email))
    if cur.fetchone():
        return jsonify({'code': 400, 'message': '用户名或邮箱已存在', 'data': None})

    cur.execute(
        "INSERT INTO Users (UserName,Password,Email,Question1,Answer1Hash,Question2,Answer2Hash) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (username, generate_password_hash(password), email, q1, generate_password_hash(a1), q2, generate_password_hash(a2)))
    conn.commit()
    return jsonify({'code': 200, 'message': '注册成功，请登录', 'data': None})


# ── 找回密码 ──────────────────────────────────────────
@auth_bp.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    d = request.get_json() or {}
    username = d.get('username', '').strip()
    step = d.get('step', '1')

    if not username:
        return jsonify({'code': 400, 'message': '请输入用户名', 'data': None})

    if step == '1':
        captcha = d.get('captcha', '').strip()
        if not captcha:
            return jsonify({'code': 400, 'message': '请输入验证码', 'data': None})
        expected = request.cookies.get('captcha_text', '')
        if captcha.upper() != expected.upper():
            return jsonify({'code': 400, 'message': '验证码错误', 'data': None})

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT UserID,Question1,Answer1Hash,Question2,Answer2Hash,FailedAttempts,LockoutUntil FROM Users WHERE UserName=%s", (username,))
    u = cur.fetchone()
    if not u:
        return jsonify({'code': 404, 'message': '用户名不存在', 'data': None})

    m = _lock_minutes(u[6])
    if m > 0:
        return jsonify({'code': 403, 'message': f'账户已被锁定，请 {m} 分钟后重试', 'data': None})

    if not u[1] or not u[2] or not u[3] or not u[4]:
        return jsonify({'code': 400, 'message': '该账户未设置安全问题', 'data': None})

    if step == '1':
        return jsonify({'code': 200, 'message': '验证码验证通过', 'data': {'username': username, 'questions': [u[1], u[3]]}})

    # step 2
    a1, a2 = d.get('answer1', '').strip(), d.get('answer2', '').strip()
    npw = d.get('new_password', '')
    cpw = d.get('confirm_password', '')

    if not a1 or not a2:
        return jsonify({'code': 400, 'message': '请回答两个安全问题', 'data': {'questions': [u[1], u[3]], 'username': username}})
    if len(npw) < 8 or len(npw) > 50:
        return jsonify({'code': 400, 'message': '密码必须8-50个字符', 'data': {'questions': [u[1], u[3]], 'username': username}})
    if ' ' in npw:
        return jsonify({'code': 400, 'message': '密码不能包含空格', 'data': {'questions': [u[1], u[3]], 'username': username}})
    if npw != cpw:
        return jsonify({'code': 400, 'message': '两次输入的密码不一致', 'data': {'questions': [u[1], u[3]], 'username': username}})

    if check_password_hash(u[2], a1) and check_password_hash(u[4], a2):
        cur.execute("UPDATE Users SET Password=%s,FailedAttempts=0,LockoutUntil=NULL WHERE UserID=%s",
                    (generate_password_hash(npw), u[0]))
        conn.commit()
        return jsonify({'code': 200, 'message': '密码重置成功，请重新登录', 'data': None})

    fails = (u[5] or 0) + 1
    lock = datetime.now() + timedelta(minutes=30) if fails >= 3 else None
    cur.execute("UPDATE Users SET FailedAttempts=%s,LockoutUntil=%s WHERE UserID=%s", (fails, lock, u[0]))
    conn.commit()
    if fails >= 3:
        return jsonify({'code': 403, 'message': '账户已被锁定，请30分钟后重试', 'data': {'questions': [u[1], u[3]], 'username': username}})
    return jsonify({'code': 401, 'message': f'答案错误，剩余 {3 - fails} 次尝试机会', 'data': {'questions': [u[1], u[3]], 'username': username}})


# ── 退出 ──────────────────────────────────────────────
@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    return jsonify({'code': 200, 'message': '已退出登录', 'data': None})


# ── 验证码 ────────────────────────────────────────────
@auth_bp.route('/api/captcha')
def captcha():
    buf, text = generate()
    resp = send_file(buf, mimetype='image/png')
    resp.set_cookie('captcha_text', text, max_age=300, httponly=True)
    return resp


# ── 当前用户信息 ──────────────────────────────────────
@auth_bp.route('/api/user/me')
@login_required
def me():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT UserName,Email FROM Users WHERE UserID=%s", (request.user_id,))
    u = cur.fetchone()
    if not u:
        return jsonify({'code': 404, 'message': '用户不存在', 'data': None})
    lp, dp = u.Email.split('@')
    masked = (lp[0] + '*' * (len(lp) - 2) + lp[-1] + '@' + dp) if len(lp) > 2 else ('*' * len(lp) + '@' + dp)
    return jsonify({'code': 200, 'message': 'ok', 'data': {'user_id': request.user_id, 'username': u.UserName, 'email': masked}})
