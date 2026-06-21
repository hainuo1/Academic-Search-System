# ============================================================
# routes/document.py —— 文献操作模块
# ============================================================

import os
import uuid
import pdfplumber
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    send_file,
    current_app,
    url_for,
    flash
)
from db import get_connection
from utils import process_keywords   # 导入工具函数

document_bp = Blueprint('document', __name__)


@document_bp.route('/document/<int:doc_id>')
def document_detail(doc_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DocumentID, Title, Author, Abstract,
               PublishDate, Category, FilePath,
               ViewCount, DownloadCount
        FROM Documents
        WHERE DocumentID = ?
    """, (doc_id,))
    document = cursor.fetchone()

    if not document:
        return render_template('error.html', message='文献不存在')

    cursor.execute("UPDATE Documents SET ViewCount = ViewCount + 1 WHERE DocumentID = ?", (doc_id,))
    conn.commit()

    try:
        cursor.execute("""
            INSERT INTO BrowseHistory (UserID, DocumentID, ViewTime)
            VALUES (?, ?, GETDATE())
        """, (session['user_id'], doc_id))
        conn.commit()
    except Exception as e:
        print(f"浏览历史记录失败：{e}")

    cursor.execute("""
        SELECT k.KeywordName
        FROM Keywords k
        INNER JOIN DocumentKeyword dk ON k.KeywordID = dk.KeywordID
        WHERE dk.DocumentID = ?
    """, (doc_id,))
    keywords = cursor.fetchall()

    cursor.execute("""
        SELECT d.DocumentID, d.Title
        FROM Citation c
        INNER JOIN Documents d ON c.SourceDocumentID = d.DocumentID
        WHERE c.TargetDocumentID = ?
    """, (doc_id,))
    citations = cursor.fetchall()
    citation_count = len(citations)

    cursor.execute("""
        SELECT FavoriteID FROM Favorites
        WHERE UserID = ? AND DocumentID = ?
    """, (session['user_id'], doc_id))
    is_favorited = cursor.fetchone() is not None

    return render_template(
        'document.html',
        document=document,
        keywords=keywords,
        citations=citations,
        citation_count=citation_count,
        is_favorited=is_favorited
    )


@document_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'GET':
        return render_template('upload.html')

    title = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    category = request.form.get('category', '').strip()
    publish_date = request.form.get('publish_date', '').strip()
    keywords_raw = request.form.get('keywords', '').strip()
    abstract = request.form.get('abstract', '').strip()
    pdf_file = request.files.get('pdf_file')

    if not all([title, author, category, publish_date, keywords_raw, abstract]):
        return render_template('upload.html', error='所有字段都必须填写')
    if not pdf_file or pdf_file.filename == '':
        return render_template('upload.html', error='请选择要上传的 PDF 文件')
    if not pdf_file.filename.lower().endswith('.pdf'):
        return render_template('upload.html', error='只允许上传 PDF 格式的文件')

    unique_filename = str(uuid.uuid4()) + '.pdf'
    upload_folder = current_app.config['UPLOAD_FOLDER']
    save_path = os.path.join(upload_folder, unique_filename)
    pdf_file.save(save_path)

    full_text = ""
    extract_error = None
    try:
        with pdfplumber.open(save_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        full_text = full_text.strip()
    except Exception as e:
        extract_error = str(e)
        full_text = ""

    file_path = os.path.join('uploads', unique_filename)
    keywords_list = [k.strip() for k in keywords_raw.split(';') if k.strip()]
    keywords_text = ';'.join(keywords_list)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO Documents
                (Title, Author, Abstract, PublishDate, Category,
                 FilePath, UploadUserID, KeywordsText, FullText)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, author, abstract, publish_date, category,
              file_path, session['user_id'], keywords_text, full_text))

        cursor.execute("SELECT SCOPE_IDENTITY()")
        doc_id = int(cursor.fetchone()[0])

        # 处理关键词（使用公共函数）
        process_keywords(cursor, doc_id, keywords_list)

        conn.commit()
    except Exception as e:
        conn.rollback()
        if os.path.exists(save_path):
            os.remove(save_path)
        return render_template('upload.html', error=f'上传失败：{str(e)}')

    if extract_error:
        flash(f'文献上传成功，但PDF全文提取失败（{extract_error}），该文献无法通过全文搜索找到。', 'warning')

    return redirect(f'/document/{doc_id}')


@document_bp.route('/download/<int:doc_id>')
def download(doc_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT FilePath, Title FROM Documents WHERE DocumentID = ?", (doc_id,))
    doc = cursor.fetchone()

    if not doc:
        return render_template('error.html', message='文献不存在')

    cursor.execute("UPDATE Documents SET DownloadCount = DownloadCount + 1 WHERE DocumentID = ?", (doc_id,))
    conn.commit()

    absolute_path = os.path.join(current_app.root_path, doc[0])
    if not os.path.exists(absolute_path):
        return render_template('error.html', message='文件不存在，可能已被删除')

    return send_file(
        absolute_path,
        as_attachment=True,
        download_name=f"{doc[1]}.pdf"
    )


@document_bp.route('/my_documents')
def my_documents():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DocumentID, Title, Author, PublishDate, Category
        FROM Documents
        WHERE UploadUserID = ?
        ORDER BY UploadTime DESC
    """, (session['user_id'],))
    my_docs = cursor.fetchall()

    return render_template('my_documents.html', my_docs=my_docs)


@document_bp.route('/delete_document/<int:doc_id>')
def delete_document(doc_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT UploadUserID, FilePath FROM Documents WHERE DocumentID = ?", (doc_id,))
    doc = cursor.fetchone()

    if not doc:
        return render_template('error.html', message='文献不存在')
    if doc[0] != session['user_id']:
        return render_template('error.html', message='你没有权限删除这篇文献')

    absolute_path = os.path.join(current_app.root_path, doc[1])

    try:
        cursor.execute("DELETE FROM Citation WHERE SourceDocumentID = ?", (doc_id,))
        cursor.execute("DELETE FROM Citation WHERE TargetDocumentID = ?", (doc_id,))
        cursor.execute("DELETE FROM Favorites WHERE DocumentID = ?", (doc_id,))
        cursor.execute("DELETE FROM DocumentKeyword WHERE DocumentID = ?", (doc_id,))
        cursor.execute("DELETE FROM Documents WHERE DocumentID = ?", (doc_id,))

        # ---------- 清理孤立关键词 ----------
        cursor.execute("""
            DELETE FROM Keywords WHERE KeywordID NOT IN (
                SELECT DISTINCT KeywordID FROM DocumentKeyword
            )
        """)

        conn.commit()

        if os.path.exists(absolute_path):
            os.remove(absolute_path)

    except Exception as e:
        conn.rollback()
        return render_template('error.html', message=f'删除失败：{str(e)}')

    return redirect('/my_documents')


@document_bp.route('/edit_document/<int:doc_id>', methods=['GET', 'POST'])
def edit_document(doc_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT UploadUserID FROM Documents WHERE DocumentID = ?", (doc_id,))
    doc_check = cursor.fetchone()

    if not doc_check:
        return render_template('error.html', message='文献不存在')
    if doc_check[0] != session['user_id']:
        return render_template('error.html', message='你没有权限编辑此文献')

    if request.method == 'GET':
        cursor.execute("""
            SELECT DocumentID, Title, Author, Abstract,
                   PublishDate, Category, KeywordsText
            FROM Documents
            WHERE DocumentID = ?
        """, (doc_id,))
        doc = cursor.fetchone()
        if not doc:
            return render_template('error.html', message='文献不存在')
        return render_template('edit_document.html', doc=doc)

    title = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    category = request.form.get('category', '').strip()
    publish_date = request.form.get('publish_date', '').strip()
    keywords_raw = request.form.get('keywords', '').strip()
    abstract = request.form.get('abstract', '').strip()

    if not all([title, author, category, publish_date, keywords_raw, abstract]):
        return render_template('edit_document.html', error='所有字段都必须填写', doc=request.form)

    keywords_list = [k.strip() for k in keywords_raw.split(';') if k.strip()]
    if not keywords_list:
        return render_template('edit_document.html', error='至少需要填写一个关键词', doc=request.form)

    keywords_text = ';'.join(keywords_list)

    try:
        cursor.execute("""
            UPDATE Documents
            SET Title = ?, Author = ?, Abstract = ?,
                PublishDate = ?, Category = ?, KeywordsText = ?
            WHERE DocumentID = ?
        """, (title, author, abstract, publish_date, category, keywords_text, doc_id))

        # 删除旧的关键词关联
        cursor.execute("DELETE FROM DocumentKeyword WHERE DocumentID = ?", (doc_id,))

        # 处理关键词（使用公共函数）
        process_keywords(cursor, doc_id, keywords_list)

        conn.commit()
    except Exception as e:
        conn.rollback()
        return render_template('edit_document.html', error=f'保存失败：{str(e)}', doc=request.form)

    return redirect(url_for('document.my_documents'))