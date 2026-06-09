import pyodbc

def get_db_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=destiny;"
        "DATABASE=AcademicSearchDB;"
        "Trusted_Connection=yes;"
    )

def search_by_title(keyword):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DocumentID, Title, Author, Category FROM Documents WHERE Title LIKE ?", f"%{keyword}%")
    rows = cursor.fetchall()
    conn.close()
    return rows

def search_by_author(author):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DocumentID, Title, Author, Category FROM Documents WHERE Author LIKE ?", f"%{author}%")
    rows = cursor.fetchall()
    conn.close()
    return rows

def search_by_category(category):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DocumentID, Title, Author, Category FROM Documents WHERE Category LIKE ?", f"%{category}%")
    rows = cursor.fetchall()
    conn.close()
    return rows

def login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT UserID FROM Users WHERE UserName=? AND Password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def register(username, password, email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Users (UserName, Password, Email) VALUES (?, ?, ?)", (username, password, email))
    conn.commit()
    conn.close()

def search_by_keyword(keyword):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.DocumentID, d.Title, d.Author, k.KeywordName, dk.TF_IDF
        FROM Documents d
        INNER JOIN DocumentKeyword dk ON d.DocumentID = dk.DocumentID
        INNER JOIN Keywords k ON dk.KeywordID = k.KeywordID
        WHERE k.KeywordName LIKE ?
        ORDER BY dk.TF_IDF DESC
    """, f"%{keyword}%")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_citation(document_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d1.Title, d2.Title
        FROM Citation c
        INNER JOIN Documents d1 ON c.SourceDocumentID=d1.DocumentID
        INNER JOIN Documents d2 ON c.TargetDocumentID=d2.DocumentID
        WHERE c.SourceDocumentID=?
    """, document_id)
    rows = cursor.fetchall()
    conn.close()
    return rows

def save_search_history(user_id, keyword):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO SearchHistory (UserID, SearchKeyword) VALUES (?, ?)", (user_id, keyword))
    conn.commit()
    conn.close()

def get_search_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SearchKeyword, SearchTime FROM SearchHistory WHERE UserID=? ORDER BY SearchTime DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_statistics():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Users")
    user_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Documents")
    document_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Keywords")
    keyword_count = cursor.fetchone()[0]
    conn.close()
    return user_count, document_count, keyword_count

def show_menu():
    print("\n==============================")
    print(" 学术文献检索系统")
    print("==============================")
    print("1. 标题检索")
    print("2. 作者检索")
    print("3. 分类检索")
    print("0. 退出系统")
    print("==============================")

show_menu()
choice = input("请选择功能：")
if choice == "1":
    keyword = input("请输入标题关键词：")
    result = search_by_title(keyword)
    for doc in result:
        print("\n文献编号：", doc[0])
        print("标题：", doc[1])
        print("作者：", doc[2])
        print("分类：", doc[3])
elif choice == "2":
    author = input("请输入作者姓名：")
    result = search_by_author(author)
    for doc in result:
        print("\n文献编号：", doc[0])
        print("标题：", doc[1])
        print("作者：", doc[2])
        print("分类：", doc[3])
elif choice == "3":
    category = input("请输入分类名称：")
    result = search_by_category(category)
    for doc in result:
        print("\n文献编号：", doc[0])
        print("标题：", doc[1])
        print("作者：", doc[2])
        print("分类：", doc[3])
elif choice == "0":
    print("系统已退出")
else:
    print("输入错误")