# ============================================================
# routes/auth.py —— 用户认证模块
# ============================================================

import re
from datetime import datetime, timedelta

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    send_file
)
from werkzeug.security import generate_password_hash, check_password_hash

from captcha import generate_captcha_response
from db import get_connection

auth_bp = Blueprint('auth', __name__)


def _get_remaining_minutes(lockout_until):
    """计算账户剩余锁定分钟数（统一算法）"""
    if not lockout_until:
        return 0
    now = datetime.now()
    if lockout_until <= now:
        return 0
    remaining_seconds = (lockout_until - now).total_seconds()
    return int(remaining_seconds // 60) + 1


@auth_bp.route('/')
def home():
    if 'user_id' in session:
        return redirect('/search')
    return render_template('index.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if not username or not password:
        return render_template('login.html', error='用户名和密码不能为空')

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT UserID, UserName, Password, FailedAttempts, LockoutUntil
        FROM Users
        WHERE UserName = %s
    """, (username,))
    user = cursor.fetchone()

    if not user:
        return render_template('login.html', error='用户名或密码错误')

    user_id = user.UserID
    username_db = user.UserName
    password_hash = user.Password
    failed_attempts = user.FailedAttempts if user.FailedAttempts is not None else 0
    lockout_until = user.LockoutUntil

    # 检查锁定
    remaining_minutes = _get_remaining_minutes(lockout_until)
    if remaining_minutes > 0:
        return render_template(
            'login.html',
            error=f'账户已被锁定，请 {remaining_minutes} 分钟后重试'
        )

    if check_password_hash(password_hash, password):
        cursor.execute("""
            UPDATE Users
            SET FailedAttempts = 0, LockoutUntil = NULL
            WHERE UserID = %s
        """, (user_id,))
        conn.commit()
        session['user_id'] = user_id
        session['username'] = username_db
        return redirect('/search')
    else:
        failed_attempts += 1
        lockout_time = None
        if failed_attempts >= 5:
            lockout_time = datetime.now() + timedelta(minutes=30)
            error_msg = '密码错误次数过多，账户已被锁定30分钟'
        else:
            remaining = 5 - failed_attempts
            error_msg = f'用户名或密码错误，剩余 {remaining} 次尝试机会'

        cursor.execute("""
            UPDATE Users
            SET FailedAttempts = %s, LockoutUntil = %s
            WHERE UserID = %s
        """, (failed_attempts, lockout_time, user_id))
        conn.commit()
        return render_template('login.html', error=error_msg)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    email = request.form.get('email', '').strip()
    question1 = request.form.get('question1', '').strip()
    answer1 = request.form.get('answer1', '').strip()
    question2 = request.form.get('question2', '').strip()
    answer2 = request.form.get('answer2', '').strip()

    if len(username) < 2 or len(username) > 20:
        return render_template('register.html', error='用户名必须2-20个字符')
    if not re.match(r'^[a-zA-Z0-9_一-龥]+$', username):
        return render_template('register.html', error='用户名只能包含字母、数字、下划线或中文')
    if len(password) < 8 or len(password) > 50:
        return render_template('register.html', error='密码必须8-50个字符')
    if ' ' in password:
        return render_template('register.html', error='密码不能包含空格')
    if password != confirm_password:
        return render_template('register.html', error='两次输入的密码不一致')
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return render_template('register.html', error='邮箱格式不正确')
    if len(question1) < 2 or len(question1) > 100:
        return render_template('register.html', error='安全问题1必须2-100个字符')
    if len(answer1) < 1 or len(answer1) > 30:
        return render_template('register.html', error='答案1必须1-30个字符')
    if len(question2) < 2 or len(question2) > 100:
        return render_template('register.html', error='安全问题2必须2-100个字符')
    if len(answer2) < 1 or len(answer2) > 30:
        return render_template('register.html', error='答案2必须1-30个字符')

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT UserID FROM Users WHERE UserName = %s OR Email = %s
    """, (username, email))
    if cursor.fetchone():
        return render_template('register.html', error='用户名或邮箱已存在')

    hashed_password = generate_password_hash(password)
    hashed_answer1 = generate_password_hash(answer1)
    hashed_answer2 = generate_password_hash(answer2)

    cursor.execute("""
        INSERT INTO Users
            (UserName, Password, Email, Question1, Answer1Hash, Question2, Answer2Hash)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (username, hashed_password, email, question1, hashed_answer1, question2, hashed_answer2))

    conn.commit()
    return redirect('/login')


@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html')

    username = request.form.get('username', '').strip()
    captcha_user_input = request.form.get('captcha', '').strip()
    step = request.form.get('step')

    if not username:
        return render_template('forgot_password.html', error='请输入用户名')

    # Bug #10 修复：明确使用 step 字段控制状态流转，不依赖 answer1/answer2 是否存在
    if step == '1':
        if not captcha_user_input:
            return render_template('forgot_password.html', error='请输入验证码')
        expected_captcha = session.get('captcha_text', '')
        if captcha_user_input.upper() != expected_captcha.upper():
            session.pop('captcha_text', None)
            return render_template('forgot_password.html', error='验证码错误，请重新输入')
        session.pop('captcha_text', None)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT UserID, Question1, Answer1Hash, Question2, Answer2Hash,
               FailedAttempts, LockoutUntil
        FROM Users
        WHERE UserName = %s
    """, (username,))
    user = cursor.fetchone()

    if not user:
        return render_template('forgot_password.html', error='用户名不存在')

    user_id = user[0]
    question1 = user[1]
    answer1_hash = user[2]
    question2 = user[3]
    answer2_hash = user[4]
    failed_attempts = user[5] if user[5] is not None else 0
    lockout_until = user[6]

    remaining = _get_remaining_minutes(lockout_until)
    if remaining > 0:
        return render_template('forgot_password.html',
                               error=f'账户已被锁定，请 {remaining} 分钟后重试')

    if not question1 or not answer1_hash or not question2 or not answer2_hash:
        return render_template('forgot_password.html',
                               error='该账户未设置安全问题，请联系管理员重置密码')

    answer1 = request.form.get('answer1', '').strip()
    answer2 = request.form.get('answer2', '').strip()
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not answer1 or not answer2:
        return render_template('forgot_password.html',
                               questions=[question1, question2],
                               username=username)

    if len(new_password) < 8 or len(new_password) > 50:
        return render_template('forgot_password.html',
                               questions=[question1, question2],
                               username=username,
                               error='密码必须8-50个字符')
    if ' ' in new_password:
        return render_template('forgot_password.html',
                               questions=[question1, question2],
                               username=username,
                               error='密码不能包含空格')
    if new_password != confirm_password:
        return render_template('forgot_password.html',
                               questions=[question1, question2],
                               username=username,
                               error='两次输入的密码不一致')

    if check_password_hash(answer1_hash, answer1) and check_password_hash(answer2_hash, answer2):
        hashed_password = generate_password_hash(new_password)
        cursor.execute("""
            UPDATE Users
            SET Password = %s, FailedAttempts = 0, LockoutUntil = NULL
            WHERE UserID = %s
        """, (hashed_password, user_id))
        conn.commit()
        return render_template('forgot_password.html',
                               success='密码重置成功，请返回登录')
    else:
        failed_attempts += 1
        lockout_time = None
        if failed_attempts >= 3:
            lockout_time = datetime.now() + timedelta(minutes=30)

        cursor.execute("""
            UPDATE Users
            SET FailedAttempts = %s, LockoutUntil = %s
            WHERE UserID = %s
        """, (failed_attempts, lockout_time, user_id))
        conn.commit()

        remaining_tries = 3 - failed_attempts
        if remaining_tries <= 0:
            return render_template('forgot_password.html',
                                   questions=[question1, question2],
                                   username=username,
                                   error='账户已被锁定，请30分钟后重试')
        else:
            return render_template('forgot_password.html',
                                   questions=[question1, question2],
                                   username=username,
                                   error=f'答案错误，剩余 {remaining_tries} 次尝试机会')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@auth_bp.route('/captcha')
def captcha():
    buf, text = generate_captcha_response()
    session['captcha_text'] = text
    return send_file(buf, mimetype='image/png')
