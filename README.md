<div align="center">

# 🌦️ MeteoScholar · 气象科学研究数据平台

**v5.0 | 基于 Vue 3 + Flask + MySQL 的前后端分离科研数据平台**

[![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[功能特性](#-核心特性) · [系统架构](#️-系统架构) · [快速开始](#-快速开始) · [数据库设计](#️-数据库设计) · [数据来源](#-数据来源)

</div>

---

## 📖 项目简介

MeteoScholar 是一个面向大气科学研究领域的综合性 Web 平台，采用**前后端分离架构**——前端基于 Vue 3 + Vite 构建 SPA 单页应用，后端基于 Flask 提供 RESTful API，数据库使用 MySQL 8.0。

平台整合了**三大灾害观测数据分析模块**与**学术文献检索管理系统**，并集成 DeepSeek 大语言模型提供智能科学解读，旨在为气象研究者提供一站式的数据查询、可视化分析与文献管理工具。

---

## ✨ 核心特性

### 🌪️ 热带气旋观测分析

- 🗺️ **路径可视化**：基于 Leaflet + 高德瓦片，动态绘制台风历史移动路径
- 📈 **强度时序分析**：风速、气压双轴时序图，直观展示生命周期演变
- 🔵 **风圈结构展示**：七级/十级风圈四象限半径可视化
- 🤖 **AI 科学解读**：DeepSeek 自动生成台风趋势分析、影响评估与出行建议
- 📊 **年度统计**：按年份统计台风生成频次、强度分布

### 🌍 地震数据分析

- 🔍 **多条件检索**：按震级、时间、区域、深度多维筛选地震事件
- 🗺️ **震中分布地图**：全球/区域地震震中位置可视化
- 📉 **震级-深度关系分析**：散点图展示深度与震级相关性
- 🤖 **AI 灾害评估**：自动生成地震灾害等级与潜在影响分析

### 🌬️ 龙卷风数据分析

- 📋 **事件查询**：EF 等级、伤亡、损失金额多维度筛选
- 📊 **EF 等级分布统计**：各强度等级频次柱状图
- 🌎 **区域热力分析**：龙卷风高发区域统计
- 🤖 **AI 风险评估**：智能分析龙卷风灾害风险等级

### 🔍 学术文献检索与管理

- **五维检索**：标题、作者、分类、关键词、全文检索
- **PDF 智能上传**：自动提取全文内容，支持关键词关联
- **个人文献库**：上传、编辑、删除，私有文献管理
- ⭐ **收藏系统**：一键收藏/取消，分页浏览
- 🔗 **引文网络**：文献引用关系管理，构建研究脉络
- 📝 **使用追踪**：检索历史 + 浏览历史双记录
- 📊 **统计看板**：高频关键词、活跃研究者、高被引文献 TOP10 排行

### 🔐 用户与安全

- JWT 无状态认证，24 小时有效期
- 登录失败 5 次自动锁定 30 分钟
- 图形验证码防暴力破解
- 密码 PBKDF2 哈希存储，安全问题不可逆加密
- 邮箱脱敏显示，隐私保护

---

## 🏗️ 系统架构

```
                          ┌─────────────────────────┐
                          │         浏览器           │
                          │     (localhost:5173)     │
                          └────────────┬────────────┘
                                       │
                          ┌────────────▼────────────┐
                          │   Vue 3 SPA · Vite      │
                          │   Pinia · Vue Router     │
                          │   Tailwind · Leaflet     │
                          │   ECharts               │
                          └────────────┬────────────┘
                                       │ Axios + JWT
                          ┌────────────▼────────────┐
                          │ Flask API Server        │
                          │ (localhost:5000)        │
                          │ Blueprint · PyMySQL     │
                          │ pdfplumber · PyJWT      │
                          └─────┬──────────┬────────┘
                                │          │
                       ┌────────▼──┐  ┌────▼─────────┐
                       │ MySQL 8.0 │  │ DeepSeek API │
                       │ 12张业务表 │  │ AI 智能分析  │
                       └───────────┘  └──────────────┘
```

---

## 🛠️ 技术栈

| 层级 | 技术 | 版本 | 说明 |
|:---|:---|:---|:---|
| **前端框架** | Vue 3 | 3.5+ | Composition API，组件化开发 |
| 构建工具 | Vite | 6.x | 开发服务器 + HMR 热更新 |
| 路由管理 | Vue Router | 4.x | 前端路由 + 导航守卫 |
| 状态管理 | Pinia | 2.x | 全局状态（认证/消息提示） |
| HTTP 客户端 | Axios | 1.7+ | 统一请求封装，自动携带 Token |
| CSS 框架 | Tailwind CSS | — | CDN 引入，实用优先 |
| 地图可视化 | Leaflet.js | 1.9+ | 开源地图库 + 高德瓦片 |
| 图表库 | ECharts | 6.x | 专业数据可视化 |
| **后端框架** | Flask | 3.x | 轻量 Web 框架 + Blueprint |
| 数据库驱动 | PyMySQL | — | MySQL 连接驱动 |
| 认证方案 | PyJWT | — | JSON Web Token 无状态认证 |
| 密码加密 | Werkzeug | — | PBKDF2 哈希算法 |
| PDF 解析 | pdfplumber | — | PDF 全文文本提取 |
| AI 接口 | DeepSeek API | — | 大语言模型智能解读 |
| 跨域处理 | flask-cors | — | 前后端跨端口通信 |
| **数据库** | MySQL | 8.0+ | utf8mb4 字符集，InnoDB 引擎 |

---

## 🚀 快速开始

### 环境要求

| 组件 | 最低版本 |
|:---|:---|
| Python | 3.10+ |
| Node.js | 18 LTS |
| npm | 9+ |
| MySQL | 8.0+ |

### 1. 克隆项目

```bash
git clone https://github.com/hainuo1/Academic-Search-System.git
cd Academic-Search-System
```

### 2. 数据库初始化

```sql
CREATE DATABASE AcademicSearchDB CHARACTER SET utf8mb4;
```

依次执行建表 SQL：

```bash
mysql -u root -p AcademicSearchDB < "数据库相关文件/检索系统建表.sql"
mysql -u root -p AcademicSearchDB < "数据库相关文件/台风模块建表.sql"
mysql -u root -p AcademicSearchDB < "数据库相关文件/地震模块建表.sql"
mysql -u root -p AcademicSearchDB < "数据库相关文件/龙卷风模块建表.sql"
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

| 变量 | 必填 | 说明 |
|:---|:---|:---|
| `DB_PASSWORD` | ✅ | MySQL 数据库密码 |
| `SECRET_KEY` | — | Flask 密钥（默认自动生成随机值） |
| `DB_HOST` | — | 数据库地址（默认 localhost） |
| `DB_PORT` | — | 数据库端口（默认 3306） |
| `DB_USER` | — | 数据库用户（默认 root） |
| `DB_NAME` | — | 数据库名（默认 AcademicSearchDB） |
| `DEEPSEEK_API_KEY` | — | DeepSeek API 密钥（AI 功能需要） |

### 4. 导入灾害数据（可选）

项目自带三个数据导入脚本：

```bash
# 台风数据（IBTrACS）
python import_typhoon_csv.py --file "数据集/热带气旋/ibtracs.ALL.list.v04r01.csv"

# 地震数据（USGS）
python import_earthquake_csv.py --dir "数据集/地震"

# 龙卷风数据（NOAA SPC）
python import_usgs_tornado_csv.py --file "数据集/龙卷风/1950-2024_actual_tornadoes.csv"
```

💡 建议先加 `--dry-run` 参数预览导入数据量，确认后再正式执行。

### 5. 启动服务

**方式一：一键启动（Windows，推荐）**

双击 `启动检索系统.ahk`（需安装 AutoHotkey v2），自动启动前后端并打开浏览器。

**方式二：手动启动**

```bash
# 后端
cd backend
pip install -r requirements.txt
python app.py  # http://localhost:5000

# 前端（新开终端）
cd frontend
npm install
npm run dev  # http://localhost:5173
```

浏览器访问 `http://localhost:5173/welcome` 即可使用。

---

## 📁 项目结构

```
MeteoScholar/
├── README.md                          # 项目说明文档
├── LICENSE                            # MIT 开源许可证
├── .env.example                       # 环境变量模板
├── .gitignore                         # Git 忽略规则
├── requirements.txt                   # Python 依赖清单
├── 启动检索系统.ahk                    # AutoHotkey 一键启动脚本
│
├── import_typhoon_csv.py              # IBTrACS 台风数据导入脚本
├── import_earthquake_csv.py           # USGS 地震数据导入脚本
├── import_usgs_tornado_csv.py         # NOAA SPC 龙卷风数据导入脚本
│
├── 数据库相关文件/                     # 数据库 SQL 与设计文档
│   ├── 检索系统建表.sql                #   用户/文献/检索相关表
│   ├── 检索系统数据模拟生成.sql         #   模拟测试数据
│   ├── 台风模块建表.sql                #   热带气旋相关表
│   ├── 地震模块建表.sql                #   地震相关表
│   └── 龙卷风模块建表.sql              #   龙卷风相关表
│
├── 数据集/                             # 原始 CSV 数据（可选）
│   ├── 热带气旋/
│   ├── 地震/
│   └── 龙卷风/
│
├── backend/                           # Flask API 后端
│   ├── app.py                         #   应用入口，注册蓝图与中间件
│   ├── config.py                      #   集中配置管理
│   ├── db.py                          #   数据库连接层（Row 封装）
│   ├── utils.py                       #   工具函数（JWT/分页/鉴权）
│   ├── captcha.py                     #   图形验证码生成
│   └── routes/                        #   Blueprint 路由模块（10个）
│       ├── auth.py                    #     用户认证
│       ├── search.py                  #     文献检索 + 历史记录
│       ├── document.py                #     文献 CRUD
│       ├── favorites.py               #     收藏管理
│       ├── citation.py                #     引文关系
│       ├── profile.py                 #     个人中心
│       ├── stats.py                   #     统计排行
│       ├── typhoon.py                 #     台风模块
│       ├── earthquake.py              #     地震模块
│       └── tornado.py                 #     龙卷风模块
│
└── frontend/                          # Vue 3 前端
    ├── index.html                     #   HTML 入口
    ├── package.json                   #   依赖配置
    ├── vite.config.js                 #   Vite 构建配置
    └── src/
        ├── main.js                    #   Vue 应用入口
        ├── App.vue                    #   根组件（导航+布局）
        ├── api/index.js               #   Axios 封装 + 拦截器
        ├── router/index.js            #   路由表 + 守卫
        ├── stores/                    #   Pinia 状态管理
        │   ├── auth.js                #     认证状态
        │   └── flash.js               #     全局消息
        └── views/                     #   页面组件（20+）
            ├── WelcomeView.vue        #     欢迎首页
            ├── DashboardView.vue      #     功能面板
            ├── TyphoonView.vue        #     台风列表
            ├── TyphoonDetail.vue      #     台风详情（地图+图表+AI）
            ├── EarthquakeView.vue     #     地震列表
            ├── EarthquakeDetail.vue   #     地震详情
            ├── TornadoView.vue        #     龙卷风列表
            ├── TornadoDetail.vue      #     龙卷风详情
            ├── SearchView.vue         #     文献检索
            ├── DocumentView.vue       #     文献详情
            ├── UploadView.vue         #     文献上传
            ├── MyDocumentsView.vue    #     个人文献库
            ├── FavoritesView.vue      #     收藏列表
            ├── HistoryView.vue        #     使用历史
            ├── StatsView.vue          #     统计总览
            ├── CitationView.vue       #     引文管理
            ├── ProfileView.vue        #     个人中心
            ├── LoginView.vue          #     登录
            ├── RegisterView.vue       #     注册
            ├── ForgotPasswordView.vue #     找回密码
            └── ErrorView.vue          #     404 页面
```

---

## 🗄️ 数据库设计

共 12 张业务表，遵循第三范式（3NF）设计：

```
Users ───┬── Documents ───┬── DocumentKeyword ─── Keywords
         │                └── Citation (Source/Target)
         ├── Favorites
         ├── BrowseHistory
         ├── SearchHistory
         ├── UserSearchCount
         └── KeywordSearchCount

TyphoonInfo  ──── TyphoonTrack
EarthquakeInfo ── EarthquakeDetail
TornadoInfo   ─── TornadoTrack
```

详细表结构、字段说明、索引建议见 `数据库相关文件/` 目录下的设计文档。

---

## 📊 数据来源

| 模块 | 数据源 | 说明 |
|:---|:---|:---|
| 热带气旋 | IBTrACS v04r01 | NOAA 国际热带气旋最佳路径数据集 |
| 地震 | USGS Earthquake Catalog | 美国地质调查局地震目录 |
| 龙卷风 | NOAA SPC Tornado Database | 美国风暴预测中心龙卷风历史数据库 |

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

<div align="center">

© 2026 南京农业大学 · 信息与计算科学专业

丁俊杰 · hainuo@stu.njau.edu.cn

</div>
