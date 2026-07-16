-- ============================================================
-- schema_mysql.sql —— MySQL 建表脚本
-- 使用方式：在 Navicat 中新建 AcademicSearchDB 数据库后，执行此脚本
-- ============================================================

CREATE DATABASE IF NOT EXISTS `AcademicSearchDB`
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE `AcademicSearchDB`;

-- --------------------------------------------------------
-- 1. 用户表
-- --------------------------------------------------------
CREATE TABLE `Users` (
    `UserID`          INT AUTO_INCREMENT PRIMARY KEY,
    `UserName`        VARCHAR(50)  NOT NULL UNIQUE,
    `Password`        VARCHAR(255) NOT NULL,
    `Email`           VARCHAR(100) NOT NULL,
    `Question1`       VARCHAR(200),
    `Answer1Hash`     VARCHAR(255),
    `Question2`       VARCHAR(200),
    `Answer2Hash`     VARCHAR(255),
    `FailedAttempts`  INT          NOT NULL DEFAULT 0,
    `LockoutUntil`    DATETIME     NULL
) ENGINE=InnoDB;

-- --------------------------------------------------------
-- 2. 文献表
-- --------------------------------------------------------
CREATE TABLE `Documents` (
    `DocumentID`      INT AUTO_INCREMENT PRIMARY KEY,
    `Title`           VARCHAR(500)  NOT NULL,
    `Author`          VARCHAR(200)  NOT NULL,
    `Abstract`        TEXT,
    `PublishDate`     VARCHAR(50),
    `Category`        VARCHAR(100),
    `FilePath`        VARCHAR(500),
    `UploadUserID`    INT           NOT NULL,
    `KeywordsText`    VARCHAR(1000),
    `FullText`        LONGTEXT,
    `ViewCount`       INT           NOT NULL DEFAULT 0,
    `DownloadCount`   INT           NOT NULL DEFAULT 0,
    `UploadTime`      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`UploadUserID`) REFERENCES `Users`(`UserID`)
) ENGINE=InnoDB;

-- --------------------------------------------------------
-- 3. 关键词表
-- --------------------------------------------------------
CREATE TABLE `Keywords` (
    `KeywordID`    INT AUTO_INCREMENT PRIMARY KEY,
    `KeywordName`  VARCHAR(200) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- --------------------------------------------------------
-- 4. 文献-关键词关联表
-- --------------------------------------------------------
CREATE TABLE `DocumentKeyword` (
    `DocumentID`  INT   NOT NULL,
    `KeywordID`   INT   NOT NULL,
    `TF_IDF`      FLOAT NOT NULL DEFAULT 1.0,
    PRIMARY KEY (`DocumentID`, `KeywordID`),
    FOREIGN KEY (`DocumentID`) REFERENCES `Documents`(`DocumentID`) ON DELETE CASCADE,
    FOREIGN KEY (`KeywordID`)  REFERENCES `Keywords`(`KeywordID`)   ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------------
-- 5. 引用关系表
-- --------------------------------------------------------
CREATE TABLE `Citation` (
    `SourceDocumentID` INT NOT NULL,
    `TargetDocumentID` INT NOT NULL,
    PRIMARY KEY (`SourceDocumentID`, `TargetDocumentID`),
    FOREIGN KEY (`SourceDocumentID`) REFERENCES `Documents`(`DocumentID`) ON DELETE CASCADE,
    FOREIGN KEY (`TargetDocumentID`) REFERENCES `Documents`(`DocumentID`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------------
-- 6. 收藏表
-- --------------------------------------------------------
CREATE TABLE `Favorites` (
    `FavoriteID`  INT AUTO_INCREMENT PRIMARY KEY,
    `UserID`      INT      NOT NULL,
    `DocumentID`  INT      NOT NULL,
    `CreateTime`  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`UserID`)     REFERENCES `Users`(`UserID`)         ON DELETE CASCADE,
    FOREIGN KEY (`DocumentID`) REFERENCES `Documents`(`DocumentID`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------------
-- 7. 检索历史表
-- --------------------------------------------------------
CREATE TABLE `SearchHistory` (
    `HistoryID`     INT AUTO_INCREMENT PRIMARY KEY,
    `UserID`        INT          NOT NULL,
    `SearchKeyword` VARCHAR(500) NOT NULL,
    `SearchTime`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`UserID`) REFERENCES `Users`(`UserID`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------------
-- 8. 浏览历史表
-- --------------------------------------------------------
CREATE TABLE `BrowseHistory` (
    `BrowseHistoryID` INT AUTO_INCREMENT PRIMARY KEY,
    `UserID`          INT      NOT NULL,
    `DocumentID`      INT      NOT NULL,
    `ViewTime`        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`UserID`)     REFERENCES `Users`(`UserID`)         ON DELETE CASCADE,
    FOREIGN KEY (`DocumentID`) REFERENCES `Documents`(`DocumentID`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------------
-- 9. 用户搜索次数统计表
-- --------------------------------------------------------
CREATE TABLE `UserSearchCount` (
    `UserID`      INT PRIMARY KEY,
    `SearchCount` INT NOT NULL DEFAULT 0,
    FOREIGN KEY (`UserID`) REFERENCES `Users`(`UserID`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------------
-- 10. 关键词搜索次数统计表
-- --------------------------------------------------------
CREATE TABLE `KeywordSearchCount` (
    `Keyword`     VARCHAR(200) PRIMARY KEY,
    `SearchCount` INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;

-- --------------------------------------------------------
-- 索引（加速常见查询）
-- --------------------------------------------------------
CREATE INDEX `idx_documents_category`   ON `Documents`(`Category`);
CREATE INDEX `idx_documents_uploaduser` ON `Documents`(`UploadUserID`);
CREATE INDEX `idx_documents_title`      ON `Documents`(`Title`);
CREATE INDEX `idx_searchhistory_user`   ON `SearchHistory`(`UserID`, `SearchTime` DESC);
CREATE INDEX `idx_browsehistory_user`   ON `BrowseHistory`(`UserID`, `ViewTime` DESC);
CREATE INDEX `idx_favorites_user`       ON `Favorites`(`UserID`);
