# ============================================================
# routes/citation.py —— 引用关系管理模块
# ============================================================

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    jsonify
)

from db import get_connection

citation_bp = Blueprint('citation', __name__)


@citation_bp.route('/citation/<int:doc_id>')
def citation(doc_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()

    # ---------- 合并查询：一次查出 Title 和 UploadUserID ----------
    cursor.execute("""
        SELECT DocumentID, Title, UploadUserID
        FROM Documents
        WHERE DocumentID = %s
    """, (doc_id,))
    doc = cursor.fetchone()

    if not doc:
        return render_template('error.html', message='文献不存在')

    doc_id_db, title, upload_user_id = doc[0], doc[1], doc[2]

    # 权限校验：只有上传者才能设置引用关系
    if upload_user_id != session['user_id']:
        return render_template('error.html', message='你没有权限设置此文献的引用关系')

    # 查询这篇文献已经引用了哪些文献（已选中的）
    cursor.execute("""
        SELECT TargetDocumentID FROM Citation
        WHERE SourceDocumentID = %s
    """, (doc_id,))
    selected_ids = [row[0] for row in cursor.fetchall()]

    return render_template(
        'citation.html',
        current_doc={'DocumentID': doc_id_db, 'Title': title},
        selected_ids=selected_ids
    )


@citation_bp.route('/search_citation')
def search_citation():
    if 'user_id' not in session:
        return jsonify([])

    keyword = request.args.get('keyword', '').strip()
    doc_id = request.args.get('doc_id', type=int)

    if not keyword:
        return jsonify([])

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DocumentID, Title, Author
        FROM Documents
        WHERE Title LIKE %s
        AND DocumentID != %s
        ORDER BY DocumentID DESC
        LIMIT 20
    """, ('%' + keyword + '%', doc_id))
    rows = cursor.fetchall()

    results = [
        {
            'DocumentID': row[0],
            'Title': row[1],
            'Author': row[2]
        }
        for row in rows
    ]
    return jsonify(results)


@citation_bp.route('/save_citation/<int:doc_id>', methods=['POST'])
def save_citation(doc_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT UploadUserID FROM Documents WHERE DocumentID = %s
    """, (doc_id,))
    doc = cursor.fetchone()

    if not doc or doc[0] != session['user_id']:
        return render_template('error.html', message='你没有权限修改此文献的引用关系')

    target_ids = request.form.getlist('target_doc_ids')

    if target_ids:
        target_ids_int = []
        for tid in target_ids:
            try:
                target_ids_int.append(int(tid))
            except ValueError:
                return render_template('error.html', message='无效的文献ID格式')

        placeholders = ','.join('%s' for _ in target_ids_int)
        cursor.execute(f"SELECT DocumentID FROM Documents WHERE DocumentID IN ({placeholders})", target_ids_int)
        existing_ids = {row[0] for row in cursor.fetchall()}
        invalid_ids = set(target_ids_int) - existing_ids
        if invalid_ids:
            return render_template('error.html', message=f'以下文献不存在，无法建立引用关系：{list(invalid_ids)}')
        target_ids = target_ids_int
    else:
        target_ids = []

    try:
        cursor.execute("""
            DELETE FROM Citation WHERE SourceDocumentID = %s
        """, (doc_id,))

        for target_id in target_ids:
            if target_id == doc_id:
                continue
            cursor.execute("""
                INSERT INTO Citation (SourceDocumentID, TargetDocumentID)
                VALUES (%s, %s)
            """, (doc_id, target_id))

        conn.commit()
    except Exception as e:
        conn.rollback()
        return render_template('error.html', message=f'保存失败：{str(e)}')

    return redirect('/my_documents')
