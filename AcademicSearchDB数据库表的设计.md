# AcademicSearchDB 数据字典

## 1. Users（用户信息表）

|字段名|数据类型|约束内容|作用|
|---|---|---|---|
|UserID|INT|IDENTITY(1,1) + PRIMARY KEY + NOT NULL|从 1 开始自增，自动 +1，唯一主键，非空|
|UserName|NVARCHAR(20)|NOT NULL + UNIQUE + CHECK(LEN BETWEEN 2 AND 20)|非空，2~20 字符，无重复值|
|Password|NVARCHAR(50)|NOT NULL + CHECK(LEN BETWEEN 8 AND 50 AND 禁止空格)|非空，8~50 字符，禁止空格|
|Email|NVARCHAR(100)|NOT NULL + UNIQUE + CHECK(标准邮箱格式)|非空，≤100 字符，符合标准邮箱格式，无重复值|
|RegisterTime|DATETIME|NOT NULL + DEFAULT GETDATE()|默认自动记录注册时间|

---

## 2. Documents（文献信息表）

|字段名|数据类型|约束内容|作用说明|
|---|---|---|---|
|DocumentID|INT|IDENTITY(1,1) + PRIMARY KEY + NOT NULL|从 1 开始自增，唯一主键|
|Title|NVARCHAR(300)|NOT NULL + CHECK(LEN BETWEEN 1 AND 300)|文献标题|
|Author|NVARCHAR(100)|NOT NULL + CHECK(LEN BETWEEN 1 AND 100)|文献作者|
|Abstract|NVARCHAR(MAX)|NOT NULL|文献摘要|
|PublishDate|DATE|NOT NULL|文献发表日期|
|Category|NVARCHAR(50)|NOT NULL + CHECK(LEN BETWEEN 1 AND 50)|文献分类|
|FilePath|NVARCHAR(500)|NOT NULL + CHECK(LEN BETWEEN 1 AND 500)|文件存储路径|
|UploadUserID|INT|NULL + FOREIGN KEY → Users(UserID)|上传用户|
|KeywordsText|NVARCHAR(500)|NOT NULL + CHECK(LEN <= 500)|拼接后的关键词文本|
|UploadTime|DATETIME|NOT NULL + DEFAULT GETDATE()|上传时间|

---

## 3. Keywords（关键词表）

|字段名|数据类型|约束内容|作用说明|
|---|---|---|---|
|KeywordID|INT|IDENTITY(1,1) + PRIMARY KEY + NOT NULL|自动递增主键|
|KeywordName|NVARCHAR(100)|NOT NULL + UNIQUE + CHECK(LEN BETWEEN 1 AND 100)|唯一关键词|

---

## 4. DocumentKeyword（文献关键词关联表）

|字段名|数据类型|外键|约束内容|作用说明|
|---|---|---|---|---|
|DocumentID|INT|Documents.DocumentID|NOT NULL + ON DELETE CASCADE|对应文献|
|KeywordID|INT|Keywords.KeywordID|NOT NULL + ON DELETE CASCADE|对应关键词|
|TF_IDF|FLOAT|-|NOT NULL + CHECK(TF_IDF >= 0)|TF-IDF 权重|

### 联合主键

```text
(DocumentID, KeywordID)
```

保证同一篇文献不会重复绑定同一个关键词。

---

## 5. SearchHistory（检索历史表）

|字段名|数据类型|外键|约束内容|
|---|---|---|---|
|HistoryID|INT|-|IDENTITY(1,1) + PRIMARY KEY|
|UserID|INT|Users.UserID|NOT NULL + FOREIGN KEY|
|SearchKeyword|NVARCHAR(200)|-|NOT NULL + CHECK(LEN BETWEEN 1 AND 200)|
|SearchTime|DATETIME|-|DEFAULT GETDATE()|

---

## 6. Citation（文献引用关系表）

|字段名|数据类型|外键|作用说明|
|---|---|---|---|
|CitationID|INT|-|引用关系主键|
|SourceDocumentID|INT|Documents.DocumentID|引用方文献|
|TargetDocumentID|INT|Documents.DocumentID|被引用文献|

### 附加约束

#### 联合唯一约束

```text
(SourceDocumentID, TargetDocumentID)
```

禁止重复引用。

#### 自引用检查

```text
SourceDocumentID <> TargetDocumentID
```

禁止文献引用自身。

---

# 数据库索引设计

|索引名称|所属表|字段|
|---|---|---|
|IX_Documents_Title|Documents|Title|
|IX_Documents_Author|Documents|Author|
|IX_Keywords_Name|Keywords|KeywordName|
|IX_DocumentKeyword_KeywordID|DocumentKeyword|KeywordID|
|IX_SearchHistory_UserID|SearchHistory|UserID|
|IX_Citation_Source|Citation|SourceDocumentID|
|IX_Citation_Target|Citation|TargetDocumentID|

---

# 数据库总体结构

```text
AcademicSearchDB
│
├── Users
├── Documents
├── Keywords
├── DocumentKeyword
├── SearchHistory
└── Citation
```