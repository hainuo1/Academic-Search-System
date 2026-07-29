# 气象科学研究数据平台 — v6.0
# 基于 Vue 3 + FastAPI + PostgreSQL + PostGIS 的前后端分离气象科学研究平台
# 南京农业大学 · 信息与计算科学专业

---

## 项目概述

气象科学研究数据平台是一个面向大气科学研究的综合性 Web 平台，采用前后端分离架构——前端使用 Vue 3 + Vite 构建 SPA 单页应用，后端使用 FastAPI 提供 REST API 纯数据服务，前后端通过 HTTP + JSON 通信，JWT 无状态认证。

平台包含三大灾害观测模块和学术文献管理模块：

- **热带气旋观测分析**：基于 IBTrACS 国际最佳路径数据集，提供台风历史路径可视化、强度时序分析、风场结构展示、PostGIS 空间密度统计及 DeepSeek AI 科学解读
- **地震数据分析**：基于 USGS 地震目录，提供全球地震事件查询、震中分布、区域地震活动趋势、震级-深度属性对比、PostGIS 邻近空间统计及 AI 灾害评估
- **龙卷风数据分析**：基于 NOAA SPC 龙卷风历史数据库（1950–2024），提供龙卷风事件查询、EF 等级频次分布、灾害影响评估、PostGIS 邻近密度分析及 AI 风险评估
- **学术文献检索与管理**：支持多维度文献检索（含 PostgreSQL tsvector 全文检索 + 中文兜底）、PDF 上传与全文提取、引文网络分析、文献收藏管理、检索浏览历史追踪及数据统计分析

---

## v6.0 重大升级（对比 5.0）

| 维度 | 5.0 (MySQL) | 6.0 (PostgreSQL + PostGIS) |
|:---|:---|:---|
| **后端框架** | Flask | **FastAPI**（async-ready, 自动 OpenAPI 文档） |
| **数据库** | MySQL 8.0 | **PostgreSQL + PostGIS**（空间分析能力） |
| **全文检索** | MySQL FULLTEXT | **PostgreSQL tsvector + GIN 索引 + 中文兜底** |
| **空间分析** | MySQL查询 | **PostGIS ST_DWithin**（台风 500km / 地震 300km / 龙卷风 100km 邻近密度分析） |
| **地图** | OpenStreetMap + 高德瓦片 | **OpenStreetMap + 高德瓦片**（按场景切换） |
| **图表** | Canvas 2D | **Canvas 2D**（自绘，无第三方依赖） |
| **认证** | PyJWT | **PyJWT 2.10**（UTC 时间标准化） |
| **配置管理** | 环境变量 | **pydantic-settings + `.env`**（集中管理，密钥不入库） |
| **数据导入** | 3 个独立脚本 | **1 个一键导入脚本**（含州名映射、坐标验证、批量 INSERT） |

---

## 核心功能

| 模块 | 功能描述 |
|:---|:---|
| 🌪️ **台风观测** | 路径可视化、强度时序分析、风圈展示、PostGIS 空间密度分析、AI 科学解读、出行建议 |
| 🌍 **地震分析** | 全球地震事件查询、震中分布、区域活动趋势、事件属性对比、PostGIS 邻近空间统计、AI 灾害评估 |
| 🌬️ **龙卷风分析** | 龙卷风事件查询（排序：EF等级↓ 死亡↓）、EF 等级频次分布、灾害记录解析、PostGIS 邻近密度分析、AI 风险评估 |
| 🔍 **文献检索** | 标题、作者、分类、关键词、全文五种维度检索 + PostgreSQL tsvector 全文检索 + ILIKE 中文兜底 + ts_rank 相关性排序 |
| 📄 **文献管理** | PDF 上传（自动提取全文）、编辑、删除，个人文献库 |
| ⭐ **文献收藏** | 一键收藏/取消，收藏列表分页 |
| 🔗 **引文分析** | 文献引用关系管理，引用网络查看 |
| 📊 **统计总览** | 高频关键词、活跃用户、高被引文献、浏览/下载/收藏排行 TOP10 |
| 📝 **使用记录** | 检索历史 + 浏览历史追踪，窗口化分页 |
| 🔐 **用户认证** | 注册、登录、密码找回（验证码 + 安全问答），JWT 无状态认证，登录失败锁定，找回密码安全信息不泄露 |
| 🤖 **AI 分析** | 集成 DeepSeek 大语言模型，按分析类型（趋势/风险/影响）prompt 工程，首次结果缓存 |

---

## 技术架构

```
浏览器 (localhost:5173)
    ↓
Vite 开发服务器 → Vue 3 SPA
    ↓ axios + JWT Bearer Token
FastAPI ASGI Server (localhost:5000)
    ↓ SQLAlchemy 2.0 + psycopg2
PostgreSQL + PostGIS (localhost:5432)
```

| 层级 | 技术 | 说明 |
|:---|:---|:---|
| **前端框架** | Vue 3.5（Composition API） | SPA 单页应用 |
| **前端构建** | Vite 6.0 | 极速 HMR 开发服务器 |
| **前端路由** | Vue Router 4.5 | 24 条路由 + 导航守卫 |
| **状态管理** | Pinia 2.3 | 轻量级响应式 store |
| **HTTP 客户端** | Axios 1.7 | JWT 拦截器 + 401 自动跳转 |
| **CSS 框架** | Tailwind CSS（CDN） | Utility-first 原子化 CSS |
| **图标库** | Font Awesome 4.7（CDN） | 矢量图标 |
| **地图可视化** | Leaflet 1.9 | OSM + 高德瓦片双底图 |
| **图表绘制** | Canvas 2D | 自绘柱状图、趋势图、频次图 |
| **后端框架** | FastAPI 0.115 | ASGI 异步框架 + 自动 OpenAPI 文档 |
| **ASGI 服务器** | Uvicorn 0.30 | 高性能 Python ASGI |
| **数据库** | PostgreSQL + PostGIS 3.x | 关系型 + 空间数据 |
| **ORM** | SQLAlchemy 2.0 + raw SQL | 混合模式：ORM 建模 + text() 查询 |
| **全文检索** | tsvector + GIN 索引 | PostgreSQL 原生全文检索（simple 分词 + 中文 ILIKE 兜底） |
| **认证** | PyJWT 2.10 + cryptography | HS256 JWT 无状态认证 |
| **配置管理** | pydantic-settings 2.5 | .env 环境变量自动加载，密钥不入库 |
| **AI 接口** | DeepSeek API（deepseek-chat） | Prompt 工程 + 结果缓存 |
| **PDF 解析** | pdfplumber 0.11 | 按页提取全文文本 |
| **验证码** | Pillow 10.4 | 服务端生成 CAPTCHA 图片 |
| **密码哈希** | Werkzeug ≥3.0.4 | scrypt 加密 |
| **跨域** | FastAPI CORSMiddleware | allow_credentials=True + 指定 origins |
| **空间扩展** | PostGIS + geoalchemy2 | geometry(Point/LineString/Polygon, 4326) + GIST 索引 |
| **一键启动** | AutoHotkey v2 | Windows 批处理启动脚本 |

---

## 快速开始

### 环境要求

| 组件 | 版本 | 说明 |
|:---|:---|:---|
| Python | 3.10+ | 后端运行环境 |
| Node.js | 18+ (LTS) | 前端构建环境 |
| npm | 9+ | 包管理器 |
| PostgreSQL | 15+ | 数据库（需预先安装好 PostGIS 扩展） |
| PostGIS | 3.x | 空间扩展 |

### 数据库初始化

1. 创建数据库：
```sql
CREATE DATABASE "AcademicSearchDB";
```

2. 启用 PostGIS 扩展（需超级用户权限，执行一次即可）：
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

3. 执行建库脚本（一键创建全部 17 张表 + 索引 + 触发器）：
```bash
psql -U postgres -d AcademicSearchDB -f "数据库文件/建表及模拟数据.sql"
```

4. 复制环境变量模板并填入实际值：
```bash
copy backend\.env.example backend\.env
```

需要修改的配置项：

| 变量 | 必填 | 说明 |
|:---|:---|:---|
| `SECRET_KEY` | **是** | JWT 签名密钥（建议用 `openssl rand -hex 32` 生成） |
| `DB_PASSWORD` | **是** | PostgreSQL 数据库密码 |
| `DEEPSEEK_API_KEY` | 否 | DeepSeek API 密钥（AI 分析功能需要） |

### 数据导入

使用一键导入脚本（导入台风 + 地震 + 龙卷风三个数据集）：

```bash
# 先设置数据库密码环境变量（Windows 命令行）
set DB_PASSWORD=你的数据库密码

# 执行一键导入
python 数据库导入文件.py
```

数据来源：

| 模块 | 数据文件 | 约记录数 | 来源 |
|:---|:---|:---|:---|
| 台风 | `数据集/热带气旋/ibtracs.ALL.list.v04r01.csv` | ~800,000 路径点 | IBTrACS v04r01 |
| 地震 | `数据集/地震/*.csv`（7 个年代文件） | ~80,000 条 | USGS Earthquake Catalog |
| 龙卷风 | `数据集/龙卷风/1950-2024_actual_tornadoes.csv` | ~70,000 条 | NOAA SPC |

### 启动

后端：
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
# API 文档自动生成于 http://localhost:5000/docs
```

前端：
```bash
cd frontend
npm install
npm run dev  # http://localhost:5173
```

浏览器访问 `http://localhost:5173/welcome`

可选：双击 `启动检索系统.ahk` 一键启动（Windows + AutoHotkey v2）。

---

## 项目结构

```
6.0版本/
├── README.md                              # 项目说明（本文件）
├── LICENSE                                # 许可证
├── .gitignore                             # Git 忽略规则
├── 启动检索系统.ahk                        # AutoHotkey 一键启动
├── 数据库导入文件.py                        # 三大数据集一键导入脚本
│
├── 数据库文件/                             # 数据库 SQL + 设计文档
│   ├── 建表及模拟数据.sql                   #   17 张表 DDL + 索引 + 触发器
│   └── 数据库设计.md                       #   E-R 图 + 17 张表详细说明
│   
│
├── 数据集/                                # 原始 CSV 数据
│   ├── 热带气旋/                           #   IBTrACS v04r01
│   ├── 地震/                              #   USGS（分年代 csv）
│   └── 龙卷风/                             #   NOAA SPC 1950-2024
│
├── backend/                               # FastAPI 后端
│   ├── .env                               #   环境变量（gitignored）
│   ├── .env.example                       #   环境变量模板
│   ├── requirements.txt                   #   Python 依赖
│   ├── app/
│   │   ├── main.py                        #     应用入口
│   │   ├── core/
│   │   │   ├── config.py                  #        pydantic-settings 配置
│   │   │   ├── database.py                #        SQLAlchemy engine + session
│   │   │   └── security.py                #        JWT 创建/验证/依赖注入
│   │   ├── models/__init__.py             #        ORM 模型（17 张表）
│   │   ├── schemas/__init__.py            #        Pydantic 请求/响应模型
│   │   ├── services/__init__.py           #        DeepSeek AI + 验证码生成
│   │   └── routers/
│   │       ├── auth.py                    #          登录/注册/找回密码/验证码
│   │       ├── search.py                  #          文献检索（tsvector 全文检索）
│   │       ├── document.py                #          文献 CRUD + PDF 下载
│   │       ├── favorites.py               #          文献收藏
│   │       ├── citation.py                #          引文关系管理
│   │       ├── profile.py                 #          个人信息修改
│   │       ├── stats.py                   #          统计排行 TOP10
│   │       ├── typhoon.py                 #          台风列表/详情/路径/AI
│   │       ├── earthquake.py              #          地震列表/详情/统计/AI
│   │       └── tornado.py                 #          龙卷风列表/详情/AI
│   └── uploads/                           #       PDF 存储目录（gitignored）
│
└── frontend/                              # Vue 3 前端
    ├── index.html
    ├── package.json                       #   前端依赖
    ├── vite.config.js                     #   Vite 配置
    └── src/
        ├── main.js                        #   Vue 启动器
        ├── App.vue                        #   根组件
        ├── api/index.js                   #   axios 实例 + JWT 拦截器
        ├── router/index.js                #   路由表（24 条）+ 导航守卫
        ├── stores/                        #   Pinia 状态管理
        │   ├── auth.js                    #     认证状态
        │   └── flash.js                   #     全局消息提示
        └── views/                         #   页面组件（24 个）
            ├── WelcomeView.vue                # 欢迎首页
            ├── DashboardView.vue              # 功能入口面板
            ├── LoginView.vue                  # 登录
            ├── RegisterView.vue               # 注册
            ├── ForgotPasswordView.vue         # 找回密码
            ├── TyphoonView.vue                # 台风列表
            ├── TyphoonDetail.vue              # 台风详情（路径+图表+空间密度+AI）
            ├── EarthquakeView.vue             # 地震列表
            ├── EarthquakeDetail.vue           # 地震详情（震中+趋势+对比+空间密度+AI）
            ├── TornadoView.vue                # 龙卷风列表
            ├── TornadoDetail.vue              # 龙卷风详情（位置+EF频次+空间密度+AI）
            ├── SearchView.vue                 # 文献检索
            ├── DocumentView.vue               # 文献详情
            ├── UploadView.vue                 # 文献上传
            ├── EditDocumentView.vue           # 文献编辑
            ├── MyDocumentsView.vue            # 个人文献库
            ├── FavoritesView.vue              # 文献收藏
            ├── HistoryView.vue                # 使用记录
            ├── StatsView.vue                  # 统计总览
            ├── CitationView.vue               # 引文关系
            ├── ProfileView.vue                # 个人中心
            └── ErrorView.vue                  # 404 错误页
```

---

## 数据库设计

17 张表，完整支持三大灾害模块 + 学术文献管理。含外键、唯一约束、CHECK 约束、触发器（自动维护 PostGIS geometry 列和 tsvector 全文检索向量）。

| 类别 | 表名 | 说明 |
|:---|:---|:---|
| 用户 | `users` | 注册用户（含安全问答、失败锁定机制） |
| 文献 | `documents` | 文献元数据 + 全文 + tsvector（GIN 索引） |
| 文献 | `keywords` | 关键词字典 |
| 文献 | `document_keyword` | 文献-关键词多对多关联 |
| 文献 | `citation` | 文献引用关系 |
| 文献 | `favorites` | 用户收藏 |
| 文献 | `search_history` / `browse_history` | 检索/浏览记录 |
| 文献 | `user_search_count` / `keyword_search_count` | 搜索统计 |
| 台风 | `typhoon_info` | 台风基本信息 + PostGIS LineString 轨迹线 |
| 台风 | `typhoon_track` | 台风路径观测点 + PostGIS Point |
| 台风 | `typhoon_ai_analysis` | AI 分析缓存 |
| 地震 | `earthquake_info` | 地震事件 + PostGIS Point 震中 |
| 地震 | `earthquake_ai_analysis` | AI 分析缓存 |
| 龙卷风 | `tornado_info` | 龙卷风事件 + PostGIS Point 地点 |
| 龙卷风 | `tornado_ai_analysis` | AI 分析缓存 |

详见 `数据库文件/数据库设计.md`

---

© 2026 南京农业大学 · 信息与计算科学专业

丁俊杰 · hainuo@stu.njau.edu.cn
