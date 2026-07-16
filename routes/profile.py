# ============================================================
# routes/profile.py —— 个人信息模块
# ============================================================

import re

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session
)
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_connection

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT UserName, Email, Password,
               Question1, Answer1Hash, Question2, Answer2Hash
        FROM Users
        WHERE UserID = %s
    """, (session['user_id'],))
    user = cursor.fetchone()

    if not user:
        return redirect('/login')

    username = user[0]
    email = user[1]
    password_hash = user[2]
    question1 = user[3]
    answer1_hash = user[4]
    question2 = user[5]
    answer2_hash = user[6]

    error = None
    success = None

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'change_email':
            current_password = request.form.get('current_password', '')
            new_email = request.form.get('new_email', '').strip()
            confirm_new_email = request.form.get('confirm_new_email', '').strip()

            if new_email != confirm_new_email:
                error = '两次输入的新邮箱不一致'
            elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', new_email):
                error = '新邮箱格式不正确'
            elif not check_password_hash(password_hash, current_password):
                error = '当前密码错误，验证失败'
            else:
                cursor.execute("""
                    SELECT UserID FROM Users
                    WHERE Email = %s AND UserID != %s
                """, (new_email, session['user_id']))
                if cursor.fetchone():
                    error = '该邮箱已被其他账号绑定'
                else:
                    cursor.execute("""
                        UPDATE Users SET Email = %s WHERE UserID = %s
                    """, (new_email, session['user_id']))
                    conn.commit()
                    success = '邮箱修改成功！'
                    email = new_email

        elif action == 'change_password':
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_new_password = request.form.get('confirm_new_password', '')

            if new_password != confirm_new_password:
                error = '两次输入的新密码不一致'
            elif len(new_password) < 8 or len(new_password) > 50:
                error = '新密码必须8-50个字符'
            elif ' ' in new_password:
                error = '密码不能包含空格'
            elif not check_password_hash(password_hash, current_password):
                error = '当前密码错误，验证失败'
            else:
                new_hashed = generate_password_hash(new_password)
                cursor.execute("""
                    UPDATE Users SET Password = %s WHERE UserID = %s
                """, (new_hashed, session['user_id']))
                conn.commit()
                success = '密码修改成功！'

        elif action == 'change_security_questions':
            question1_new = request.form.get('question1', '').strip()
            answer1_new = request.form.get('answer1', '').strip()
            question2_new = request.form.get('question2', '').strip()
            answer2_new = request.form.get('answer2', '').strip()
            current_password = request.form.get('current_password_for_security', '')

            if len(question1_new) < 2 or len(question1_new) > 100:
                error = '安全问题1必须2-100个字符'
            elif len(answer1_new) < 1 or len(answer1_new) > 30:
                error = '答案1必须1-30个字符'
            elif len(question2_new) < 2 or len(question2_new) > 100:
                error = '安全问题2必须2-100个字符'
            elif len(answer2_new) < 1 or len(answer2_new) > 30:
                error = '答案2必须1-30个字符'
            elif not check_password_hash(password_hash, current_password):
                error = '当前密码错误，验证失败'
            else:
                hashed_answer1 = generate_password_hash(answer1_new)
                hashed_answer2 = generate_password_hash(answer2_new)
                cursor.execute("""
                    UPDATE Users
                    SET Question1 = %s, Answer1Hash = %s,
                        Question2 = %s, Answer2Hash = %s
                    WHERE UserID = %s
                """, (question1_new, hashed_answer1, question2_new, hashed_answer2, session['user_id']))
                conn.commit()
                success = '安全问题修改成功！'
                question1 = question1_new
                question2 = question2_new

    # 脱敏处理
    display_username = username
    local_part, domain_part = email.split('@')
    if len(local_part) <= 2:
        masked_local = '*' * len(local_part)
    else:
        masked_local = local_part[0] + '*' * (len(local_part) - 2) + local_part[-1]
    masked_email = masked_local + '@' + domain_part

    return render_template(
        'profile.html',
        display_username=display_username,
        masked_email=masked_email,
        error=error,
        success=success,
        question1=question1,
        question2=question2
    )
