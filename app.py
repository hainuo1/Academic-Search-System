from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    send_file,
    jsonify
)
import pyodbc
import os
import uuid
import re

app = Flask(__name__)
app.secret_key = "academic_search_system_2026"
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 限制单个上传文件最大为50MB
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

def get_connection():
    return pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=destiny;'
        'DATABASE=AcademicSearchDB;'
        'Trusted_Connection=yes;'
    )

# =========================
# 首页
# =========================
@app.route('/')
def home():
    return render_template('index.html')

# =========================
# 登录
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT UserID, UserName
            FROM Users
            WHERE UserName = ? AND Password = ?
        """, (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user_id'] = user.UserID
            session['username'] = user.UserName
            return redirect('/search')
        return render_template('login.html', error="用户名或密码错误")
    return render_template('login.html')

# =========================
# 忘记密码
# =========================
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html')
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    email = request.form.get('email')
    # 验证
    if len(username) < 2 or len(username) > 20:
        return render_template('forgot_password.html', error='用户名必须2-20位')
    if len(password) < 8 or len(password) > 50:
        return render_template('forgot_password.html', error='密码必须8-50位')
    if password != confirm_password:
        return render_template('forgot_password.html', error='两次输入的密码不一致')
    email_pattern = r'^[^@]+@[^@]+\.[^@]+$'
    if not re.match(email_pattern, email):
        return render_template('forgot_password.html', error='邮箱格式不正确')
    # 查询用户
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT UserID FROM Users WHERE UserName = ? AND Email = ?
    """, (username, email))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return render_template('forgot_password.html', error='用户名与邮箱不匹配')
    cursor.execute("""
        UPDATE Users SET Password = ? WHERE UserName = ? AND Email = ?
    """, (password, username, email))
    conn.commit()
    conn.close()
    return render_template(
        'forgot_password.html',
        success='密码修改成功，请返回登录'
    )

# =========================
# 注册
# =========================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        # 验证
        if len(username) < 2 or len(username) > 20:
            return render_template('register.html', error='用户名必须2-20位')
        if len(password) < 8 or len(password) > 50:
            return render_template('register.html', error='密码必须8-50位')
        if ' ' in password:
            return render_template('register.html', error='密码不能包含空格')
        email_pattern = r'^[^@]+@[^@]+\.[^@]+$'
        if not re.match(email_pattern, email):
            return render_template('register.html', error='邮箱格式不正确')
        if password != confirm_password:
            return render_template('register.html', error='两次输入的密码不一致')
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT UserID FROM Users
            WHERE UserName = ? OR Email = ?
        """, (username, email))
        if cursor.fetchone():
            conn.close()
            return render_template('register.html', error='用户名或邮箱已存在')
        cursor.execute("""
            INSERT INTO Users (UserName, Password, Email)
            VALUES (?, ?, ?)
        """, (username, password, email))
        conn.commit()
        conn.close()
        return redirect('/login')
    return render_template('register.html')

# =========================
# 搜索
# =========================
@app.route('/search')
def search():
    if 'user_id' not in session:
        return redirect('/login')
    # 获取全局搜索参数（顶部搜索栏）
    keyword = request.args.get('keyword', '').strip()
    search_type = request.args.get('search_type', 'title').strip()
    # 获取高级组合筛选参数
    title_filter = request.args.get('title', '').strip()
    author_filter = request.args.get('author', '').strip()
    category_filter = request.args.get('category', '').strip()
    keyword_filter = request.args.get('keyword_filter', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    # 分页参数
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except:
        page = 1
    page_size = 10
    offset = (page - 1) * page_size
    results = []
    total_count = 0
    total_pages = 0
    # 构建通用筛选条件（适用于所有搜索类型）
    common_conditions = []
    common_params = []
    if title_filter:
        common_conditions.append("d.Title LIKE ?")
        common_params.append('%' + title_filter + '%')
    if author_filter:
        common_conditions.append("d.Author LIKE ?")
        common_params.append('%' + author_filter + '%')
    if category_filter:
        common_conditions.append("d.Category LIKE ?")
        common_params.append('%' + category_filter + '%')
    if start_date:
        common_conditions.append("d.PublishDate >= ?")
        common_params.append(start_date)
    if end_date:
        common_conditions.append("d.PublishDate <= ?")
        common_params.append(end_date)
    # 关键词筛选特殊处理（需要关联DocumentKeyword和Keywords表）
    keyword_condition = ""
    keyword_params = []
    if keyword_filter:
        keyword_condition = " AND k.KeywordName LIKE ?"
        keyword_params.append('%' + keyword_filter + '%')
    # 拼接通用条件SQL
    common_condition_sql = ""
    if common_conditions:
        common_condition_sql = " AND " + " AND ".join(common_conditions)
    if keyword:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # 插入搜索历史
            cursor.execute("""
                INSERT INTO SearchHistory
                (UserID, SearchKeyword, SearchTime)
                VALUES (?, ?, GETDATE())
            """, (session['user_id'], keyword))
            # 保留最多100条历史记录
            cursor.execute("""
                DELETE FROM SearchHistory 
                WHERE UserID = ? 
                AND HistoryID NOT IN (
                    SELECT TOP 100 HistoryID 
                    FROM SearchHistory 
                    WHERE UserID = ? 
                    ORDER BY SearchTime DESC
                )
            """, (session['user_id'], session['user_id']))
            if search_type == "keyword":
                # 关键词搜索（关联三个表）
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM Documents d
                    INNER JOIN DocumentKeyword dk ON d.DocumentID = dk.DocumentID
                    INNER JOIN Keywords k ON dk.KeywordID = k.KeywordID
                    WHERE k.KeywordName = ?
                    """ + common_condition_sql + keyword_condition,
                               (keyword,) + tuple(common_params) + tuple(keyword_params))
                total_count = cursor.fetchone()[0]
                total_pages = (total_count + page_size - 1) // page_size
                cursor.execute("""
                    SELECT
                        d.DocumentID,
                        d.Title,
                        d.Author,
                        d.Category,
                        dk.TF_IDF,
                        CONVERT(VARCHAR(10), d.PublishDate, 23) AS PublishDate
                    FROM Documents d
                    INNER JOIN DocumentKeyword dk ON d.DocumentID = dk.DocumentID
                    INNER JOIN Keywords k ON dk.KeywordID = k.KeywordID
                    WHERE k.KeywordName = ?
                    """ + common_condition_sql + keyword_condition + """
                    ORDER BY dk.TF_IDF DESC
                    OFFSET ? ROWS
                    FETCH NEXT ? ROWS ONLY
                """, (keyword,) + tuple(common_params) + tuple(keyword_params) + (offset, page_size))
            elif search_type == "author":
                # 作者搜索
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM Documents d
                    WHERE Author LIKE ?
                    """ + common_condition_sql,
                               ('%' + keyword + '%',) + tuple(common_params))
                total_count = cursor.fetchone()[0]
                total_pages = (total_count + page_size - 1) // page_size
                cursor.execute("""
                    SELECT
                        DocumentID,
                        Title,
                        Author,
                        Category,
                        CAST(NULL AS FLOAT) AS TF_IDF,
                        CONVERT(VARCHAR(10), PublishDate, 23) AS PublishDate
                    FROM Documents d
                    WHERE Author LIKE ?
                    """ + common_condition_sql + """
                    ORDER BY PublishDate DESC
                    OFFSET ? ROWS
                    FETCH NEXT ? ROWS ONLY
                """, ('%' + keyword + '%',) + tuple(common_params) + (offset, page_size))
            elif search_type == "category":
                # 分类搜索
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM Documents d
                    WHERE Category LIKE ?
                    """ + common_condition_sql,
                               ('%' + keyword + '%',) + tuple(common_params))
                total_count = cursor.fetchone()[0]
                total_pages = (total_count + page_size - 1) // page_size
                cursor.execute("""
                    SELECT
                        DocumentID,
                        Title,
                        Author,
                        Category,
                        CAST(NULL AS FLOAT) AS TF_IDF,
                        CONVERT(VARCHAR(10), PublishDate, 23) AS PublishDate
                    FROM Documents d
                    WHERE Category LIKE ?
                    """ + common_condition_sql + """
                    ORDER BY PublishDate DESC
                    OFFSET ? ROWS
                    FETCH NEXT ? ROWS ONLY
                """, ('%' + keyword + '%',) + tuple(common_params) + (offset, page_size))
            else:
                # 标题搜索（默认）
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM Documents d
                    WHERE Title LIKE ?
                    """ + common_condition_sql,
                               ('%' + keyword + '%',) + tuple(common_params))
                total_count = cursor.fetchone()[0]
                total_pages = (total_count + page_size - 1) // page_size
                cursor.execute("""
                    SELECT
                        DocumentID,
                        Title,
                        Author,
                        Category,
                        NULL,
                        CONVERT(VARCHAR(10), PublishDate, 23) AS PublishDate
                    FROM Documents d
                    WHERE Title LIKE ?
                    """ + common_condition_sql + """
                    ORDER BY PublishDate DESC
                    OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
                """, ('%' + keyword + '%',) + tuple(common_params) + (offset, page_size))
            results = cursor.fetchall()
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
        finally:
            conn.close()
    return render_template(
        'search.html',
        results=results,
        keyword=keyword,
        search_type=search_type,
        page=page,
        total_pages=total_pages,
        total_count=total_count,
        username=session.get('username')
    )

# =========================
# 上传
# =========================
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'GET':
        return render_template('upload.html')
    try:
        pdf_file = request.files['pdf_file']
        if not pdf_file.filename.lower().endswith('.pdf'):
            return render_template('error.html', message='仅允许PDF文件')
        title = request.form['title']
        author = request.form['author']
        category = request.form['category']
        abstract = request.form['abstract']
        publish_date = request.form['publish_date']
        keywords_text = request.form['keywords']
        file_name = str(uuid.uuid4()) + '.pdf'
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        pdf_file.save(save_path)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Documents
            (Title, Author, Abstract, PublishDate, Category, FilePath, UploadUserID, KeywordsText, UploadTime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
        """, (title, author, abstract, publish_date, category, save_path, session['user_id'], keywords_text))
        # 获取新插入文档的自增ID
        cursor.execute("SELECT @@IDENTITY")
        document_id = cursor.fetchone()[0]
        # 处理关键词，同步到关联表
        keywords = [k.strip() for k in keywords_text.split(';') if k.strip()]
        for kw in keywords:
            cursor.execute("SELECT KeywordID FROM Keywords WHERE KeywordName = ?", (kw,))
            kw_row = cursor.fetchone()
            if kw_row:
                kw_id = kw_row[0]
            else:
                cursor.execute("INSERT INTO Keywords (KeywordName) VALUES (?)", (kw,))
                cursor.execute("SELECT @@IDENTITY")
                kw_id = cursor.fetchone()[0]
            # 建立关联
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM DocumentKeyword WHERE DocumentID = ? AND KeywordID = ?)
                BEGIN
                    INSERT INTO DocumentKeyword (DocumentID, KeywordID, TF_IDF)
                    VALUES (?, ?, 1.0)
                END
            """, (document_id, kw_id, document_id, kw_id))
        conn.commit()
        conn.close()
        return redirect(f'/document/{document_id}')
    except Exception as e:
        return render_template('error.html', message=str(e))

# =========================
# 下载
# =========================
@app.route('/download/<int:doc_id>')
def download_document(doc_id):
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT FilePath
        FROM Documents
        WHERE DocumentID = ?
    """, (doc_id,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        return render_template('error.html', message='文献不存在')
    file_path = result[0]
    if not file_path:
        return render_template('error.html', message='文件不存在')
    absolute_path = os.path.join(app.root_path, file_path)
    if not os.path.exists(absolute_path):
        return render_template('error.html', message='服务器未找到文件')
    return send_file(absolute_path, as_attachment=True)

# =========================
# 详情页
# =========================
@app.route('/document/<int:doc_id>')
def document_detail(doc_id):
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DocumentID, Title, Author, Category, PublishDate, Abstract, KeywordsText
        FROM Documents
        WHERE DocumentID = ?
    """, (doc_id,))
    document = cursor.fetchone()
    cursor.execute("""
        SELECT
            d.DocumentID,
            d.Title
        FROM Citation c
        JOIN Documents d
        ON c.SourceDocumentID = d.DocumentID
        WHERE c.TargetDocumentID = ?
    """, (doc_id,))
    citations = cursor.fetchall()
    cursor.execute("""
        SELECT COUNT(*)
        FROM Citation
        WHERE TargetDocumentID = ?
    """, (doc_id,))
    citation_count = cursor.fetchone()[0]
    cursor.execute("""
        SELECT
            k.KeywordName,
            dk.TF_IDF
        FROM DocumentKeyword dk
        JOIN Keywords k
        ON dk.KeywordID = k.KeywordID
        WHERE dk.DocumentID = ?
        ORDER BY dk.TF_IDF DESC
    """, (doc_id,))
    keywords = cursor.fetchall()
    # 查询当前用户是否已收藏该文档
    cursor.execute("SELECT FavoriteID FROM Favorites WHERE UserID = ? AND DocumentID = ?", (session['user_id'], doc_id))
    is_favorited = cursor.fetchone() is not None
    conn.close()
    return render_template('document.html', document=document, citations=citations, citation_count=citation_count,
                           keywords=keywords, is_favorited=is_favorited)

# =========================
# 个人检索历史
# =========================
@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect('/login')
    # 分页参数处理，与搜索页保持一致
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except:
        page = 1
    page_size = 10  # 每页10条，与搜索页统一
    offset = (page - 1) * page_size
    conn = get_connection()
    cursor = conn.cursor()
    # 1. 查询总记录数，用于计算总页数
    cursor.execute("""
        SELECT COUNT(*)
        FROM SearchHistory
        WHERE UserID = ?
    """, (session['user_id'],))
    total_count = cursor.fetchone()[0]
    total_pages = (total_count + page_size - 1) // page_size
    # 2. 分页查询当前页的历史记录
    cursor.execute("""
        SELECT SearchKeyword, SearchTime
        FROM SearchHistory
        WHERE UserID = ?
        ORDER BY SearchTime DESC
        OFFSET ? ROWS
        FETCH NEXT ? ROWS ONLY
    """, (session['user_id'], offset, page_size))
    histories = cursor.fetchall()
    conn.close()
    return render_template(
        'history.html',
        histories=histories,
        total_count=total_count,  # 总记录数
        page=page,                # 当前页码
        total_pages=total_pages,  # 总页数
        username=session.get('username')
    )

# =========================
# 系统数据统计
# =========================
@app.route('/stats')
def stats():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP 10
            SearchKeyword,
            COUNT(*) AS cnt
        FROM SearchHistory
        GROUP BY SearchKeyword
        ORDER BY cnt DESC
    """)
    keyword_rank = cursor.fetchall()
    cursor.execute("""
        SELECT TOP 10
            u.UserName,
            COUNT(*) AS cnt
        FROM SearchHistory h
        JOIN Users u ON h.UserID = u.UserID
        GROUP BY u.UserID, u.UserName
        ORDER BY cnt DESC
    """)
    user_rank = cursor.fetchall()
    cursor.execute("""
        SELECT TOP 10
            d.Title,
            COUNT(*) AS cnt
        FROM Citation c
        JOIN Documents d ON c.TargetDocumentID = d.DocumentID
        GROUP BY d.Title
        ORDER BY cnt DESC
    """)
    citation_rank = cursor.fetchall()
    conn.close()
    return render_template(
        'stats.html',
        keyword_rank=keyword_rank,
        user_rank=user_rank,
        citation_rank=citation_rank,
        username=session.get('username')
    )

# =========================
# 退出
# =========================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# =========================
# 错误处理
# =========================
@app.errorhandler(413)
def too_large(e):
    return render_template('error.html', message='文件过大，单个文件最大支持50MB'), 413

# =========================
# 我的论文与引用设置
# =========================
@app.route('/my_documents')
def my_documents():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            DocumentID,
            Title,
            Author,
            CONVERT(VARCHAR(10), PublishDate, 23)
        FROM Documents
        WHERE UploadUserID = ?
        ORDER BY UploadTime DESC
    """, (session['user_id'],))
    my_docs = cursor.fetchall()
    conn.close()
    return render_template(
        'my_documents.html',
        my_docs=my_docs,
        username=session.get('username')
    )

@app.route('/citation/<int:doc_id>')
def citation(doc_id):
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            DocumentID,
            Title
        FROM Documents
        WHERE DocumentID = ?
    """, (doc_id,))
    current_doc = cursor.fetchone()
    if not current_doc:
        conn.close()
        return render_template(
            'error.html',
            message='文献不存在'
        )
    cursor.execute("""
        SELECT TargetDocumentID
        FROM Citation
        WHERE SourceDocumentID = ?
    """, (doc_id,))
    selected_ids = [
        row[0]
        for row in cursor.fetchall()
    ]
    conn.close()
    return render_template(
        'citation.html',
        current_doc=current_doc,
        selected_ids=selected_ids,
        username=session.get('username')
    )

@app.route('/search_citation')
def search_citation():
    if 'user_id' not in session:
        return []
    keyword = request.args.get(
        'keyword',
        ''
    ).strip()
    doc_id = request.args.get(
        'doc_id'
    )
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP 30
            DocumentID,
            Title,
            Author
        FROM Documents
        WHERE Title LIKE ?
        AND DocumentID <> ?
        ORDER BY PublishDate DESC
    """, (
        '%' + keyword + '%',
        doc_id
    ))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        result.append({
            "DocumentID": row[0],
            "Title": row[1],
            "Author": row[2]
        })
    return jsonify(result)

@app.route(
    '/save_citation/<int:doc_id>',
    methods=['POST']
)
def save_citation(doc_id):
    if 'user_id' not in session:
        return redirect('/login')
    target_ids = request.form.getlist(
        'target_doc_ids'
    )
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM Citation
        WHERE SourceDocumentID = ?
    """, (doc_id,))
    for target_id in target_ids:
        if int(target_id) == doc_id:
            continue
        cursor.execute("""
            INSERT INTO Citation
            (
                SourceDocumentID,
                TargetDocumentID
            )
            VALUES
            (?, ?)
        """, (
            doc_id,
            target_id
        ))
    conn.commit()
    conn.close()
    return redirect('/my_documents')

# 删除自己上传的文献
@app.route('/delete_document/<int:doc_id>')
def delete_document(doc_id):
    if 'user_id' not in session:
        return redirect('/login')
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # 权限校验：只能删除自己上传的文献
        cursor.execute("SELECT UploadUserID, FilePath FROM Documents WHERE DocumentID = ?", (doc_id,))
        doc = cursor.fetchone()
        if not doc or doc[0] != session['user_id']:
            conn.close()
            return render_template('error.html', message='你没有权限删除这篇文献')
        # 删除服务器上的PDF文件
        file_path = doc[1]
        absolute_path = os.path.join(app.root_path, file_path)
        if os.path.exists(absolute_path):
            os.remove(absolute_path)
        # 删除数据库记录，外键级联自动清理所有关联数据
        cursor.execute("DELETE FROM Documents WHERE DocumentID = ?", (doc_id,))
        conn.commit()
        conn.close()
        return redirect('/my_documents')
    except Exception as e:
        return render_template('error.html', message=str(e))

# =========================
# 个人信息
# =========================
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_connection()
    cursor = conn.cursor()
    # 查询当前用户信息
    cursor.execute("""
        SELECT UserName, Email
        FROM Users
        WHERE UserID = ?
    """, (session['user_id'],))
    user = cursor.fetchone()
    username = user[0]
    email = user[1]
    error = None
    success = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'change_email':
            # 修改邮箱逻辑：需要验证账号+当前密码
            current_password = request.form.get('current_password')
            new_email = request.form.get('new_email')
            confirm_new_email = request.form.get('confirm_new_email')
            # 验证
            if new_email != confirm_new_email:
                error = '两次输入的新邮箱不一致'
            elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', new_email):
                error = '邮箱格式不正确'
            else:
                # 验证账号+密码
                cursor.execute("""
                    SELECT UserID FROM Users
                    WHERE UserName = ? AND Password = ?
                """, (username, current_password))
                if not cursor.fetchone():
                    error = '当前密码错误，验证失败'
                else:
                    # 检查新邮箱是否已被使用
                    cursor.execute("""
                        SELECT UserID FROM Users WHERE Email = ?
                    """, (new_email,))
                    if cursor.fetchone():
                        error = '该邮箱已被其他账号绑定'
                    else:
                        # 更新邮箱
                        cursor.execute("""
                            UPDATE Users SET Email = ? WHERE UserID = ?
                        """, (new_email, session['user_id']))
                        conn.commit()
                        success = '邮箱修改成功！'
                        email = new_email
        elif action == 'change_password':
            # 修改密码逻辑：需要验证账号+当前邮箱
            current_email = request.form.get('current_email')
            new_password = request.form.get('new_password')
            confirm_new_password = request.form.get('confirm_new_password')
            # 验证
            if new_password != confirm_new_password:
                error = '两次输入的新密码不一致'
            elif len(new_password) < 8 or len(new_password) > 50:
                error = '密码必须8-50位'
            elif ' ' in new_password:
                error = '密码不能包含空格'
            else:
                # 验证账号+邮箱
                cursor.execute("""
                    SELECT UserID FROM Users
                    WHERE UserName = ? AND Email = ?
                """, (username, current_email))
                if not cursor.fetchone():
                    error = '当前邮箱错误，验证失败'
                else:
                    # 更新密码
                    cursor.execute("""
                        UPDATE Users SET Password = ? WHERE UserID = ?
                    """, (new_password, session['user_id']))
                    conn.commit()
                    success = '密码修改成功！'
    # 脱敏处理账号和邮箱，隐藏敏感信息
    if len(username) <= 2:
        masked_username = '*' * len(username)
    else:
        masked_username = username[0] + '*' * (len(username)-2) + username[-1]
    local_part, domain_part = email.split('@')
    masked_local = local_part[0] + '*' * (len(local_part)-1)
    if len(domain_part) <= 2:
        masked_domain = '*' * len(domain_part)
    else:
        masked_domain = domain_part[0] + '*' * (len(domain_part)-2) + domain_part[-1]
    masked_email = masked_local + '@' + masked_domain
    conn.close()
    return render_template(
        'profile.html',
        masked_username=masked_username,
        masked_email=masked_email,
        error=error,
        success=success,
        username=session.get('username')
    )

# =========================
# 收藏功能
# =========================
@app.route('/favorites')
def favorites():
    if 'user_id' not in session:
        return redirect('/login')
    # 分页参数，和历史的分页完全一样
    page = request.args.get('page', 1, type=int)
    per_page = 10
    user_id = session['user_id']
    conn = get_connection()
    cursor = conn.cursor()
    # 先查总记录数，算总页数
    cursor.execute("""
        SELECT COUNT(*) FROM Favorites WHERE UserID = ?
    """, (user_id,))
    total_count = cursor.fetchone()[0]
    total_pages = (total_count + per_page - 1) // per_page
    # 分页查询用户的收藏，按收藏时间倒序，最新的在前面
    cursor.execute("""
        SELECT d.DocumentID, d.Title, d.Author, d.PublishDate
        FROM Favorites f
        JOIN Documents d ON f.DocumentID = d.DocumentID
        WHERE f.UserID = ?
        ORDER BY f.CreateTime DESC
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """, (user_id, (page - 1) * per_page, per_page))
    documents = cursor.fetchall()
    conn.close()
    return render_template(
        'favorites.html',
        documents=documents,
        total_count=total_count,
        page=page,
        total_pages=total_pages
    )

# 异步的收藏/取消收藏接口
@app.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': '未登录'})
    data = request.get_json()
    doc_id = data.get('document_id')
    user_id = session['user_id']
    conn = get_connection()
    cursor = conn.cursor()
    # 检查用户有没有已经收藏这篇
    cursor.execute("""
        SELECT FavoriteID FROM Favorites WHERE UserID = ? AND DocumentID = ?
    """, (user_id, doc_id))
    exists = cursor.fetchone()
    if exists:
        # 已经收藏了，就取消收藏
        cursor.execute("""
            DELETE FROM Favorites WHERE FavoriteID = ?
        """, (exists[0],))
        is_favorited = False
    else:
        # 没收藏，就新增收藏
        cursor.execute("""
            INSERT INTO Favorites (UserID, DocumentID) VALUES (?, ?)
        """, (user_id, doc_id))
        is_favorited = True
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'is_favorited': is_favorited})

if __name__ == '__main__':
    app.run(debug=True)