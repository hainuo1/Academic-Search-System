-- ============================================================
-- 地震模块建表 SQL —— 气象科学研究数据平台
-- 数据来源：USGS Earthquake Catalog（FDSN Event Web Service）
-- 范围约束：中国境内及周边，经度 73°E–135°E，纬度 18°N–54°N
-- ============================================================

USE `AcademicSearchDB`;

-- --------------------------------------------------------
-- 1. 地震基本信息表
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `EarthquakeInfo` (
    `EventID`        VARCHAR(30)  PRIMARY KEY COMMENT 'USGS 事件 ID，如 us7000rr52',
    `DateTime`       DATETIME     NOT NULL COMMENT '发震时间（UTC）',
    `Latitude`       FLOAT        NOT NULL COMMENT '纬度（-90~90）',
    `Longitude`      FLOAT        NOT NULL COMMENT '经度（-180~180）',
    `Depth`          FLOAT        DEFAULT 0 COMMENT '震源深度（km）',
    `Magnitude`      FLOAT        DEFAULT 0 COMMENT '震级（Mw/Ms/mb）',
    `MagType`        VARCHAR(10)  DEFAULT '' COMMENT '震级类型',
    `Place`          VARCHAR(300) DEFAULT '' COMMENT '参考地点描述',
    `Status`         VARCHAR(20)  DEFAULT '' COMMENT '审核状态：reviewed/automatic',
    `Tsunami`        INT          DEFAULT 0 COMMENT '海啸预警（0=无, 1=有）',
    `Alert`          VARCHAR(20)  DEFAULT '' COMMENT '警报级别：green/yellow/orange/red',
    `Significance`   INT          DEFAULT 0 COMMENT '事件显著性（0-1000+）',
    `Gap`            FLOAT        DEFAULT 0 COMMENT '台站方位角间隙',
    `Dmin`           FLOAT        DEFAULT 0 COMMENT '距最近台站距离（°）',
    `Rms`            FLOAT        DEFAULT 0 COMMENT '定位残差均方根',
    `Nst`            INT          DEFAULT 0 COMMENT '定位使用台站数',
    `HorizontalError` FLOAT       DEFAULT 0 COMMENT '水平定位误差（km）',
    `DepthError`     FLOAT        DEFAULT 0 COMMENT '深度误差（km）',
    `MagError`       FLOAT        DEFAULT 0 COMMENT '震级误差',
    `MagNst`         INT          DEFAULT 0 COMMENT '震级计算台站数',
    `Updated`        DATETIME     NULL COMMENT '最后更新时间（UTC）',
    INDEX `idx_eq_magnitude` (`Magnitude`),
    INDEX `idx_eq_datetime` (`DateTime`),
    INDEX `idx_eq_place` (`Place`(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- 2. 地震 AI 分析缓存表
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `EarthquakeAIAnalysis` (
    `EventID`       VARCHAR(30)  NOT NULL COMMENT '地震事件 ID',
    `AnalysisType`  VARCHAR(20)  NOT NULL COMMENT '分析类型：trend/risk/impact',
    `Content`       TEXT         NOT NULL COMMENT 'AI 分析结果文本',
    `CreatedAt`     DATETIME     DEFAULT NOW() COMMENT '首次生成时间',
    PRIMARY KEY (`EventID`, `AnalysisType`),
    FOREIGN KEY (`EventID`) REFERENCES `EarthquakeInfo`(`EventID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
