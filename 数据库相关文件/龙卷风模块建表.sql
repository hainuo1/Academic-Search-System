-- ============================================================
-- 龙卷风模块建表 SQL —— 气象科学研究数据平台
-- 数据来源：NOAA SPC（Storm Prediction Center）全美龙卷风历史数据库
--          下载地址：https://www.spc.noaa.gov/wcm/data/1950-2024_actual_tornadoes.csv
-- 范围约束：中国境内，经度 73°E–135°E，纬度 18°N–54°N
-- ============================================================

USE `AcademicSearchDB`;

-- --------------------------------------------------------
-- 1. 龙卷风基本信息表
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `TornadoInfo` (
    `EventID`        INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    `DateTime`       DATETIME     NOT NULL COMMENT '发生时间（UTC+8）',
    `Latitude`       FLOAT        NOT NULL COMMENT '纬度',
    `Longitude`      FLOAT        NOT NULL COMMENT '经度',
    `Place`          VARCHAR(200) DEFAULT '' COMMENT '发生地点',
    `Province`       VARCHAR(50)  DEFAULT '' COMMENT '所在省份',
    `EFScale`        VARCHAR(10)  DEFAULT '' COMMENT 'EF等级：EF0/EF1/EF2/EF3/EF4/EF5',
    `Magnitude`      INT          DEFAULT 0 COMMENT 'EF等级数值（0-5）',
    `Casualties`     INT          DEFAULT 0 COMMENT '伤亡人数',
    `Deaths`         INT          DEFAULT 0 COMMENT '死亡人数',
    `Injuries`       INT          DEFAULT 0 COMMENT '受伤人数',
    `Damage`         VARCHAR(500) DEFAULT '' COMMENT '灾害描述',
    `Confidence`     VARCHAR(20)  DEFAULT '' COMMENT '可信度：confirmed/probable/possible',
    `Source`         VARCHAR(100) DEFAULT '' COMMENT '数据来源',
    INDEX `idx_tornado_datetime` (`DateTime`),
    INDEX `idx_tornado_province` (`Province`),
    INDEX `idx_tornado_ef` (`EFScale`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- 2. 龙卷风 AI 分析缓存表
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `TornadoAIAnalysis` (
    `EventID`       INT          NOT NULL COMMENT '龙卷风事件 ID',
    `AnalysisType`  VARCHAR(20)  NOT NULL COMMENT '分析类型：trend/risk/climate',
    `Content`       TEXT         NOT NULL COMMENT 'AI 分析结果文本',
    `CreatedAt`     DATETIME     DEFAULT NOW() COMMENT '首次生成时间',
    PRIMARY KEY (`EventID`, `AnalysisType`),
    FOREIGN KEY (`EventID`) REFERENCES `TornadoInfo`(`EventID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
