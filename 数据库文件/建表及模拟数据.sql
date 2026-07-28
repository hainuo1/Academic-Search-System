-- ============================================================
-- 建表及模拟数据.sql —— PostgreSQL + PostGIS 完整建库脚本
-- 气象科学研究数据平台 v6.0
--
-- 使用方法（图形界面）：
--   1. 在 pgAdmin 或 DBeaver 中创建数据库 "AcademicSearchDB"
--   2. 打开此文件，全选 → 执行
--
-- 技术栈：PostgreSQL + PostGIS 空间扩展 + pg_trgm 全文检索
-- 数据来源：IBTrACS v04r01 / USGS Earthquake Catalog / NOAA SPC
-- ============================================================

-- ════════════════════════════════════════════════════════════
-- 必须扩展（首次执行需要超级用户权限）
-- ════════════════════════════════════════════════════════════
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;


-- ════════════════════════════════════════════════════════════
-- 第一部分：建表（共 17 张表）
-- ════════════════════════════════════════════════════════════

-- --------------------------------------------------------
-- 1. 用户表
-- --------------------------------------------------------
CREATE TABLE users (
    user_id         SERIAL PRIMARY KEY,
    user_name       VARCHAR(50)  NOT NULL UNIQUE,
    password        VARCHAR(255) NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    question1       VARCHAR(200),
    answer1_hash    VARCHAR(255),
    question2       VARCHAR(200),
    answer2_hash    VARCHAR(255),
    failed_attempts INT          NOT NULL DEFAULT 0,
    lockout_until   TIMESTAMP    NULL,
    register_time   TIMESTAMP    NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  users IS '系统注册用户';
COMMENT ON COLUMN users.user_id         IS '用户唯一标识（自增）';
COMMENT ON COLUMN users.user_name       IS '登录用户名';
COMMENT ON COLUMN users.password        IS 'Werkzeug scrypt 加密密码';
COMMENT ON COLUMN users.email           IS '绑定邮箱';
COMMENT ON COLUMN users.failed_attempts IS '连续登录/找回密码失败次数';
COMMENT ON COLUMN users.lockout_until   IS '账户锁定到期时间（NULL=未锁定）';
COMMENT ON COLUMN users.register_time   IS '注册时间戳';

-- --------------------------------------------------------
-- 2. 文献表（含 PostgreSQL 全文检索）
-- --------------------------------------------------------
CREATE TABLE documents (
    document_id     SERIAL PRIMARY KEY,
    title           VARCHAR(500)  NOT NULL,
    author          VARCHAR(200)  NOT NULL,
    abstract        TEXT,
    publish_date    VARCHAR(50),
    category        VARCHAR(100),
    file_path       VARCHAR(500),
    upload_user_id  INT           NOT NULL REFERENCES users(user_id),
    keywords_text   VARCHAR(1000),
    full_text       TEXT,
    view_count      INT           NOT NULL DEFAULT 0,
    download_count  INT           NOT NULL DEFAULT 0,
    upload_time     TIMESTAMP     NOT NULL DEFAULT NOW()
);

-- 全文检索 tsvector 列 + GIN 索引（替代 MySQL FULLTEXT INDEX）
-- 使用 'simple' 分词配置：英文按空格分词，中文按单字分词，不进行词干提取
ALTER TABLE documents ADD COLUMN full_text_tsv tsvector;
CREATE INDEX idx_documents_fulltext_tsv ON documents USING GIN (full_text_tsv);

CREATE OR REPLACE FUNCTION documents_tsv_trigger() RETURNS trigger AS $$
BEGIN
    NEW.full_text_tsv :=
        setweight(to_tsvector('simple', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('simple', COALESCE(NEW.abstract, '')), 'B') ||
        setweight(to_tsvector('simple', COALESCE(NEW.full_text, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_documents_tsv
    BEFORE INSERT OR UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION documents_tsv_trigger();

-- 回填已有数据（如果触发器在数据之后创建，执行 UPDATE 触发重建）
-- UPDATE documents SET full_text = full_text;

-- pg_trgm 索引：加速 ILIKE '%中文%' 中文兜底查询（可选，数据量增大后建议启用）
-- CREATE INDEX IF NOT EXISTS idx_documents_full_text_trgm ON documents USING GIN (full_text gin_trgm_ops);
-- CREATE INDEX IF NOT EXISTS idx_documents_title_trgm ON documents USING GIN (title gin_trgm_ops);

CREATE INDEX idx_documents_category   ON documents(category);
CREATE INDEX idx_documents_uploaduser ON documents(upload_user_id);
CREATE INDEX idx_documents_title      ON documents(title);
CREATE INDEX idx_documents_pubdate    ON documents(publish_date);

COMMENT ON TABLE  documents IS '学术文献元数据及全文内容';
COMMENT ON COLUMN documents.full_text_tsv IS '全文检索向量（tsvector），通过触发器自动维护，simple 配置，权重 A-标题/B-摘要/C-全文';

-- --------------------------------------------------------
-- 3. 关键词表
-- --------------------------------------------------------
CREATE TABLE keywords (
    keyword_id   SERIAL PRIMARY KEY,
    keyword_name VARCHAR(200) NOT NULL UNIQUE
);

COMMENT ON TABLE keywords IS '关键词字典化统一管理';

-- --------------------------------------------------------
-- 4. 文献-关键词关联表
-- --------------------------------------------------------
CREATE TABLE document_keyword (
    document_id INT                NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    keyword_id  INT                NOT NULL REFERENCES keywords(keyword_id)    ON DELETE CASCADE,
    tf_idf      DOUBLE PRECISION   NOT NULL DEFAULT 1.0,
    PRIMARY KEY (document_id, keyword_id)
);

COMMENT ON TABLE document_keyword IS '文献与关键词多对多关系（含 TF-IDF 权重）';

-- --------------------------------------------------------
-- 5. 引用关系表
-- --------------------------------------------------------
CREATE TABLE citation (
    source_document_id INT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    target_document_id INT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    PRIMARY KEY (source_document_id, target_document_id),
    CHECK (source_document_id <> target_document_id)
);

COMMENT ON TABLE citation IS '文献之间的引用关系网络';

-- --------------------------------------------------------
-- 6. 收藏表
-- --------------------------------------------------------
CREATE TABLE favorites (
    favorite_id SERIAL PRIMARY KEY,
    user_id     INT       NOT NULL REFERENCES users(user_id)         ON DELETE CASCADE,
    document_id INT       NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    create_time TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, document_id)
);

CREATE INDEX idx_favorites_user ON favorites(user_id);

COMMENT ON TABLE favorites IS '用户文献收藏记录';

-- --------------------------------------------------------
-- 7. 检索历史表
-- --------------------------------------------------------
CREATE TABLE search_history (
    history_id     SERIAL PRIMARY KEY,
    user_id        INT          NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    search_keyword VARCHAR(500) NOT NULL,
    search_time    TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_searchhistory_user ON search_history(user_id, search_time DESC);

COMMENT ON TABLE search_history IS '用户检索操作记录';

-- --------------------------------------------------------
-- 8. 浏览历史表
-- --------------------------------------------------------
CREATE TABLE browse_history (
    browse_history_id SERIAL PRIMARY KEY,
    user_id           INT       NOT NULL REFERENCES users(user_id)         ON DELETE CASCADE,
    document_id       INT       NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    view_time         TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_browsehistory_user ON browse_history(user_id, view_time DESC);

COMMENT ON TABLE browse_history IS '用户文献浏览记录';

-- --------------------------------------------------------
-- 9. 用户搜索次数统计表
-- --------------------------------------------------------
CREATE TABLE user_search_count (
    user_id      INT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    search_count INT NOT NULL DEFAULT 0
);

COMMENT ON TABLE user_search_count IS '用户累积检索次数统计（用于活跃排行榜）';

-- --------------------------------------------------------
-- 10. 关键词搜索次数统计表
-- --------------------------------------------------------
CREATE TABLE keyword_search_count (
    keyword      VARCHAR(200) PRIMARY KEY,
    search_count INT NOT NULL DEFAULT 0
);

COMMENT ON TABLE keyword_search_count IS '关键词被检索次数统计（用于热门排行）';


-- ════════════════════════════════════════════════════════════
-- 气象灾害模块（含 PostGIS 空间列）
-- ════════════════════════════════════════════════════════════

-- --------------------------------------------------------
-- 11. 台风基本信息表
-- --------------------------------------------------------
CREATE TABLE typhoon_info (
    typhoon_id   VARCHAR(50)  PRIMARY KEY,
    typhoon_name VARCHAR(100) NOT NULL,
    season       INT          NOT NULL,
    basin        VARCHAR(50)  DEFAULT 'WP',
    max_wind     DOUBLE PRECISION DEFAULT 0,
    min_pressure DOUBLE PRECISION DEFAULT 9999,
    total_points INT          DEFAULT 0,
    start_time   TIMESTAMP    NULL,
    end_time     TIMESTAMP    NULL,

    -- PostGIS 几何列
    track_geom   geometry(LineString, 4326) NULL,
    bbox         geometry(Polygon, 4326)    NULL
);

CREATE INDEX idx_typhoon_season     ON typhoon_info(season);
CREATE INDEX idx_typhoon_name      ON typhoon_info(typhoon_name);
CREATE INDEX idx_typhoon_track_geom ON typhoon_info USING GIST (track_geom);
CREATE INDEX idx_typhoon_bbox      ON typhoon_info USING GIST (bbox);

COMMENT ON TABLE  typhoon_info IS '台风基本信息（IBTrACS 数据），含 PostGIS 轨迹几何';
COMMENT ON COLUMN typhoon_info.track_geom IS '台风中心轨迹线（LineString, EPSG:4326）';
COMMENT ON COLUMN typhoon_info.bbox       IS '轨迹外包矩形（用于快速空间过滤）';

-- --------------------------------------------------------
-- 12. 台风路径点表
-- --------------------------------------------------------
CREATE TABLE typhoon_track (
    track_id             SERIAL PRIMARY KEY,
    typhoon_id           VARCHAR(50)  NOT NULL REFERENCES typhoon_info(typhoon_id) ON DELETE CASCADE,
    date_time            TIMESTAMP    NOT NULL,
    latitude             DOUBLE PRECISION NOT NULL,
    longitude            DOUBLE PRECISION NOT NULL,
    max_sustained_wind   DOUBLE PRECISION DEFAULT 0,
    min_pressure         DOUBLE PRECISION DEFAULT 9999,
    storm_category       VARCHAR(50)  DEFAULT '',

    -- PostGIS 点几何（自动生成）
    geom                 geometry(Point, 4326) NOT NULL,

    wind_radius7_ne      DOUBLE PRECISION DEFAULT 0,
    wind_radius7_se      DOUBLE PRECISION DEFAULT 0,
    wind_radius7_sw      DOUBLE PRECISION DEFAULT 0,
    wind_radius7_nw      DOUBLE PRECISION DEFAULT 0,
    wind_radius10_ne     DOUBLE PRECISION DEFAULT 0,
    wind_radius10_se     DOUBLE PRECISION DEFAULT 0,
    wind_radius10_sw     DOUBLE PRECISION DEFAULT 0,
    wind_radius10_nw     DOUBLE PRECISION DEFAULT 0
);

-- 自动将经纬度填充为 PostGIS Point
CREATE OR REPLACE FUNCTION set_geom_from_lonlat() RETURNS trigger AS $$
BEGIN
    NEW.geom := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_typhoon_track_geom
    BEFORE INSERT OR UPDATE ON typhoon_track
    FOR EACH ROW EXECUTE FUNCTION set_geom_from_lonlat();

CREATE INDEX idx_track_typhoon   ON typhoon_track(typhoon_id);
CREATE INDEX idx_track_datetime  ON typhoon_track(date_time);
CREATE INDEX idx_track_geom      ON typhoon_track USING GIST (geom);

COMMENT ON TABLE typhoon_track IS '台风路径观测点数据';
COMMENT ON COLUMN typhoon_track.geom IS '观测点空间位置（Point, EPSG:4326），触发器自动生成';

-- --------------------------------------------------------
-- 13. 台风 AI 分析缓存表
-- --------------------------------------------------------
CREATE TABLE typhoon_ai_analysis (
    typhoon_id    VARCHAR(50) NOT NULL REFERENCES typhoon_info(typhoon_id) ON DELETE CASCADE,
    analysis_type VARCHAR(20) NOT NULL,
    content       TEXT        NOT NULL,
    created_at    TIMESTAMP   DEFAULT NOW(),
    PRIMARY KEY (typhoon_id, analysis_type)
);

COMMENT ON TABLE typhoon_ai_analysis IS '台风 AI 分析结果缓存（DeepSeek）';

-- --------------------------------------------------------
-- 14. 地震基本信息表
-- --------------------------------------------------------
CREATE TABLE earthquake_info (
    event_id         VARCHAR(30)  PRIMARY KEY,
    date_time        TIMESTAMP    NOT NULL,
    latitude         DOUBLE PRECISION NOT NULL,
    longitude        DOUBLE PRECISION NOT NULL,

    -- PostGIS 震中点（自动生成）
    epicenter        geometry(Point, 4326) NOT NULL,

    depth            DOUBLE PRECISION DEFAULT 0,
    magnitude        DOUBLE PRECISION DEFAULT 0,
    mag_type         VARCHAR(10)  DEFAULT '',
    place            VARCHAR(300) DEFAULT '',
    status           VARCHAR(20)  DEFAULT '',
    tsunami          INT          DEFAULT 0,
    alert            VARCHAR(20)  DEFAULT '',
    significance     INT          DEFAULT 0,
    gap              DOUBLE PRECISION DEFAULT 0,
    dmin             DOUBLE PRECISION DEFAULT 0,
    rms              DOUBLE PRECISION DEFAULT 0,
    nst              INT          DEFAULT 0,
    horizontal_error DOUBLE PRECISION DEFAULT 0,
    depth_error      DOUBLE PRECISION DEFAULT 0,
    mag_error        DOUBLE PRECISION DEFAULT 0,
    mag_nst          INT          DEFAULT 0,
    updated          TIMESTAMP    NULL
);

-- 共享 set_geom_from_lonlat 触发器（与 typhoon_track 一致）
-- 但这里字段名是 epicenter，不是 geom，所以需要单独的触发器

CREATE OR REPLACE FUNCTION earthquake_geom_trigger() RETURNS trigger AS $$
BEGIN
    NEW.epicenter := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_earthquake_geom
    BEFORE INSERT OR UPDATE ON earthquake_info
    FOR EACH ROW EXECUTE FUNCTION earthquake_geom_trigger();

CREATE INDEX idx_eq_magnitude  ON earthquake_info(magnitude);
CREATE INDEX idx_eq_datetime   ON earthquake_info(date_time);
CREATE INDEX idx_eq_epicenter  ON earthquake_info USING GIST (epicenter);
CREATE INDEX idx_eq_place      ON earthquake_info(place);

COMMENT ON TABLE  earthquake_info IS '地震基本信息（USGS Earthquake Catalog）';
COMMENT ON COLUMN earthquake_info.epicenter IS '震中点几何（Point, EPSG:4326）';

-- --------------------------------------------------------
-- 15. 地震 AI 分析缓存表
-- --------------------------------------------------------
CREATE TABLE earthquake_ai_analysis (
    event_id      VARCHAR(30) NOT NULL REFERENCES earthquake_info(event_id) ON DELETE CASCADE,
    analysis_type VARCHAR(20) NOT NULL,
    content       TEXT        NOT NULL,
    created_at    TIMESTAMP   DEFAULT NOW(),
    PRIMARY KEY (event_id, analysis_type)
);

COMMENT ON TABLE earthquake_ai_analysis IS '地震 AI 分析结果缓存（DeepSeek）';

-- --------------------------------------------------------
-- 16. 龙卷风基本信息表
-- --------------------------------------------------------
CREATE TABLE tornado_info (
    event_id    SERIAL PRIMARY KEY,
    date_time   TIMESTAMP    NOT NULL,
    latitude    DOUBLE PRECISION NOT NULL,
    longitude   DOUBLE PRECISION NOT NULL,

    -- PostGIS 点几何（自动生成）
    geom        geometry(Point, 4326) NOT NULL,

    place       VARCHAR(200) DEFAULT '',
    province    VARCHAR(50)  DEFAULT '',
    ef_scale    VARCHAR(10)  DEFAULT '',
    magnitude   INT          DEFAULT 0,
    casualties  INT          DEFAULT 0,
    deaths      INT          DEFAULT 0,
    injuries    INT          DEFAULT 0,
    damage      VARCHAR(500) DEFAULT '',
    confidence  VARCHAR(20)  DEFAULT '',
    source      VARCHAR(100) DEFAULT ''
);

CREATE TRIGGER trg_tornado_geom
    BEFORE INSERT OR UPDATE ON tornado_info
    FOR EACH ROW EXECUTE FUNCTION set_geom_from_lonlat();

CREATE INDEX idx_tornado_datetime ON tornado_info(date_time);
CREATE INDEX idx_tornado_province ON tornado_info(province);
CREATE INDEX idx_tornado_ef       ON tornado_info(ef_scale);
CREATE INDEX idx_tornado_geom     ON tornado_info USING GIST (geom);

COMMENT ON TABLE  tornado_info IS '龙卷风基本信息（NOAA SPC）';
COMMENT ON COLUMN tornado_info.geom IS '发生地点（Point, EPSG:4326）';

-- --------------------------------------------------------
-- 17. 龙卷风 AI 分析缓存表
-- --------------------------------------------------------
CREATE TABLE tornado_ai_analysis (
    event_id      INT         NOT NULL REFERENCES tornado_info(event_id) ON DELETE CASCADE,
    analysis_type VARCHAR(20) NOT NULL,
    content       TEXT        NOT NULL,
    created_at    TIMESTAMP   DEFAULT NOW(),
    PRIMARY KEY (event_id, analysis_type)
);

COMMENT ON TABLE tornado_ai_analysis IS '龙卷风 AI 分析结果缓存（DeepSeek）';


-- ════════════════════════════════════════════════════════════
-- 第二部分：模拟测试数据
-- ════════════════════════════════════════════════════════════

-- --------------------------------------------------------
-- 清空旧数据（按外键依赖顺序，可重复执行）
-- --------------------------------------------------------
TRUNCATE TABLE tornado_ai_analysis    RESTART IDENTITY CASCADE;
TRUNCATE TABLE tornado_info           RESTART IDENTITY CASCADE;
TRUNCATE TABLE earthquake_ai_analysis RESTART IDENTITY CASCADE;
TRUNCATE TABLE earthquake_info        RESTART IDENTITY CASCADE;
TRUNCATE TABLE typhoon_ai_analysis    RESTART IDENTITY CASCADE;
TRUNCATE TABLE typhoon_track          RESTART IDENTITY CASCADE;
TRUNCATE TABLE typhoon_info           RESTART IDENTITY CASCADE;
TRUNCATE TABLE browse_history         RESTART IDENTITY CASCADE;
TRUNCATE TABLE search_history         RESTART IDENTITY CASCADE;
TRUNCATE TABLE keyword_search_count   RESTART IDENTITY CASCADE;
TRUNCATE TABLE user_search_count      RESTART IDENTITY CASCADE;
TRUNCATE TABLE favorites              RESTART IDENTITY CASCADE;
TRUNCATE TABLE citation               RESTART IDENTITY CASCADE;
TRUNCATE TABLE document_keyword       RESTART IDENTITY CASCADE;
TRUNCATE TABLE keywords               RESTART IDENTITY CASCADE;
TRUNCATE TABLE documents              RESTART IDENTITY CASCADE;
TRUNCATE TABLE users                  RESTART IDENTITY CASCADE;

-- 确保序列从 1 开始
ALTER SEQUENCE IF EXISTS users_user_id_seq           RESTART WITH 1;
ALTER SEQUENCE IF EXISTS documents_document_id_seq   RESTART WITH 1;
ALTER SEQUENCE IF EXISTS keywords_keyword_id_seq     RESTART WITH 1;
ALTER SEQUENCE IF EXISTS favorites_favorite_id_seq   RESTART WITH 1;
ALTER SEQUENCE IF EXISTS search_history_history_id_seq  RESTART WITH 1;
ALTER SEQUENCE IF EXISTS browse_history_browse_history_id_seq RESTART WITH 1;

-- --------------------------------------------------------
-- 2.1 用户（5 人）
-- --------------------------------------------------------
INSERT INTO users (user_name, password, email, question1, answer1_hash, question2, answer2_hash) VALUES
('admin',
 'scrypt:32768:8:1$JFGjzMinnDKGZbbL$537deda27121867bd7138d937fa72ac1df1a7de36ecf20f1173d96389509e29ef06424e1968a149ff1fd49d73727fd7294af41617d34ceb598e5d9cab19ffd8f',
 'admin@example.com',
 '你最喜欢的城市？',
 'scrypt:32768:8:1$5D4kQMmxUSsyfnvq$7e2edc47de8228529711e1c40dcf7d7f31c2fa2843dcfcca0f4df81b705beaa3b644d12aac50899bf1b2b3123d3b26898887a2554d153bf69be8593b15def50a',
 '你的小学名称？',
 'scrypt:32768:8:1$I1vxxIbxtxyHrHs1$8e7ffe93d806563ed1567bb2d625c8bbe2bf4abc47218712d6a1ea23e7791df51a079bcc23f5ba7cf07e5e8a2a667b7d55eadb8abb0ca45e8e21d64bf40bf46b'),

('张三',
 'scrypt:32768:8:1$kIMGQF4uzsZcJdOp$03fe6c872c4becc2e65e9397c8ed4cafb45c5081c949766dd5a2179c1e21ce61358b2aa853ecd1491016e153ddea69dd72eecfd7bd18e57f6f3d3b87ce8ddf8a',
 'zhangsan@example.com',
 '你的生日是？',
 'scrypt:32768:8:1$0BgevidtBxFGNHCs$81121992859e61611143c65d6ebe93872b0f066ee3b3800de62e5e1a2943ff0cff92e41edc0886be1874d933cee8d78232ca055918dfebfc63b6d5b2adc8180c',
 '你的宠物名字？',
 'scrypt:32768:8:1$H5ZMqTdTudXTh2Oh$a4e3332be1e64944241534954dc4c2138a28ec170597916636f8514160fdbcc040c14f99a9be5b91d002bfd1dcaf987b30c21c72db5156d6fa0ae39fdc6a2741'),

('李四',
 'scrypt:32768:8:1$zUUz4xGsw0gaRFPb$4596c699123d4f584003140f3cacb949ae3c669e2bf557d9e5e674f0763e990f1474ef47b41b0092979d15dc77c0c08dd49892ef982a202a75d9f7d9325c9289',
 'lisi@example.com',
 '你的身份证后四位？',
 'scrypt:32768:8:1$XDt4Ed6Y3tazVdTQ$11004df642039fab7bc92ae1301fbd5c6919c88263398be85cde537d7d1bda942c522c6d2e12dd3ac5968986605cf8d301630866cf8fdb555f463773bf837c52',
 '你喜欢吃什么？',
 'scrypt:32768:8:1$uASLpD761Dg0dfpB$c6e9c9f208ff2b24b9ed3f45315b3094a2513b0f69971f6e3f21670119aaebaa67b8c8f3b075f5e57629a68d00684e4b879350eb00334ca02e1494c2e938c639'),

('王五',
 'scrypt:32768:8:1$JsJdZBzE4gqtsRKU$87ae316232336cbe6514b11b28ea60c434a42563522d4d241e5d3badf9fb0758c13ac97270e782614accbaa07a10f972f490e5539073fee18c1c88a3880a167f',
 'wangwu@example.com',
 '你的母亲名字？',
 'scrypt:32768:8:1$w4lR1bBMgXDp4Fte$a694a8a780067fcd225b06dfa40046f7c2bda7b13b80c902ddf6077714c81accf457d588801fade12460991e84a38a407a02445cca39ae8c637548eff6455f20',
 '你的父亲名字？',
 'scrypt:32768:8:1$8I4xeET69QzAgU2A$b54e6b0f7de08df2d94a54178609f5e0b6b25f035d69e52b01e0d9e68c8ce028715c2310c3c4773d57a03f7bd07c03e8542c8b5c7e78ca15d5997357781d403d'),

('testuser',
 'scrypt:32768:8:1$bTUDILrERNPfDiVM$39f5575411a944cb0f8d434235cdd1d85c344ae528ba6fd6dfd8d48756da26690ec03d7c4c14630500a765410eebd8a1e6925c7300fa2d119a883a371742e963',
 'test@example.com',
 '你的大学名称？',
 'scrypt:32768:8:1$n6ftswAvmQhpDW5Y$15160f82ddb04a321826ce217133c8e3670774a98e60dfb16a60e841e3ed12c646d9f936f45620700e70a252b0c26f0bbc9dd4dd202f171c8581c5cb6c31a91f',
 '你的专业是什么？',
 'scrypt:32768:8:1$64RYUXAjEdnX5QkW$88550ff50e1c8eb64f29e1793cea18ca7d20a0e75d0a4c99ce76a4b7fff4dc61f0f2b0f0ee7ba2a4b1a5f3e77ffeb0f9d00f8ed0415c678831b6395ce3fd1f45');

-- --------------------------------------------------------
-- 2.2 文献（15 篇）
-- --------------------------------------------------------
INSERT INTO documents (title, author, abstract, publish_date, category, file_path, upload_user_id, keywords_text, full_text, view_count, download_count) VALUES
('基于深度学习的自然语言处理综述',
 '陈小明',
 '深度学习技术近年来在自然语言处理领域取得了突破性进展。本文对卷积神经网络、循环神经网络、Transformer等主流架构在文本分类、命名实体识别、机器翻译、情感分析等任务中的应用进行了全面综述。',
 '2024-03-15', '计算机科学', '', 1,
 '深度学习;自然语言处理;Transformer;神经网络;文本分类',
 '深度学习技术近年来在自然语言处理领域取得了突破性进展。本文对卷积神经网络、循环神经网络、Transformer等主流架构在文本分类、命名实体识别、机器翻译、情感分析等任务中的应用进行了全面综述。',
 256, 89),

('Machine Learning Approaches for Medical Image Analysis',
 'Li Wei, Zhang Hua',
 'Medical image analysis plays a critical role in modern clinical diagnosis. This paper reviews state-of-the-art machine learning and deep learning approaches for medical image segmentation, classification, and detection.',
 '2024-01-20', '医学', '', 2,
 'Medical Imaging;Deep Learning;CNN;Computer Vision;Diagnosis',
 'Medical image analysis plays a critical role in modern clinical diagnosis. This paper reviews state-of-the-art machine learning and deep learning approaches for medical image segmentation, classification, and detection.',
 142, 45),

('量子计算在密码学中的应用研究',
 '王建国, 刘芳',
 '量子计算的快速发展对传统密码学构成了重大挑战。Shor算法和Grover算法展示了量子计算机在破解RSA、ECC等公钥密码体系方面的潜力。本文系统梳理了后量子密码学的主要技术路线。',
 '2024-05-10', '计算机科学', '', 3,
 '量子计算;密码学;后量子密码;Shor算法;网络安全',
 '量子计算的快速发展对传统密码学构成了重大挑战。Shor算法和Grover算法展示了量子计算机在破解RSA、ECC等公钥密码体系方面的潜力。本文系统梳理了后量子密码学的主要技术路线。',
 198, 67),

('大数据环境下隐私保护技术研究',
 '赵雪梅',
 '随着大数据技术的广泛应用，数据隐私保护成为社会各界关注的焦点。本文深入分析了差分隐私、联邦学习、安全多方计算、同态加密等前沿隐私保护技术的原理和适用场景。',
 '2024-02-28', '计算机科学', '', 1,
 '大数据;隐私保护;差分隐私;联邦学习;数据安全',
 '随着大数据技术的广泛应用，数据隐私保护成为社会各界关注的焦点。本文深入分析了差分隐私、联邦学习、安全多方计算、同态加密等前沿隐私保护技术的原理和适用场景。',
 173, 52),

('A Survey of Graph Neural Networks',
 'Yang Ming, Chen Fei',
 'Graph Neural Networks have emerged as a powerful tool for learning on graph-structured data. This survey provides a comprehensive overview of GNN architectures including GCN, GAT, GraphSAGE.',
 '2024-04-05', '计算机科学', '', 2,
 'Graph Neural Networks;GNN;GCN;Deep Learning;Graph Representation',
 'Graph Neural Networks have emerged as a powerful tool for learning on graph-structured data. This survey provides a comprehensive overview of GNN architectures including GCN, GAT, GraphSAGE.',
 221, 78),

('气候变化的生态系统影响与适应性策略',
 '林海涛, 陈思远',
 '全球气候变化已对陆地和水生生态系统产生深远影响。本文基于过去20年的观测数据和模型预测，分析了气温升高、降水模式改变和极端天气事件对生物多样性的影响。',
 '2023-12-01', '环境科学', '', 4,
 '气候变化;生态系统;生物多样性;适应性策略;碳排放',
 '全球气候变化已对陆地和水生生态系统产生深远影响。本文基于过去20年的观测数据和模型预测，分析了气温升高、降水模式改变和极端天气事件对生物多样性的影响。',
 88, 21),

('强化学习在自动驾驶决策系统中的应用',
 '张晓峰',
 '自动驾驶技术的核心挑战之一是在复杂动态环境中做出安全高效的决策。本文探讨了深度强化学习在自动驾驶决策规划中的应用。',
 '2024-06-18', '计算机科学', '', 3,
 '强化学习;自动驾驶;决策系统;深度强化学习;CARLA',
 '自动驾驶技术的核心挑战之一是在复杂动态环境中做出安全高效的决策。本文探讨了深度强化学习在自动驾驶决策规划中的应用。',
 134, 38),

('新能源材料的设计与计算模拟',
 '刘阳, 孙浩然',
 '第一性原理计算和分子动力学模拟在新能源材料开发中发挥着越来越重要的作用。本文综述了密度泛函理论、机器学习势函数等方法在锂离子电池电极材料等领域的应用。',
 '2024-03-28', '材料科学', '', 4,
 '新能源材料;DFT;分子动力学;锂电池;钙钛矿',
 '第一性原理计算和分子动力学模拟在新能源材料开发中发挥着越来越重要的作用。本文综述了密度泛函理论、机器学习势函数等方法在锂离子电池电极材料等领域的应用。',
 67, 15),

('知识图谱构建与推理技术综述',
 '陈小明, 王建国',
 '知识图谱作为一种结构化的语义知识库，在智能搜索、问答系统、推荐系统等领域发挥着关键作用。本文系统梳理了知识图谱的构建流程，并对比分析了基于符号逻辑和基于表示学习的知识推理方法。',
 '2024-04-22', '计算机科学', '', 1,
 '知识图谱;知识推理;信息抽取;自然语言处理;表示学习',
 '知识图谱作为一种结构化的语义知识库，在智能搜索、问答系统、推荐系统等领域发挥着关键作用。本文系统梳理了知识图谱的构建流程，并对比分析了基于符号逻辑和基于表示学习的知识推理方法。',
 180, 56),

('脑机接口技术的发展现状与伦理思考',
 '赵雪梅, 林海涛',
 '脑机接口技术近年来取得了显著进展，从实验室逐渐走向临床应用。本文介绍了侵入式、半侵入式和非侵入式脑机接口技术的最新进展和伦理问题。',
 '2024-05-30', '交叉学科', '', 2,
 '脑机接口;神经科学;人工智能;伦理;Neuralink',
 '脑机接口技术近年来取得了显著进展，从实验室逐渐走向临床应用。本文介绍了侵入式、半侵入式和非侵入式脑机接口技术的最新进展和伦理问题。',
 110, 33),

('区块链技术在供应链金融中的应用',
 '刘芳',
 '供应链金融面临信用传递困难、信息不对称和操作效率低等痛点。区块链技术以其去中心化、不可篡改和可追溯的特性，为供应链金融提供了创新解决方案。',
 '2024-01-15', '经济学', '', 5,
 '区块链;供应链金融;智能合约;联盟链;金融科技',
 '供应链金融面临信用传递困难、信息不对称和操作效率低等痛点。区块链技术以其去中心化、不可篡改和可追溯的特性，为供应链金融提供了创新解决方案。',
 75, 18),

('深度学习在蛋白质结构预测中的突破',
 '孙浩然, 张晓峰',
 'AlphaFold2的问世标志着蛋白质结构预测领域的革命性突破。本文深入解析了AlphaFold2的Evoformer架构、结构模块和端到端训练策略。',
 '2024-02-10', '生物学', '', 3,
 'AlphaFold;蛋白质结构预测;深度学习;生物信息学;药物发现',
 'AlphaFold2的问世标志着蛋白质结构预测领域的革命性突破。本文深入解析了AlphaFold2的Evoformer架构、结构模块和端到端训练策略。',
 156, 48),

('教育数字化转型的理论框架与实施路径',
 '陈思远',
 '教育数字化转型是全球教育改革的重要趋势。本文构建了包含数字基础设施、数字素养、数字内容和数字治理四个维度的教育数字化理论框架。',
 '2024-06-01', '教育学', '', 4,
 '教育数字化;教育技术;智慧教育;在线学习;人工智能教育',
 '教育数字化转型是全球教育改革的重要趋势。本文构建了包含数字基础设施、数字素养、数字内容和数字治理四个维度的教育数字化理论框架。',
 45, 9),

('Sentiment Analysis Using Pre-trained Language Models',
 'Yang Ming, Liu Yang',
 'Pre-trained language models such as BERT, RoBERTa, and GPT have achieved state-of-the-art results in various sentiment analysis tasks. We propose a novel attention fusion mechanism.',
 '2024-04-15', '计算机科学', '', 2,
 'Sentiment Analysis;BERT;NLP;Attention Mechanism;Pre-trained Models',
 'Pre-trained language models such as BERT, RoBERTa, and GPT have achieved state-of-the-art results in various sentiment analysis tasks. We propose a novel attention fusion mechanism.',
 189, 62),

('城市交通拥堵的时空模式分析与预测',
 '张晓峰, 刘阳',
 '城市交通拥堵是困扰现代城市发展的全球性问题。本文基于大规模浮动车GPS轨迹数据，运用时空聚类分析、图神经网络和LSTM等方法对城市交通拥堵进行了系统建模。',
 '2024-03-05', '交通运输', '', 1,
 '交通拥堵;时空分析;GPS轨迹;图神经网络;深度学习',
 '城市交通拥堵是困扰现代城市发展的全球性问题。本文基于大规模浮动车GPS轨迹数据，运用时空聚类分析、图神经网络和LSTM等方法对城市交通拥堵进行了系统建模。',
 102, 28);

-- --------------------------------------------------------
-- 2.3 关键词（72 个）
-- --------------------------------------------------------
INSERT INTO keywords (keyword_name) VALUES
('深度学习'), ('自然语言处理'), ('Transformer'), ('神经网络'), ('文本分类'),
('Medical Imaging'), ('Deep Learning'), ('CNN'), ('Computer Vision'), ('Diagnosis'),
('量子计算'), ('密码学'), ('后量子密码'), ('Shor算法'), ('网络安全'),
('大数据'), ('隐私保护'), ('差分隐私'), ('联邦学习'), ('数据安全'),
('Graph Neural Networks'), ('GNN'), ('GCN'), ('Graph Representation'),
('气候变化'), ('生态系统'), ('生物多样性'), ('适应性策略'), ('碳排放'),
('强化学习'), ('自动驾驶'), ('决策系统'), ('深度强化学习'), ('CARLA'),
('新能源材料'), ('DFT'), ('分子动力学'), ('锂电池'), ('钙钛矿'),
('知识图谱'), ('知识推理'), ('信息抽取'), ('表示学习'),
('脑机接口'), ('神经科学'), ('人工智能'), ('伦理'), ('Neuralink'),
('区块链'), ('供应链金融'), ('智能合约'), ('联盟链'), ('金融科技'),
('AlphaFold'), ('蛋白质结构预测'), ('生物信息学'), ('药物发现'),
('教育数字化'), ('教育技术'), ('智慧教育'), ('在线学习'), ('人工智能教育'),
('Sentiment Analysis'), ('BERT'), ('NLP'), ('Attention Mechanism'), ('Pre-trained Models'),
('交通拥堵'), ('时空分析'), ('GPS轨迹'), ('图神经网络');

-- --------------------------------------------------------
-- 2.4 文献-关键词关联（72 条）
-- --------------------------------------------------------
DO $$
DECLARE
    kid INT;
BEGIN
    -- 文献1: 深度学习/自然语言处理/Transformer/神经网络/文本分类
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='深度学习';          INSERT INTO document_keyword VALUES(1,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='自然语言处理';      INSERT INTO document_keyword VALUES(1,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='Transformer';       INSERT INTO document_keyword VALUES(1,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='神经网络';          INSERT INTO document_keyword VALUES(1,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='文本分类';          INSERT INTO document_keyword VALUES(1,kid,1.0);

    -- 文献2
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='Medical Imaging';   INSERT INTO document_keyword VALUES(2,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='Deep Learning';     INSERT INTO document_keyword VALUES(2,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='CNN';               INSERT INTO document_keyword VALUES(2,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='Computer Vision';   INSERT INTO document_keyword VALUES(2,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='Diagnosis';         INSERT INTO document_keyword VALUES(2,kid,1.0);

    -- 文献3
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='量子计算';          INSERT INTO document_keyword VALUES(3,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='密码学';            INSERT INTO document_keyword VALUES(3,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='后量子密码';        INSERT INTO document_keyword VALUES(3,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='Shor算法';          INSERT INTO document_keyword VALUES(3,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='网络安全';          INSERT INTO document_keyword VALUES(3,kid,1.0);

    -- 文献4
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='大数据';            INSERT INTO document_keyword VALUES(4,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='隐私保护';          INSERT INTO document_keyword VALUES(4,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='差分隐私';          INSERT INTO document_keyword VALUES(4,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='联邦学习';          INSERT INTO document_keyword VALUES(4,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='数据安全';          INSERT INTO document_keyword VALUES(4,kid,1.0);

    -- 文献5
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='Graph Neural Networks'; INSERT INTO document_keyword VALUES(5,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='GNN';                   INSERT INTO document_keyword VALUES(5,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='GCN';                   INSERT INTO document_keyword VALUES(5,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='Deep Learning';         INSERT INTO document_keyword VALUES(5,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='Graph Representation';  INSERT INTO document_keyword VALUES(5,kid,1.0);

    -- 文献6
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='气候变化';          INSERT INTO document_keyword VALUES(6,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='生态系统';          INSERT INTO document_keyword VALUES(6,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='生物多样性';        INSERT INTO document_keyword VALUES(6,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='适应性策略';        INSERT INTO document_keyword VALUES(6,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='碳排放';            INSERT INTO document_keyword VALUES(6,kid,1.0);

    -- 文献7
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='强化学习';          INSERT INTO document_keyword VALUES(7,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='自动驾驶';          INSERT INTO document_keyword VALUES(7,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='决策系统';          INSERT INTO document_keyword VALUES(7,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='深度强化学习';      INSERT INTO document_keyword VALUES(7,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='CARLA';              INSERT INTO document_keyword VALUES(7,kid,1.0);

    -- 文献8
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='新能源材料';        INSERT INTO document_keyword VALUES(8,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='DFT';                INSERT INTO document_keyword VALUES(8,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='分子动力学';        INSERT INTO document_keyword VALUES(8,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='锂电池';            INSERT INTO document_keyword VALUES(8,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='钙钛矿';            INSERT INTO document_keyword VALUES(8,kid,1.0);

    -- 文献9
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='知识图谱';          INSERT INTO document_keyword VALUES(9,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='知识推理';          INSERT INTO document_keyword VALUES(9,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='信息抽取';          INSERT INTO document_keyword VALUES(9,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='自然语言处理';      INSERT INTO document_keyword VALUES(9,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='表示学习';          INSERT INTO document_keyword VALUES(9,kid,1.0);

    -- 文献10
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='脑机接口';          INSERT INTO document_keyword VALUES(10,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='神经科学';          INSERT INTO document_keyword VALUES(10,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='人工智能';          INSERT INTO document_keyword VALUES(10,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='伦理';              INSERT INTO document_keyword VALUES(10,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='Neuralink';          INSERT INTO document_keyword VALUES(10,kid,1.0);

    -- 文献11
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='区块链';            INSERT INTO document_keyword VALUES(11,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='供应链金融';        INSERT INTO document_keyword VALUES(11,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='智能合约';          INSERT INTO document_keyword VALUES(11,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='联盟链';            INSERT INTO document_keyword VALUES(11,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='金融科技';          INSERT INTO document_keyword VALUES(11,kid,1.0);

    -- 文献12
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='AlphaFold';          INSERT INTO document_keyword VALUES(12,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='蛋白质结构预测';    INSERT INTO document_keyword VALUES(12,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='深度学习';          INSERT INTO document_keyword VALUES(12,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='生物信息学';        INSERT INTO document_keyword VALUES(12,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='药物发现';          INSERT INTO document_keyword VALUES(12,kid,1.0);

    -- 文献13
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='教育数字化';        INSERT INTO document_keyword VALUES(13,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='教育技术';          INSERT INTO document_keyword VALUES(13,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='智慧教育';          INSERT INTO document_keyword VALUES(13,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='在线学习';          INSERT INTO document_keyword VALUES(13,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='人工智能教育';      INSERT INTO document_keyword VALUES(13,kid,1.0);

    -- 文献14
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='Sentiment Analysis';  INSERT INTO document_keyword VALUES(14,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='BERT';                 INSERT INTO document_keyword VALUES(14,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='NLP';                  INSERT INTO document_keyword VALUES(14,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='Attention Mechanism';  INSERT INTO document_keyword VALUES(14,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='Pre-trained Models';   INSERT INTO document_keyword VALUES(14,kid,1.0);

    -- 文献15
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='交通拥堵';          INSERT INTO document_keyword VALUES(15,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='时空分析';          INSERT INTO document_keyword VALUES(15,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='GPS轨迹';           INSERT INTO document_keyword VALUES(15,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='图神经网络';        INSERT INTO document_keyword VALUES(15,kid,1.0);
    SELECT keyword_id INTO kid FROM keywords WHERE keyword_name='深度学习';          INSERT INTO document_keyword VALUES(15,kid,1.0);
END $$;

-- --------------------------------------------------------
-- 2.5 引用关系（14 条）
-- --------------------------------------------------------
INSERT INTO citation (source_document_id, target_document_id) VALUES
(1,9), (1,14), (5,2), (5,9), (7,15), (3,4), (8,12), (9,1), (14,1),
(12,2), (10,6), (15,7), (4,11), (6,8);

-- --------------------------------------------------------
-- 2.6 收藏（14 条）
-- --------------------------------------------------------
INSERT INTO favorites (user_id, document_id) VALUES
(1,1), (1,9), (1,2), (1,5),
(2,5), (2,14), (2,1),
(3,7), (3,12), (3,4),
(4,6), (4,13),
(5,1), (5,11);

-- --------------------------------------------------------
-- 2.7 检索历史（18 条）
-- --------------------------------------------------------
INSERT INTO search_history (user_id, search_keyword, search_time) VALUES
(1, '深度学习',              NOW() - INTERVAL '1 day'),
(1, '自然语言处理',          NOW() - INTERVAL '2 days'),
(1, '知识图谱',              NOW() - INTERVAL '3 days'),
(1, '脑机接口',              NOW() - INTERVAL '4 days'),
(1, '自动驾驶',              NOW() - INTERVAL '5 days'),
(2, 'Graph Neural Networks', NOW() - INTERVAL '1 day'),
(2, 'Medical Image',         NOW() - INTERVAL '2 days'),
(2, 'Sentiment Analysis',    NOW() - INTERVAL '3 days'),
(2, 'NLP',                   NOW() - INTERVAL '4 days'),
(2, '深度学习',              NOW() - INTERVAL '5 days'),
(3, '强化学习',              NOW() - INTERVAL '1 day'),
(3, '量子计算',              NOW() - INTERVAL '2 days'),
(3, '蛋白质结构',            NOW() - INTERVAL '3 days'),
(4, '气候变化',              NOW() - INTERVAL '2 days'),
(4, '教育数字化',            NOW() - INTERVAL '3 days'),
(4, '新能源材料',            NOW() - INTERVAL '4 days'),
(5, '区块链',                NOW() - INTERVAL '1 day'),
(5, '金融科技',              NOW() - INTERVAL '2 days');

-- --------------------------------------------------------
-- 2.8 浏览历史（18 条）
-- --------------------------------------------------------
INSERT INTO browse_history (user_id, document_id, view_time) VALUES
(1, 1,  NOW() - INTERVAL '1 hour'),
(1, 9,  NOW() - INTERVAL '3 hours'),
(1, 3,  NOW() - INTERVAL '5 hours'),
(1, 4,  NOW() - INTERVAL '8 hours'),
(1, 5,  NOW() - INTERVAL '12 hours'),
(2, 5,  NOW() - INTERVAL '2 hours'),
(2, 14, NOW() - INTERVAL '4 hours'),
(2, 2,  NOW() - INTERVAL '10 hours'),
(2, 1,  NOW() - INTERVAL '24 hours'),
(3, 7,  NOW() - INTERVAL '3 hours'),
(3, 12, NOW() - INTERVAL '7 hours'),
(3, 3,  NOW() - INTERVAL '15 hours'),
(3, 1,  NOW() - INTERVAL '48 hours'),
(4, 6,  NOW() - INTERVAL '6 hours'),
(4, 13, NOW() - INTERVAL '10 hours'),
(4, 1,  NOW() - INTERVAL '24 hours'),
(5, 11, NOW() - INTERVAL '2 hours'),
(5, 1,  NOW() - INTERVAL '18 hours');

-- --------------------------------------------------------
-- 2.9 用户搜索统计
-- --------------------------------------------------------
INSERT INTO user_search_count (user_id, search_count) VALUES
(1, 45), (2, 32), (3, 28), (4, 19), (5, 8);

-- --------------------------------------------------------
-- 2.10 关键词搜索统计
-- --------------------------------------------------------
INSERT INTO keyword_search_count (keyword, search_count) VALUES
('深度学习', 87),
('自然语言处理', 65),
('知识图谱', 42),
('量子计算', 33),
('强化学习', 29),
('Graph Neural Networks', 25),
('区块链', 22),
('气候变化', 18),
('Medical Imaging', 16),
('蛋白质结构', 15);

-- ============================================================
-- 完成！验证数据：
-- SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;
-- SELECT COUNT(*) AS 用户数 FROM users;
-- SELECT COUNT(*) AS 文献数 FROM documents;
-- SELECT COUNT(*) AS 关键词数 FROM keywords;
-- 期望：17 张表，5 用户，15 文献，72 关键词
-- ============================================================
