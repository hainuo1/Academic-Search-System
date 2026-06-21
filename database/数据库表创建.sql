-- ============================================================
-- 数据库：AcademicSearchDB
-- 说明：学术文献检索系统 完整建表脚本
-- 生成方式：从 Flask 项目代码中逆向提取
-- ============================================================

USE AcademicSearchDB;
GO

-- ============================================================
-- 1. 用户表（Users）
-- ============================================================
CREATE TABLE Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    UserName NVARCHAR(20) NOT NULL UNIQUE,
    Password NVARCHAR(255) NOT NULL,           -- 经过 werkzeug 哈希加密
    Email NVARCHAR(100) NOT NULL UNIQUE,
    Question1 NVARCHAR(100) NOT NULL,           -- 安全问题1
    Answer1Hash NVARCHAR(255) NOT NULL,         -- 答案1的哈希值
    Question2 NVARCHAR(100) NOT NULL,           -- 安全问题2
    Answer2Hash NVARCHAR(255) NOT NULL,         -- 答案2的哈希值
    FailedAttempts INT DEFAULT 0,               -- 登录失败次数
    LockoutUntil DATETIME NULL,                 -- 锁定到期时间
    RegisterTime DATETIME DEFAULT GETDATE()
);
GO

-- ============================================================
-- 2. 文献表（Documents）
-- ============================================================
CREATE TABLE Documents (
    DocumentID INT IDENTITY(1,1) PRIMARY KEY,
    Title NVARCHAR(500) NOT NULL,
    Author NVARCHAR(200) NOT NULL,
    Abstract NVARCHAR(MAX) NOT NULL,
    PublishDate DATE NOT NULL,
    Category NVARCHAR(100) NOT NULL,
    FilePath NVARCHAR(500) NOT NULL,            -- PDF 文件存储路径
    UploadUserID INT NOT NULL,                  -- 上传者 ID
    UploadTime DATETIME DEFAULT GETDATE(),
    ViewCount INT DEFAULT 0,
    DownloadCount INT DEFAULT 0,
    KeywordsText NVARCHAR(500),                 -- 关键词文本（分号分隔，冗余字段）
    FullText NVARCHAR(MAX),                     -- PDF 提取的全文（用于全文检索）
    FOREIGN KEY (UploadUserID) REFERENCES Users(UserID)
);
GO

-- ============================================================
-- 3. 关键词表（Keywords）
-- ============================================================
CREATE TABLE Keywords (
    KeywordID INT IDENTITY(1,1) PRIMARY KEY,
    KeywordName NVARCHAR(100) NOT NULL UNIQUE
);
GO

-- ============================================================
-- 4. 文献-关键词关联表（DocumentKeyword）
-- ============================================================
CREATE TABLE DocumentKeyword (
    DocumentID INT NOT NULL,
    KeywordID INT NOT NULL,
    TF_IDF FLOAT DEFAULT 1.0,                   -- 预留 TF-IDF 权重字段
    PRIMARY KEY (DocumentID, KeywordID),
    FOREIGN KEY (DocumentID) REFERENCES Documents(DocumentID),
    FOREIGN KEY (KeywordID) REFERENCES Keywords(KeywordID)
);
GO

-- ============================================================
-- 5. 引用关系表（Citation）
-- ============================================================
CREATE TABLE Citation (
    SourceDocumentID INT NOT NULL,              -- 引用的来源文献
    TargetDocumentID INT NOT NULL,              -- 被引用的目标文献
    PRIMARY KEY (SourceDocumentID, TargetDocumentID),
    FOREIGN KEY (SourceDocumentID) REFERENCES Documents(DocumentID),
    FOREIGN KEY (TargetDocumentID) REFERENCES Documents(DocumentID)
);
GO

-- ============================================================
-- 6. 收藏表（Favorites）
-- ============================================================
CREATE TABLE Favorites (
    FavoriteID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT NOT NULL,
    DocumentID INT NOT NULL,
    CreateTime DATETIME DEFAULT GETDATE(),
    UNIQUE (UserID, DocumentID),                -- 同一用户不能重复收藏同一文献
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (DocumentID) REFERENCES Documents(DocumentID)
);
GO

-- ============================================================
-- 7. 浏览历史表（BrowseHistory）
-- ============================================================
CREATE TABLE BrowseHistory (
    HistoryID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT NOT NULL,
    DocumentID INT NOT NULL,
    ViewTime DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (DocumentID) REFERENCES Documents(DocumentID)
);
GO

-- ============================================================
-- 8. 检索历史表（SearchHistory）
-- ============================================================
CREATE TABLE SearchHistory (
    HistoryID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT NOT NULL,
    SearchKeyword NVARCHAR(200) NOT NULL,
    SearchTime DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);
GO

-- ============================================================
-- 9. 用户检索计数表（UserSearchCount）
-- ============================================================
CREATE TABLE UserSearchCount (
    UserID INT PRIMARY KEY,
    SearchCount INT DEFAULT 1,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);
GO

-- ============================================================
-- 10. 关键词检索计数表（KeywordSearchCount）
-- ============================================================
CREATE TABLE KeywordSearchCount (
    Keyword NVARCHAR(200) PRIMARY KEY,
    SearchCount INT DEFAULT 1
);
GO
