import re
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
from utils import login_required

prof_bp = Blueprint('profile', __name__)


@prof_bp.route('/api/profile')
@login_required
def get_profile():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT UserName,Email,Question1,Question2 FROM Users WHERE UserID=%s", (request.user_id,))
    u = cur.fetchone()
    if not u:
        return jsonify({'code': 404, 'message': '用户不存在', 'data': None})
    lp, dp = u[1].split('@')
    masked = (lp[0] + '*' * (len(lp) - 2) + lp[-1] + '@' + dp) if len(lp) > 2 else ('*' * len(lp) + '@' + dp)
    return jsonify({'code': 200, 'message': 'ok', 'data': {
        'username': u[0], 'email': masked, 'question1': u[2] or '', 'question2': u[3] or ''}})


@prof_bp.route('/api/profile/email', methods=['PUT'])
@login_required
def change_email():
    d = request.get_json() or {}
    pw, ne, ce = d.get('current_password', ''), d.get('new_email', '').strip(), d.get('confirm_new_email', '').strip()
    if ne != ce: return jsonify({'code': 400, 'message': '两次输入的新邮箱不一致', 'data': None})
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', ne): return jsonify({'code': 400, 'message': '新邮箱格式不正确', 'data': None})
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT Password FROM Users WHERE UserID=%s", (request.user_id,))
    if not check_password_hash(cur.fetchone()[0], pw): return jsonify({'code': 401, 'message': '当前密码错误', 'data': None})
    cur.execute("SELECT UserID FROM Users WHERE Email=%s AND UserID!=%s", (ne, request.user_id))
    if cur.fetchone(): return jsonify({'code': 400, 'message': '该邮箱已被其他账号绑定', 'data': None})
    cur.execute("UPDATE Users SET Email=%s WHERE UserID=%s", (ne, request.user_id))
    conn.commit()
    return jsonify({'code': 200, 'message': '邮箱修改成功', 'data': None})


@prof_bp.route('/api/profile/password', methods=['PUT'])
@login_required
def change_password():
    d = request.get_json() or {}
    pw, np, cp = d.get('current_password', ''), d.get('new_password', ''), d.get('confirm_new_password', '')
    if np != cp: return jsonify({'code': 400, 'message': '两次输入的新密码不一致', 'data': None})
    if len(np) < 8 or len(np) > 50: return jsonify({'code': 400, 'message': '新密码必须8-50个字符', 'data': None})
    if ' ' in np: return jsonify({'code': 400, 'message': '密码不能包含空格', 'data': None})
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT Password FROM Users WHERE UserID=%s", (request.user_id,))
    if not check_password_hash(cur.fetchone()[0], pw): return jsonify({'code': 401, 'message': '当前密码错误', 'data': None})
    cur.execute("UPDATE Users SET Password=%s WHERE UserID=%s", (generate_password_hash(np), request.user_id))
    conn.commit()
    return jsonify({'code': 200, 'message': '密码修改成功', 'data': None})


@prof_bp.route('/api/profile/security', methods=['PUT'])
@login_required
def change_security():
    d = request.get_json() or {}
    q1, a1 = d.get('question1', '').strip(), d.get('answer1', '').strip()
    q2, a2 = d.get('question2', '').strip(), d.get('answer2', '').strip()
    pw = d.get('current_password', '')
    if len(q1) < 2 or len(q1) > 100 or len(a1) < 1 or len(a1) > 30: return jsonify({'code': 400, 'message': '安全问题1或答案格式不正确', 'data': None})
    if len(q2) < 2 or len(q2) > 100 or len(a2) < 1 or len(a2) > 30: return jsonify({'code': 400, 'message': '安全问题2或答案格式不正确', 'data': None})
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT Password FROM Users WHERE UserID=%s", (request.user_id,))
    if not check_password_hash(cur.fetchone()[0], pw): return jsonify({'code': 401, 'message': '当前密码错误', 'data': None})
    cur.execute("UPDATE Users SET Question1=%s,Answer1Hash=%s,Question2=%s,Answer2Hash=%s WHERE UserID=%s",
                (q1, generate_password_hash(a1), q2, generate_password_hash(a2), request.user_id))
    conn.commit()
    return jsonify({'code': 200, 'message': '安全问题修改成功', 'data': None})
