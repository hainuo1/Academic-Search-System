import jwt
import datetime
from functools import wraps
from flask import request, jsonify

JWT_SECRET = 'academic-search-jwt-secret-2026'
JWT_EXPIRY_HOURS = 24


def create_token(user_id, username):
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
        'iat': datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def verify_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        token = auth.replace('Bearer ', '') if auth else ''
        if not token:
            return jsonify({'code': 401, 'message': '请先登录', 'data': None})
        payload = verify_token(token)
        if not payload:
            return jsonify({'code': 401, 'message': '登录已过期，请重新登录', 'data': None})
        request.user_id = payload['user_id']
        request.username = payload['username']
        return f(*args, **kwargs)
    return decorated


def process_keywords(cursor, doc_id, keywords_list):
    for kw in keywords_list:
        cursor.execute("SELECT KeywordID FROM Keywords WHERE KeywordName=%s", (kw,))
        row = cursor.fetchone()
        if row:
            kid = row.KeywordID
        else:
            cursor.execute("INSERT INTO Keywords (KeywordName) VALUES (%s)", (kw,))
            kid = cursor.lastrowid
        cursor.execute(
            "INSERT INTO DocumentKeyword (DocumentID, KeywordID, TF_IDF) VALUES (%s, %s, %s)",
            (doc_id, kid, 1.0)
        )


def get_pagination(page_param, total_count, per_page=10):
    try:
        page = int(page_param) if page_param else 1
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1
    total_pages = max(1, (total_count + per_page - 1) // per_page)
    if page > total_pages:
        page = total_pages
    offset = (page - 1) * per_page
    return page, offset, total_pages
