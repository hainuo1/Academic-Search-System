/*=====================================================
 AcademicSearchDB
 学术文献检索系统数据库
 Version : 1.0 Final
=====================================================*/

IF DB_ID('AcademicSearchDB') IS NOT NULL
BEGIN
    ALTER DATABASE AcademicSearchDB
    SET SINGLE_USER WITH ROLLBACK IMMEDIATE;

    DROP DATABASE AcademicSearchDB;
END
GO

CREATE DATABASE AcademicSearchDB;
GO

USE AcademicSearchDB;
GO

/*=====================================================
 1.Users（用户表）
=====================================================*/

CREATE TABLE dbo.Users
(
    UserID INT IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_Users PRIMARY KEY CLUSTERED,

    UserName NVARCHAR(20) NOT NULL
        CONSTRAINT UQ_Users_UserName UNIQUE,

    Password NVARCHAR(50) NOT NULL,

    Email NVARCHAR(100) NOT NULL
        CONSTRAINT UQ_Users_Email UNIQUE,

    RegisterTime DATETIME NOT NULL
        CONSTRAINT DF_Users_RegisterTime DEFAULT(GETDATE()),

    CONSTRAINT CK_Users_UserName
        CHECK (LEN(UserName) BETWEEN 2 AND 20),

    CONSTRAINT CK_Users_Password
        CHECK (
            LEN(Password) BETWEEN 8 AND 50
            AND Password NOT LIKE '% %'
        ),

    CONSTRAINT CK_Users_Email
        CHECK (
            LEN(Email) <= 100
            AND Email LIKE '%_@__%.__%'
            AND Email NOT LIKE '%@%@%'
            AND Email NOT LIKE '.%'
            AND Email NOT LIKE '%.'
            AND Email NOT LIKE '%..%'
        )
);
GO

/*=====================================================
 2.Documents（文献表）
=====================================================*/

CREATE TABLE dbo.Documents
(
    DocumentID INT IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_Documents PRIMARY KEY CLUSTERED,

    Title NVARCHAR(300) NOT NULL
        CONSTRAINT CK_Documents_Title
        CHECK (LEN(Title) BETWEEN 1 AND 300),

    Author NVARCHAR(100) NOT NULL
        CONSTRAINT CK_Documents_Author
        CHECK (LEN(Author) BETWEEN 1 AND 100),

    Abstract NVARCHAR(MAX) NOT NULL,

    PublishDate DATE NOT NULL,

    Category NVARCHAR(50) NOT NULL
        CONSTRAINT CK_Documents_Category
        CHECK (LEN(Category) BETWEEN 1 AND 50),

    FilePath NVARCHAR(500) NOT NULL
        CONSTRAINT CK_Documents_FilePath
        CHECK (LEN(FilePath) BETWEEN 1 AND 500),

    UploadUserID INT NOT NULL,

    KeywordsText NVARCHAR(500) NOT NULL
        CONSTRAINT CK_Documents_KeywordsText
        CHECK (LEN(KeywordsText) <= 500),

    UploadTime DATETIME NOT NULL
        CONSTRAINT DF_Documents_UploadTime DEFAULT(GETDATE()),

    CONSTRAINT FK_Documents_Users
        FOREIGN KEY (UploadUserID)
        REFERENCES dbo.Users(UserID)
);
GO

/*=====================================================
 3.Keywords（关键词表）
=====================================================*/

CREATE TABLE dbo.Keywords
(
    KeywordID INT IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_Keywords PRIMARY KEY CLUSTERED,

    KeywordName NVARCHAR(100) NOT NULL
        CONSTRAINT UQ_Keywords_KeywordName UNIQUE,

    CONSTRAINT CK_Keywords_KeywordName
        CHECK (LEN(KeywordName) BETWEEN 1 AND 100)
);
GO

/*=====================================================
 4.DocumentKeyword（文献关键词关联表）
=====================================================*/

CREATE TABLE dbo.DocumentKeyword
(
    DocumentID INT NOT NULL,

    KeywordID INT NOT NULL,

    TF_IDF FLOAT NOT NULL
        CONSTRAINT CK_DocumentKeyword_TFIDF
        CHECK (TF_IDF >= 0),

    CONSTRAINT PK_DocumentKeyword
        PRIMARY KEY CLUSTERED
        (
            DocumentID,
            KeywordID
        ),

    CONSTRAINT FK_DocumentKeyword_Document
        FOREIGN KEY (DocumentID)
        REFERENCES dbo.Documents(DocumentID)
        ON DELETE CASCADE,

    CONSTRAINT FK_DocumentKeyword_Keyword
        FOREIGN KEY (KeywordID)
        REFERENCES dbo.Keywords(KeywordID)
        ON DELETE CASCADE
);
GO

/*=====================================================
 5.SearchHistory（检索历史表）
=====================================================*/

CREATE TABLE dbo.SearchHistory
(
    HistoryID INT IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_SearchHistory PRIMARY KEY CLUSTERED,

    UserID INT NOT NULL,

    SearchKeyword NVARCHAR(200) NOT NULL
        CONSTRAINT CK_SearchHistory_SearchKeyword
        CHECK (LEN(SearchKeyword) BETWEEN 1 AND 200),

    SearchTime DATETIME NOT NULL
        CONSTRAINT DF_SearchHistory_SearchTime DEFAULT(GETDATE()),

    CONSTRAINT FK_SearchHistory_User
        FOREIGN KEY (UserID)
        REFERENCES dbo.Users(UserID)
        ON DELETE CASCADE
);
GO

/*=====================================================
 6.Citation（引用关系表）
=====================================================*/

CREATE TABLE dbo.Citation
(
    CitationID INT IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_Citation PRIMARY KEY CLUSTERED,

    SourceDocumentID INT NOT NULL,

    TargetDocumentID INT NOT NULL,

    CONSTRAINT UQ_Citation
        UNIQUE
        (
            SourceDocumentID,
            TargetDocumentID
        ),

    CONSTRAINT CK_Citation_NotSelf
        CHECK (SourceDocumentID <> TargetDocumentID),

    CONSTRAINT FK_Citation_Source
        FOREIGN KEY (SourceDocumentID)
        REFERENCES dbo.Documents(DocumentID)
        ON DELETE CASCADE,

    CONSTRAINT FK_Citation_Target
        FOREIGN KEY (TargetDocumentID)
        REFERENCES dbo.Documents(DocumentID)
        ON DELETE CASCADE
);
GO

/*=====================================================
 7.Favorites（收藏表）
=====================================================*/

CREATE TABLE dbo.Favorites
(
    FavoriteID INT IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_Favorites PRIMARY KEY CLUSTERED,

    UserID INT NOT NULL,

    DocumentID INT NOT NULL,

    CreateTime DATETIME NOT NULL
        CONSTRAINT DF_Favorites_CreateTime
        DEFAULT(GETDATE()),

    CONSTRAINT UQ_Favorites
        UNIQUE (UserID, DocumentID),

    CONSTRAINT FK_Favorites_User
        FOREIGN KEY (UserID)
        REFERENCES dbo.Users(UserID)
        ON DELETE CASCADE,

    CONSTRAINT FK_Favorites_Document
        FOREIGN KEY (DocumentID)
        REFERENCES dbo.Documents(DocumentID)
        ON DELETE CASCADE
);
GO

/*=====================================================
 索引
=====================================================*/

CREATE INDEX IX_Documents_Title
ON dbo.Documents(Title);
GO

CREATE INDEX IX_Documents_Author
ON dbo.Documents(Author);
GO

CREATE INDEX IX_Keywords_Name
ON dbo.Keywords(KeywordName);
GO

CREATE INDEX IX_DocumentKeyword_KeywordID
ON dbo.DocumentKeyword(KeywordID);
GO

CREATE INDEX IX_SearchHistory_UserID
ON dbo.SearchHistory(UserID);
GO

CREATE INDEX IX_Citation_Source
ON dbo.Citation(SourceDocumentID);
GO

CREATE INDEX IX_Citation_Target
ON dbo.Citation(TargetDocumentID);
GO

CREATE INDEX IX_Favorites_UserID
ON dbo.Favorites(UserID);
GO

CREATE INDEX IX_Favorites_DocumentID
ON dbo.Favorites(DocumentID);
GO