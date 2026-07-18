-- ============================================================
-- 台风模块建表 SQL —— 气象学术科研平台 v4.1
-- 数据来源：IBTrACS（国际台风最佳路径数据集）
-- 范围约束：太平洋区域，经度 100°E-180°E，纬度 0°-60°N
-- ============================================================

USE `AcademicSearchDB`;

-- --------------------------------------------------------
-- 1. 台风基本信息表
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `TyphoonInfo` (
    `TyphoonID`    VARCHAR(50)  PRIMARY KEY COMMENT 'IBTrACS SID，如 1984001N11141',
    `TyphoonName`  VARCHAR(100) NOT NULL COMMENT '台风名称（如 HAIYAN）',
    `Season`       INT          NOT NULL COMMENT '所属年份',
    `Basin`        VARCHAR(50)  DEFAULT 'WP' COMMENT '海域代码',
    `MaxWind`      FLOAT        DEFAULT 0 COMMENT '生命周期最大风速（knots）',
    `MinPressure`  FLOAT        DEFAULT 9999 COMMENT '生命周期最低中心气压（hPa）',
    `TotalPoints`  INT          DEFAULT 0 COMMENT '路径点总数',
    `StartTime`    DATETIME     NULL COMMENT '第一个观测点时间（UTC）',
    `EndTime`      DATETIME     NULL COMMENT '最后一个观测点时间（UTC）',
    INDEX `idx_typhoon_season` (`Season`),
    INDEX `idx_typhoon_name` (`TyphoonName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- 2. 台风路径点表
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `TyphoonTrack` (
    `TrackID`            INT AUTO_INCREMENT PRIMARY KEY,
    `TyphoonID`          VARCHAR(50)  NOT NULL COMMENT '关联台风 ID',
    `DateTime`           DATETIME     NOT NULL COMMENT '观测时间（UTC）',
    `Latitude`           FLOAT        NOT NULL COMMENT '纬度（-90~90）',
    `Longitude`          FLOAT        NOT NULL COMMENT '经度（0~360，太平洋区 100~180 即 100°E~180°E）',
    `MaxSustainedWind`   FLOAT        DEFAULT 0 COMMENT '最大持续风速（knots）',
    `MinPressure`        FLOAT        DEFAULT 9999 COMMENT '最低中心气压（hPa）',
    `StormCategory`      VARCHAR(50)  DEFAULT '' COMMENT '强度等级（TD/TS/C1/C2/C3/C4/C5）',
    `WindRadius7NE`      FLOAT        DEFAULT 0 COMMENT '七级风圈（34kt）东北象限半径（海里）',
    `WindRadius7SE`      FLOAT        DEFAULT 0 COMMENT '七级风圈东南象限半径（海里）',
    `WindRadius7SW`      FLOAT        DEFAULT 0 COMMENT '七级风圈西南象限半径（海里）',
    `WindRadius7NW`      FLOAT        DEFAULT 0 COMMENT '七级风圈西北象限半径（海里）',
    `WindRadius10NE`     FLOAT        DEFAULT 0 COMMENT '十级风圈（50kt）东北象限半径（海里）',
    `WindRadius10SE`     FLOAT        DEFAULT 0 COMMENT '十级风圈东南象限半径（海里）',
    `WindRadius10SW`     FLOAT        DEFAULT 0 COMMENT '十级风圈西南象限半径（海里）',
    `WindRadius10NW`     FLOAT        DEFAULT 0 COMMENT '十级风圈西北象限半径（海里）',
    FOREIGN KEY (`TyphoonID`) REFERENCES `TyphoonInfo`(`TyphoonID`) ON DELETE CASCADE,
    INDEX `idx_track_typhoon` (`TyphoonID`),
    INDEX `idx_track_datetime` (`DateTime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- 3. 台风 AI 分析缓存表（分析一次，永久复用）
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `TyphoonAIAnalysis` (
    `TyphoonID`     VARCHAR(50)  NOT NULL COMMENT '台风 ID',
    `AnalysisType`  VARCHAR(20)  NOT NULL COMMENT '分析类型：trend/compare/impact/travel',
    `Content`       TEXT         NOT NULL COMMENT 'AI 分析结果文本',
    `CreatedAt`     DATETIME     DEFAULT NOW() COMMENT '首次生成时间',
    PRIMARY KEY (`TyphoonID`, `AnalysisType`),
    FOREIGN KEY (`TyphoonID`) REFERENCES `TyphoonInfo`(`TyphoonID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
