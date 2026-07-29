-- ============================================================
-- 基础数据库初始化 SQL（全新部署用）
-- 气象科学研究数据平台 v6.1
-- 包含：建表 + 用户 + 分类标签 + 15种子文献 + 关键词
-- 执行后若要添加3000篇：python gen3000.py → 执行生成的SQL
-- ============================================================

-- ════════════════════════════════════════════════════════════
-- 1. 建表（18张表，PostgreSQL + PostGIS）
-- ════════════════════════════════════════════════════════════
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 1.1 用户表
CREATE TABLE IF NOT EXISTS users (
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

-- 1.2 文献表
CREATE TABLE IF NOT EXISTS documents (
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

-- 全文检索
ALTER TABLE documents ADD COLUMN IF NOT EXISTS full_text_tsv tsvector;
CREATE INDEX IF NOT EXISTS idx_documents_fulltext_tsv ON documents USING GIN (full_text_tsv);

CREATE OR REPLACE FUNCTION documents_tsv_trigger() RETURNS trigger AS $$
BEGIN
    NEW.full_text_tsv :=
        setweight(to_tsvector('simple', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('simple', COALESCE(NEW.abstract, '')), 'B') ||
        setweight(to_tsvector('simple', COALESCE(NEW.full_text, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_documents_tsv ON documents;
CREATE TRIGGER trg_documents_tsv BEFORE INSERT OR UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION documents_tsv_trigger();

-- 1.3 分类标签表
CREATE TABLE IF NOT EXISTS literature_categories (
    category_id   SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    sort_order    INT          NOT NULL DEFAULT 0,
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- 1.4 关键词表
CREATE TABLE IF NOT EXISTS keywords (
    keyword_id   SERIAL PRIMARY KEY,
    keyword_name VARCHAR(200) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS document_keyword (
    document_id INT REFERENCES documents(document_id) ON DELETE CASCADE,
    keyword_id  INT REFERENCES keywords(keyword_id) ON DELETE CASCADE,
    tf_idf      DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    PRIMARY KEY (document_id, keyword_id)
);

-- 1.5 引用表
CREATE TABLE IF NOT EXISTS citation (
    source_document_id INT REFERENCES documents(document_id) ON DELETE CASCADE,
    target_document_id INT REFERENCES documents(document_id) ON DELETE CASCADE,
    PRIMARY KEY (source_document_id, target_document_id),
    CHECK (source_document_id <> target_document_id)
);

-- 1.6 收藏表
CREATE TABLE IF NOT EXISTS favorites (
    favorite_id SERIAL PRIMARY KEY,
    user_id     INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    document_id INT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    create_time TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, document_id)
);

-- 1.7 检索历史
CREATE TABLE IF NOT EXISTS search_history (
    history_id     SERIAL PRIMARY KEY,
    user_id        INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    search_keyword VARCHAR(500) NOT NULL,
    search_time    TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 1.8 浏览历史
CREATE TABLE IF NOT EXISTS browse_history (
    browse_history_id SERIAL PRIMARY KEY,
    user_id           INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    document_id       INT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    view_time         TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 1.9 用户检索次数
CREATE TABLE IF NOT EXISTS user_search_count (
    user_id      INT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    search_count INT NOT NULL DEFAULT 0
);

-- 1.10 关键词检索次数
CREATE TABLE IF NOT EXISTS keyword_search_count (
    keyword      VARCHAR(200) PRIMARY KEY,
    search_count INT NOT NULL DEFAULT 0
);

-- 1.11 台风模块
CREATE TABLE IF NOT EXISTS typhoon_info (
    typhoon_id   VARCHAR(50) PRIMARY KEY,
    typhoon_name VARCHAR(100) NOT NULL,
    season       INTEGER NOT NULL,
    basin        VARCHAR(50) DEFAULT 'WP',
    max_wind     DOUBLE PRECISION DEFAULT 0,
    min_pressure DOUBLE PRECISION DEFAULT 9999,
    total_points INTEGER DEFAULT 0,
    start_time   TIMESTAMP NULL,
    end_time     TIMESTAMP NULL,
    track_geom   geometry(LineString, 4326) NULL
);
CREATE INDEX IF NOT EXISTS idx_typhoon_track_geom ON typhoon_info USING GIST (track_geom);

CREATE TABLE IF NOT EXISTS typhoon_track (
    track_id           SERIAL PRIMARY KEY,
    typhoon_id         VARCHAR(50) NOT NULL REFERENCES typhoon_info(typhoon_id) ON DELETE CASCADE,
    date_time          TIMESTAMP NOT NULL,
    latitude           DOUBLE PRECISION NOT NULL,
    longitude          DOUBLE PRECISION NOT NULL,
    max_sustained_wind DOUBLE PRECISION DEFAULT 0,
    min_pressure       DOUBLE PRECISION DEFAULT 9999,
    storm_category     VARCHAR(50) DEFAULT '',
    wind_radius7_ne    DOUBLE PRECISION DEFAULT 0,
    wind_radius7_se    DOUBLE PRECISION DEFAULT 0,
    wind_radius7_sw    DOUBLE PRECISION DEFAULT 0,
    wind_radius7_nw    DOUBLE PRECISION DEFAULT 0,
    wind_radius10_ne   DOUBLE PRECISION DEFAULT 0,
    wind_radius10_se   DOUBLE PRECISION DEFAULT 0,
    wind_radius10_sw   DOUBLE PRECISION DEFAULT 0,
    wind_radius10_nw   DOUBLE PRECISION DEFAULT 0
);

CREATE TABLE IF NOT EXISTS typhoon_ai_analysis (
    typhoon_id    VARCHAR(50) NOT NULL REFERENCES typhoon_info(typhoon_id) ON DELETE CASCADE,
    analysis_type VARCHAR(20) NOT NULL,
    content       TEXT NOT NULL,
    created_at    TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (typhoon_id, analysis_type)
);

-- 1.12 地震模块
CREATE TABLE IF NOT EXISTS earthquake_info (
    event_id         VARCHAR(30) PRIMARY KEY,
    date_time        TIMESTAMP NOT NULL,
    latitude         DOUBLE PRECISION NOT NULL,
    longitude        DOUBLE PRECISION NOT NULL,
    depth            DOUBLE PRECISION DEFAULT 0,
    magnitude        DOUBLE PRECISION DEFAULT 0,
    mag_type         VARCHAR(10) DEFAULT '',
    place            VARCHAR(300) DEFAULT '',
    status           VARCHAR(20) DEFAULT '',
    tsunami          INTEGER DEFAULT 0,
    alert            VARCHAR(20) DEFAULT '',
    significance     INTEGER DEFAULT 0,
    gap              DOUBLE PRECISION DEFAULT 0,
    dmin             DOUBLE PRECISION DEFAULT 0,
    rms              DOUBLE PRECISION DEFAULT 0,
    nst              INTEGER DEFAULT 0,
    horizontal_error DOUBLE PRECISION DEFAULT 0,
    depth_error      DOUBLE PRECISION DEFAULT 0,
    mag_error        DOUBLE PRECISION DEFAULT 0,
    mag_nst          INTEGER DEFAULT 0,
    updated          TIMESTAMP NULL,
    epicenter        geometry(Point, 4326) NULL
);
CREATE INDEX IF NOT EXISTS idx_earthquake_epicenter ON earthquake_info USING GIST (epicenter);

CREATE TABLE IF NOT EXISTS earthquake_ai_analysis (
    event_id      VARCHAR(30) NOT NULL REFERENCES earthquake_info(event_id) ON DELETE CASCADE,
    analysis_type VARCHAR(20) NOT NULL,
    content       TEXT NOT NULL,
    created_at    TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (event_id, analysis_type)
);

-- 1.13 龙卷风模块
CREATE TABLE IF NOT EXISTS tornado_info (
    event_id   SERIAL PRIMARY KEY,
    date_time  TIMESTAMP NOT NULL,
    latitude   DOUBLE PRECISION NOT NULL,
    longitude  DOUBLE PRECISION NOT NULL,
    place      VARCHAR(200) DEFAULT '',
    province   VARCHAR(50) DEFAULT '',
    ef_scale   VARCHAR(10) DEFAULT '',
    magnitude  INTEGER DEFAULT 0,
    casualties INTEGER DEFAULT 0,
    deaths     INTEGER DEFAULT 0,
    injuries   INTEGER DEFAULT 0,
    damage     VARCHAR(500) DEFAULT '',
    confidence VARCHAR(20) DEFAULT '',
    source     VARCHAR(100) DEFAULT '',
    geom       geometry(Point, 4326) NULL
);
CREATE INDEX IF NOT EXISTS idx_tornado_geom ON tornado_info USING GIST (geom);

CREATE TABLE IF NOT EXISTS tornado_ai_analysis (
    event_id      INTEGER NOT NULL REFERENCES tornado_info(event_id) ON DELETE CASCADE,
    analysis_type VARCHAR(20) NOT NULL,
    content       TEXT NOT NULL,
    created_at    TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (event_id, analysis_type)
);


-- ════════════════════════════════════════════════════════════
-- 2. 清空旧数据（按外键依赖顺序）
-- ════════════════════════════════════════════════════════════
TRUNCATE TABLE tornado_ai_analysis    RESTART IDENTITY CASCADE;
TRUNCATE TABLE tornado_info           RESTART IDENTITY CASCADE;
TRUNCATE TABLE earthquake_ai_analysis RESTART IDENTITY CASCADE;
TRUNCATE TABLE earthquake_info        RESTART IDENTITY CASCADE;
TRUNCATE TABLE typhoon_ai_analysis    RESTART IDENTITY CASCADE;
TRUNCATE TABLE typhoon_track          RESTART IDENTITY CASCADE;
TRUNCATE TABLE typhoon_info           RESTART IDENTITY CASCADE;
TRUNCATE TABLE keyword_search_count   RESTART IDENTITY CASCADE;
TRUNCATE TABLE user_search_count      RESTART IDENTITY CASCADE;
TRUNCATE TABLE browse_history         RESTART IDENTITY CASCADE;
TRUNCATE TABLE search_history         RESTART IDENTITY CASCADE;
TRUNCATE TABLE favorites              RESTART IDENTITY CASCADE;
TRUNCATE TABLE citation               RESTART IDENTITY CASCADE;
TRUNCATE TABLE document_keyword       RESTART IDENTITY CASCADE;
TRUNCATE TABLE keywords               RESTART IDENTITY CASCADE;
TRUNCATE TABLE documents              RESTART IDENTITY CASCADE;
TRUNCATE TABLE literature_categories  RESTART IDENTITY CASCADE;
TRUNCATE TABLE users                  RESTART IDENTITY CASCADE;


-- ════════════════════════════════════════════════════════════
-- 3. 导入用户（5人）
-- ════════════════════════════════════════════════════════════
INSERT INTO users (user_name, password, email, question1, answer1_hash, question2, answer2_hash) VALUES
('admin', 'scrypt:32768:8:1$JFGjzMinnDKGZbbL$537deda27121867bd7138d937fa72ac1df1a7de36ecf20f1173d96389509e29ef06424e1968a149ff1fd49d73727fd7294af41617d34ceb598e5d9cab19ffd8f', 'admin@example.com', '你最喜欢的城市？', 'scrypt:32768:8:1$5D4kQMmxUSsyfnvq$7e2edc47de8228529711e1c40dcf7d7f31c2fa2843dcfcca0f4df81b705beaa3b644d12aac50899bf1b2b3123d3b26898887a2554d153bf69be8593b15def50a', '你的小学名称？', 'scrypt:32768:8:1$I1vxxIbxtxyHrHs1$8e7ffe93d806563ed1567bb2d625c8bbe2bf4abc47218712d6a1ea23e7791df51a079bcc23f5ba7cf07e5e8a2a667b7d55eadb8abb0ca45e8e21d64bf40bf46b'),
('张三', 'scrypt:32768:8:1$kIMGQF4uzsZcJdOp$03fe6c872c4becc2e65e9397c8ed4cafb45c5081c949766dd5a2179c1e21ce61358b2aa853ecd1491016e153ddea69dd72eecfd7bd18e57f6f3d3b87ce8ddf8a', 'zhangsan@example.com', '你的生日是？', 'scrypt:32768:8:1$0BgevidtBxFGNHCs$81121992859e61611143c65d6ebe93872b0f066ee3b3800de62e5e1a2943ff0cff92e41edc0886be1874d933cee8d78232ca055918dfebfc63b6d5b2adc8180c', '你的宠物名字？', 'scrypt:32768:8:1$H5ZMqTdTudXTh2Oh$a4e3332be1e64944241534954dc4c2138a28ec170597916636f8514160fdbcc040c14f99a9be5b91d002bfd1dcaf987b30c21c72db5156d6fa0ae39fdc6a2741'),
('李四', 'scrypt:32768:8:1$zUUz4xGsw0gaRFPb$4596c699123d4f584003140f3cacb949ae3c669e2bf557d9e5e674f0763e990f1474ef47b41b0092979d15dc77c0c08dd49892ef982a202a75d9f7d9325c9289', 'lisi@example.com', '你的身份证后四位？', 'scrypt:32768:8:1$XDt4Ed6Y3tazVdTQ$11004df642039fab7bc92ae1301fbd5c6919c88263398be85cde537d7d1bda942c522c6d2e12dd3ac5968986605cf8d301630866cf8fdb555f463773bf837c52', '你喜欢吃什么？', 'scrypt:32768:8:1$uASLpD761Dg0dfpB$c6e9c9f208ff2b24b9ed3f45315b3094a2513b0f69971f6e3f21670119aaebaa67b8c8f3b075f5e57629a68d00684e4b879350eb00334ca02e1494c2e938c639'),
('王五', 'scrypt:32768:8:1$JsJdZBzE4gqtsRKU$87ae316232336cbe6514b11b28ea60c434a42563522d4d241e5d3badf9fb0758c13ac97270e782614accbaa07a10f972f490e5539073fee18c1c88a3880a167f', 'wangwu@example.com', '你的母亲名字？', 'scrypt:32768:8:1$w4lR1bBMgXDp4Fte$a694a8a780067fcd225b06dfa40046f7c2bda7b13b80c902ddf6077714c81accf457d588801fade12460991e84a38a407a02445cca39ae8c637548eff6455f20', '你的父亲名字？', 'scrypt:32768:8:1$8I4xeET69QzAgU2A$b54e6b0f7de08df2d94a54178609f5e0b6b25f035d69e52b01e0d9e68c8ce028715c2310c3c4773d57a03f7bd07c03e8542c8b5c7e78ca15d5997357781d403d'),
('testuser', 'scrypt:32768:8:1$bTUDILrERNPfDiVM$39f5575411a944cb0f8d434235cdd1d85c344ae528ba6fd6dfd8d48756da26690ec03d7c4c14630500a765410eebd8a1e6925c7300fa2d119a883a371742e963', 'test@example.com', '你的大学名称？', 'scrypt:32768:8:1$n6ftswAvmQhpDW5Y$15160f82ddb04a321826ce217133c8e3670774a98e60dfb16a60e841e3ed12c646d9f936f45620700e70a252b0c26f0bbc9dd4dd202f171c8581c5cb6c31a91f', '你的专业是什么？', 'scrypt:32768:8:1$64RYUXAjEdnX5QkW$88550ff50e1c8eb64f29e1793cea18ca7d20a0e75d0a4c99ce76a4b7fff4dc61f0f2b0f0ee7ba2a4b1a5f3e77ffeb0f9d00f8ed0415c678831b6395ce3fd1f45');


-- ════════════════════════════════════════════════════════════
-- 4. 导入140个分类标签
-- ════════════════════════════════════════════════════════════
INSERT INTO literature_categories (category_name, sort_order) VALUES
('大气科学',1),('大气物理学',2),('大气化学',3),('大气动力学',4),
('天气学',5),('气候学',6),('气候变化',7),('气候系统',8),
('地球系统科学',9),('季风研究',10),('边界层气象',11),('中尺度气象',12),
('高空气象',13),('城市气象',14),
('天气预报',20),('数值天气预报',21),('灾害天气',22),('极端天气事件',23),
('台风',24),('热带气旋',25),('龙卷风',26),('强对流天气',27),
('暴雨洪涝',28),('干旱',29),('寒潮',30),('高温事件',31),
('沙尘暴',32),('冰雹',33),('雷暴',34),('雷电灾害',35),('雾霾污染',36),
('气象观测',40),('地面观测',41),('高空气象观测',42),('气象雷达',43),
('天气雷达',44),('多普勒雷达',45),('卫星遥感',46),('气象卫星',47),
('遥感技术',48),('微波遥感',49),('激光雷达',50),('无人机气象观测',51),
('气象数据分析',60),('气象大数据',61),('数据同化',62),('模式模拟',63),
('数值模拟',64),('高性能计算',65),('科学计算',66),('机器学习气象应用',67),
('深度学习气象应用',68),('人工智能气象预测',69),('神经网络模型',70),
('时间序列分析',71),('统计气象学',72),
('海洋气象',80),('海气相互作用',81),('海洋科学',82),('环境科学',83),
('环境污染',84),('空气质量',85),('大气污染控制',86),('生态气象',87),
('农业气象',88),('水文气象',89),('冰冻圈科学',90),('极地气象',91),
('地球物理学',100),('地震学',101),('地质学',102),('地理信息系统',103),
('GIS技术',104),('空间信息科学',105),('自然灾害',106),('灾害风险评估',107),
('遥感监测',108),
('人工智能',120),('机器学习',121),('深度学习',122),('自然语言处理',123),
('计算机视觉',124),('数据挖掘',125),('数据库技术',126),('信息检索',127),
('软件工程',128),('云计算',129),('大数据技术',130),
('数学',140),('应用数学',141),('统计学',142),('概率论',143),
('随机过程',144),('偏微分方程',145),('数值分析',146),('物理学',147),
('流体力学',148),('热力学',149),('动力系统',150);


-- ════════════════════════════════════════════════════════════
-- 5. 导入15篇种子文献
-- ════════════════════════════════════════════════════════════
INSERT INTO documents (title, author, abstract, publish_date, category, file_path, upload_user_id, keywords_text, view_count, download_count) VALUES
('基于深度学习的自然语言处理综述','陈小明','深度学习技术近年来在自然语言处理领域取得了突破性进展。本文对卷积神经网络、循环神经网络、Transformer等主流架构在文本分类、命名实体识别、机器翻译、情感分析等任务中的应用进行了全面综述。','2024-03-15','人工智能,自然语言处理','',1,'深度学习;自然语言处理;Transformer;神经网络;文本分类',256,89),
('Machine Learning Approaches for Medical Image Analysis','Li Wei, Zhang Hua','Medical image analysis plays a critical role in modern clinical diagnosis. This paper reviews state-of-the-art machine learning and deep learning approaches for medical image segmentation, classification, and detection.','2024-01-20','人工智能,计算机视觉','',2,'Medical Imaging;Deep Learning;CNN;Computer Vision;Diagnosis',142,45),
('量子计算在密码学中的应用研究','王建国, 刘芳','量子计算的快速发展对传统密码学构成了重大挑战。Shor算法和Grover算法展示了量子计算机在破解RSA、ECC等公钥密码体系方面的潜力。本文系统梳理了后量子密码学的主要技术路线。','2024-05-10','人工智能,云计算','',3,'量子计算;密码学;后量子密码;Shor算法;网络安全',198,67),
('大数据环境下隐私保护技术研究','赵雪梅','随着大数据技术的广泛应用，数据隐私保护成为社会各界关注的焦点。本文深入分析了差分隐私、联邦学习、安全多方计算、同态加密等前沿隐私保护技术的原理和适用场景。','2024-02-28','大数据技术,软件工程','',1,'大数据;隐私保护;差分隐私;联邦学习;数据安全',173,52),
('A Survey of Graph Neural Networks','Yang Ming, Chen Fei','Graph Neural Networks have emerged as a powerful tool for learning on graph-structured data. This survey provides a comprehensive overview of GNN architectures including GCN, GAT, GraphSAGE.','2024-04-05','人工智能,机器学习','',2,'Graph Neural Networks;GNN;GCN;Deep Learning;Graph Representation',221,78),
('气候变化的生态系统影响与适应性策略','林海涛, 陈思远','全球气候变化已对陆地和水生生态系统产生深远影响。本文基于过去20年的观测数据和模型预测，分析了气温升高、降水模式改变和极端天气事件对生物多样性的影响。','2023-12-01','气候变化,环境科学','',4,'气候变化;生态系统;生物多样性;适应性策略;碳排放',88,21),
('强化学习在自动驾驶决策系统中的应用','张晓峰','自动驾驶技术的核心挑战之一是在复杂动态环境中做出安全高效的决策。本文探讨了深度强化学习在自动驾驶决策规划中的应用。','2024-06-18','人工智能,深度学习','',3,'强化学习;自动驾驶;决策系统;深度强化学习;CARLA',134,38),
('新能源材料的设计与计算模拟','刘阳, 孙浩然','第一性原理计算和分子动力学模拟在新能源材料开发中发挥着越来越重要的作用。本文综述了密度泛函理论、机器学习势函数等方法在锂离子电池电极材料等领域的应用。','2024-03-28','物理学,科学计算','',4,'新能源材料;DFT;分子动力学;锂电池;钙钛矿',67,15),
('知识图谱构建与推理技术综述','陈小明, 王建国','知识图谱作为一种结构化的语义知识库，在智能搜索、问答系统、推荐系统等领域发挥着关键作用。本文系统梳理了知识图谱的构建流程，并对比分析了基于符号逻辑和基于表示学习的知识推理方法。','2024-04-22','人工智能,信息检索','',1,'知识图谱;知识推理;信息抽取;自然语言处理;表示学习',180,56),
('脑机接口技术的发展现状与伦理思考','赵雪梅, 林海涛','脑机接口技术近年来取得了显著进展，从实验室逐渐走向临床应用。本文介绍了侵入式、半侵入式和非侵入式脑机接口技术的最新进展和伦理问题。','2024-05-30','人工智能,神经网络模型','',2,'脑机接口;神经科学;人工智能;伦理;Neuralink',110,33),
('区块链技术在供应链金融中的应用','刘芳','供应链金融面临信用传递困难、信息不对称和操作效率低等痛点。区块链技术以其去中心化、不可篡改和可追溯的特性，为供应链金融提供了创新解决方案。','2024-01-15','软件工程,数据库技术','',5,'区块链;供应链金融;智能合约;联盟链;金融科技',75,18),
('深度学习在蛋白质结构预测中的突破','孙浩然, 张晓峰','AlphaFold2的问世标志着蛋白质结构预测领域的革命性突破。本文深入解析了AlphaFold2的Evoformer架构、结构模块和端到端训练策略。','2024-02-10','深度学习,应用数学','',3,'AlphaFold;蛋白质结构预测;深度学习;生物信息学;药物发现',156,48),
('教育数字化转型的理论框架与实施路径','陈思远','教育数字化转型是全球教育改革的重要趋势。本文构建了包含数字基础设施、数字素养、数字内容和数字治理四个维度的教育数字化理论框架。','2024-06-01','人工智能,数据库技术','',4,'教育数字化;教育技术;智慧教育;在线学习;人工智能教育',45,9),
('Sentiment Analysis Using Pre-trained Language Models','Yang Ming, Liu Yang','Pre-trained language models such as BERT, RoBERTa, and GPT have achieved state-of-the-art results in various sentiment analysis tasks. We propose a novel attention fusion mechanism.','2024-04-15','自然语言处理,人工智能','',2,'Sentiment Analysis;BERT;NLP;Attention Mechanism;Pre-trained Models',189,62),
('城市交通拥堵的时空模式分析与预测','张晓峰, 刘阳','城市交通拥堵是困扰现代城市发展的全球性问题。本文基于大规模浮动车GPS轨迹数据，运用时空聚类分析、图神经网络和LSTM等方法对城市交通拥堵进行了系统建模。','2024-03-05','大数据技术,时间序列分析','',1,'交通拥堵;时空分析;GPS轨迹;图神经网络;深度学习',102,28);


-- ════════════════════════════════════════════════════════════
-- 6. 导入72个关键词 + 15篇文献的关联
-- ════════════════════════════════════════════════════════════
INSERT INTO keywords (keyword_name) VALUES
('深度学习'),('自然语言处理'),('Transformer'),('神经网络'),('文本分类'),
('Medical Imaging'),('Deep Learning'),('CNN'),('Computer Vision'),('Diagnosis'),
('量子计算'),('密码学'),('后量子密码'),('Shor算法'),('网络安全'),
('大数据'),('隐私保护'),('差分隐私'),('联邦学习'),('数据安全'),
('Graph Neural Networks'),('GNN'),('GCN'),('Graph Representation'),
('气候变化'),('生态系统'),('生物多样性'),('适应性策略'),('碳排放'),
('强化学习'),('自动驾驶'),('决策系统'),('深度强化学习'),('CARLA'),
('新能源材料'),('DFT'),('分子动力学'),('锂电池'),('钙钛矿'),
('知识图谱'),('知识推理'),('信息抽取'),('表示学习'),
('脑机接口'),('神经科学'),('人工智能'),('伦理'),('Neuralink'),
('区块链'),('供应链金融'),('智能合约'),('联盟链'),('金融科技'),
('AlphaFold'),('蛋白质结构预测'),('生物信息学'),('药物发现'),
('教育数字化'),('教育技术'),('智慧教育'),('在线学习'),('人工智能教育'),
('Sentiment Analysis'),('BERT'),('NLP'),('Attention Mechanism'),('Pre-trained Models'),
('交通拥堵'),('时空分析'),('GPS轨迹'),('图神经网络');

-- document_keyword 关联（document_id 1-15 对应 keyword_id 1-72）
INSERT INTO document_keyword (document_id, keyword_id, tf_idf) VALUES
(1,1,1.0),(1,2,1.0),(1,3,1.0),(1,4,1.0),(1,5,1.0),
(2,6,1.0),(2,7,1.0),(2,8,1.0),(2,9,1.0),(2,10,1.0),
(3,11,1.0),(3,12,1.0),(3,13,1.0),(3,14,1.0),(3,15,1.0),
(4,16,1.0),(4,17,1.0),(4,18,1.0),(4,19,1.0),(4,20,1.0),
(5,21,1.0),(5,22,1.0),(5,23,1.0),(5,24,1.0),
(6,25,1.0),(6,26,1.0),(6,27,1.0),(6,28,1.0),(6,29,1.0),
(7,30,1.0),(7,31,1.0),(7,32,1.0),(7,33,1.0),(7,34,1.0),
(8,35,1.0),(8,36,1.0),(8,37,1.0),(8,38,1.0),(8,39,1.0),
(9,40,1.0),(9,41,1.0),(9,42,1.0),(9,43,1.0),
(10,44,1.0),(10,45,1.0),(10,46,1.0),(10,47,1.0),(10,48,1.0),
(11,49,1.0),(11,50,1.0),(11,51,1.0),(11,52,1.0),(11,53,1.0),
(12,54,1.0),(12,55,1.0),(12,56,1.0),(12,57,1.0),
(13,58,1.0),(13,59,1.0),(13,60,1.0),(13,61,1.0),(13,62,1.0),
(14,63,1.0),(14,64,1.0),(14,65,1.0),(14,66,1.0),(14,67,1.0),
(15,68,1.0),(15,69,1.0),(15,70,1.0),(15,71,1.0);


-- ════════════════════════════════════════════════════════════
-- 7. 重建全文检索索引
-- ════════════════════════════════════════════════════════════
UPDATE documents SET full_text_tsv =
    setweight(to_tsvector('simple', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('simple', COALESCE(abstract, '')), 'B') ||
    setweight(to_tsvector('simple', COALESCE(full_text, '')), 'C');


-- ════════════════════════════════════════════════════════════
-- 8. 验证
-- ════════════════════════════════════════════════════════════
SELECT '用户' AS 数据项, COUNT(*) FROM users
UNION ALL SELECT '分类标签', COUNT(*) FROM literature_categories
UNION ALL SELECT '文献', COUNT(*) FROM documents
UNION ALL SELECT '关键词', COUNT(*) FROM keywords
UNION ALL SELECT '关联', COUNT(*) FROM document_keyword;
