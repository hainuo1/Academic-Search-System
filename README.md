# ============================================================
# 气象科学研究数据平台 — v5.0
# 基于 Vue 3 + Flask + MySQL 的前后端分离气象科学研究平台
# 南京农业大学 · 信息与计算科学专业
# ============================================================

---

## 项目概述

气象科学研究数据平台是一个面向大气科学研究的综合性 Web 平台，采用前后端分离架构——前端使用 Vue 3 + Vite 构建 SPA 单页应用，后端使用 Flask 提供 REST API 纯数据服务，前后端通过 HTTP + JSON 通信，JWT 无状态认证。

平台包含三大灾害观测模块和学术文献管理模块：

- **热带气旋观测分析**：基于 IBTrACS 国际最佳路径数据集，提供台风历史路径可视化、强度时序分析、风场结构展示及 DeepSeek AI 科学解读
- **地震数据分析**：基于 USGS 地震目录，提供地震事件查询、震中分布、震级-深度关系分析及 AI 灾害评估
- **龙卷风数据分析**：基于 NOAA SPC 龙卷风历史数据库，提供龙卷风事件查询、EF 等级分布、灾害影响评估及 AI 风险评估
- **学术文献检索与管理**：支持多维度文献检索、PDF 上传与全文提取、引文网络分析、文献收藏管理、检索浏览历史追踪及数据统计分析

---

## 核心功能

| 模块 | 功能描述 |
|:---|:---|
| 🌪️ **台风观测** | 路径可视化、强度时序分析、风圈展示、AI 科学解读、出行建议 |
| 🌍 **地震分析** | 地震事件查询、统计概览、邻近地震关联、AI 灾害评估 |
| 🌬️ **龙卷风分析** | 龙卷风事件查询、损害解析、区域统计、AI 风险评估 |
| 🔍 **文献检索** | 标题、作者、分类、关键词、全文五种维度检索 |
| 📄 **文献管理** | PDF 上传（自动提取全文）、编辑、删除，个人文献库 |
| ⭐ **文献收藏** | 一键收藏/取消，收藏列表分页 |
| 🔗 **引文分析** | 文献引用关系管理，引用网络查看 |
| 📊 **统计总览** | 高频关键词、活跃研究者、高被引文献等 TOP10 排行 |
| 📝 **使用记录** | 检索历史 + 浏览历史追踪 |
| 🔐 **用户认证** | 注册、登录、密码找回，JWT 无状态认证，登录失败锁定 |
| 🤖 **AI 分析** | 集成 DeepSeek 大语言模型，提供灾害智能科学解读 |

---

## 技术架构

```
浏览器 (localhost:5173)
    ↓
Vite 开发服务器 → Vue 3 SPA
    ↓ axios + JWT Token
Flask API Server (localhost:5000)
    ↓ PyMySQL
MySQL 数据库 (localhost:3306)
```

| 层级 | 技术栈 |
|:---|:---|
| 前端框架 | Vue 3（Composition API） |
| 前端构建 | Vite 6 |
| 前端路由 | Vue Router 4 |
| 状态管理 | Pinia 2 |
| HTTP 客户端 | axios |
| CSS 框架 | Tailwind CSS（CDN） |
| 地图可视化 | Leaflet.js + 高德瓦片 |
| 图表绘制 | Canvas 2D |
| 后端框架 | Flask 3.x（Blueprint 模块化） |
| 数据库 | MySQL 8.0 + PyMySQL |
| 认证 | JWT（PyJWT） |
| AI 接口 | DeepSeek API |
| PDF 解析 | pdfplumber |
| 跨域 | flask-cors |
| 一键启动 | AutoHotkey v2 |

---

## 快速开始

### 环境要求

| 组件 | 版本 |
|:---|:---|
| Python | 3.10+ |
| Node.js | 18+ (LTS) |
| npm | 9+ |
| MySQL | 8.0+ |
| AutoHotkey | v2.0（一键启动需要） |

### 数据库初始化

```sql
CREATE DATABASE AcademicSearchDB CHARACTER SET utf8mb4;
```

依次执行 `数据库相关文件/` 下的 SQL 文件：

```bash
mysql -u root -p AcademicSearchDB < "数据库相关文件/检索系统建表.sql"
mysql -u root -p AcademicSearchDB < "数据库相关文件/台风模块建表.sql"
mysql -u root -p AcademicSearchDB < "数据库相关文件/地震模块建表.sql"
mysql -u root -p AcademicSearchDB < "数据库相关文件/龙卷风模块建表.sql"
```

### 环境变量配置

复制 `.env.example` 为 `.env` 并填入实际值：

```bash
cp .env.example .env
```

需要配置的环境变量：

| 变量 | 必填 | 说明 |
|:---|:---|:---|
| `SECRET_KEY` | 否 | Flask 密钥（自动生成随机值） |
| `DB_HOST` | 否 | 数据库地址（默认 localhost） |
| `DB_PORT` | 否 | 数据库端口（默认 3306） |
| `DB_USER` | 否 | 数据库用户（默认 root） |
| `DB_PASSWORD` | **是** | 数据库密码 |
| `DB_NAME` | 否 | 数据库名（默认 AcademicSearchDB） |
| `DEEPSEEK_API_KEY` | 否 | DeepSeek API 密钥（AI 分析功能需要） |

### 数据导入

项目自带了三个 CSV 导入脚本，对应三个灾害模块：

```bash
# 台风数据（IBTrACS）
python import_typhoon_csv.py --file "热带气旋数据/ibtracs.ALL.list.v04r01.csv"

# 地震数据（USGS）
python import_earthquake_csv.py --dir "地震数据"

# 龙卷风数据（NOAA SPC）
python import_usgs_tornado_csv.py --file "龙卷风数据/1950-2024_actual_tornadoes.csv"
```

建议先 `--dry-run` 预览，确认后再正式导入。

### 启动

**方式一：一键启动（推荐）**

双击 `启动检索系统.ahk`

**方式二：手动启动**

后端：
```bash
cd backend
pip install -r requirements.txt
python app.py  # http://localhost:5000
```

前端：
```bash
cd frontend
npm install
npm run dev  # http://localhost:5173
```

浏览器访问 `http://localhost:5173/welcome`

---

## 项目结构

```
5.0版本/
├── README.md                          # 项目说明
├── LICENSE                            # MIT 许可证
├── .env.example                       # 环境变量模板
├── .gitignore                         # Git 忽略规则
├── 启动检索系统.ahk                    # AutoHotkey 一键启动脚本
├── requirements.txt                   # Python 依赖
│
├── import_typhoon_csv.py              # IBTrACS 台风数据导入脚本
├── import_earthquake_csv.py           # USGS 地震数据导入脚本
├── import_usgs_tornado_csv.py         # NOAA SPC 龙卷风数据导入脚本
│
├── 数据库相关文件/                     # 数据库 SQL
│   ├── 检索系统建表.sql
│   ├── 检索系统数据模拟生成.sql
│   ├── 台风模块建表.sql
│   ├── 地震模块建表.sql
│   └── 龙卷风模块建表.sql
│
├── 热带气旋数据/                       # 台风 CSV 数据（可选）
├── 地震数据/                           # 地震 CSV 数据（可选）
├── 龙卷风数据/                         # 龙卷风 CSV 数据（可选）
│
├── backend/                           # Flask API 后端
│   ├── app.py                         #   应用入口
│   ├── config.py                      #   集中配置（通过环境变量管理敏感信息）
│   ├── db.py                          #   数据库层（Row / RowCursor 包装）
│   ├── utils.py                       #   工具函数（JWT、分页、认证装饰器）
│   ├── captcha.py                     #   图形验证码生成
│   ├── uploads/                       #   PDF 存储目录（gitignored）
│   └── routes/                        #   蓝图路由（10 个模块）
│       ├── __init__.py
│       ├── auth.py                    #     用户认证（注册/登录/找回密码）
│       ├── search.py                  #     文献检索 + 浏览/检索历史
│       ├── document.py                #     文献 CRUD
│       ├── favorites.py               #     文献收藏
│       ├── citation.py                #     引文关系
│       ├── profile.py                 #     个人信息
│       ├── stats.py                   #     统计排行
│       ├── typhoon.py                 #     台风数据分析 + AI 分析
│       ├── earthquake.py              #     地震数据分析 + AI 分析
│       └── tornado.py                 #     龙卷风数据分析 + AI 分析
│
└── frontend/                          # Vue 3 前端
    ├── index.html                     #   浏览器入口
    ├── package.json                   #   前端依赖
    ├── vite.config.js                 #   Vite 配置
    └── src/
        ├── main.js                    #   Vue 启动器
        ├── App.vue                    #   根组件（导航栏 + 页脚）
        ├── api/index.js               #   axios 实例 + JWT 拦截器
        ├── router/index.js            #   路由表 + 守卫
        ├── stores/                    #   Pinia 状态管理
        │   └── auth.js                #     认证状态
        └── views/                     #   页面组件（20+）
            ├── WelcomeView.vue            # 欢迎首页
            ├── DashboardView.vue          # 功能入口面板
            ├── TyphoonView.vue            # 台风列表
            ├── TyphoonDetail.vue          # 台风详情（路径地图 + 强度图表 + AI）
            ├── EarthquakeView.vue         # 地震列表
            ├── EarthquakeDetail.vue       # 地震详情
            ├── TornadoView.vue            # 龙卷风列表
            ├── TornadoDetail.vue          # 龙卷风详情
            ├── LoginView.vue              # 登录
            ├── RegisterView.vue           # 注册
            ├── ForgotPasswordView.vue     # 找回密码
            ├── SearchView.vue             # 文献检索
            ├── DocumentView.vue           # 文献详情
            ├── UploadView.vue             # 文献上传
            ├── EditDocumentView.vue       # 文献编辑
            ├── MyDocumentsView.vue        # 个人文献库
            ├── FavoritesView.vue          # 文献收藏
            ├── HistoryView.vue            # 使用记录
            ├── StatsView.vue              # 统计总览
            ├── CitationView.vue           # 引文关系
            ├── ProfileView.vue            # 个人中心
            └── ErrorView.vue              # 404 错误
```

---

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](./LICENSE) 文件。

---

© 2026 南京农业大学 · 信息与计算科学专业

丁俊杰 · hainuo@stu.njau.edu.cn
