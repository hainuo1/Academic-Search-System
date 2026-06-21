

# 📚 AcademicSearchSystem —— 学术文献检索系统

> 基于 Flask + SQL Server 的轻量级学术文献管理平台  
> 南京农业大学 · 信息与计算科学专业 · 毕业设计

![Python|92](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.3-green.svg)
![SQL Server](https://img.shields.io/badge/SQL%20Server-2019-red.svg)

---

## 📖 项目概述

学术文献检索系统是一个基于 Web 的学术文献管理与检索平台，旨在为科研人员、高校师生提供便捷的文献检索与管理工具。系统采用 Flask 轻量级 Web 框架构建，后端使用 SQL Server 关系型数据库存储数据，前端采用 Tailwind CSS 实现现代化响应式界面。

系统支持文献上传、多维度检索、引用关系管理、收藏管理、历史记录追踪、数据统计分析等核心功能，可作为信息检索、数据库系统、Web 开发等课程的综合实践项目。

---

## ✨ 核心功能

| 模块          | 功能描述                                         |
| :---------- | :------------------------------------------- |
| 🔐 **用户认证** | 注册 / 登录 / 密码找回（安全问题 + 图形验证码），登录失败锁定机制        |
| 🔍 **智能检索** | 支持标题、作者、分类、关键词、**全文** 五种检索方式，并支持高级筛选（日期、分类等） |
| 📄 **文献管理** | 上传 PDF（自动提取全文）、下载、编辑、删除，个人文献库管理              |
| ⭐ **收藏系统**  | 一键收藏 / 取消收藏，我的收藏分页展示                         |
| 🔗 **引用关系** | 为文献添加引用关系，查看被引次数，追踪学术脉络                      |
| 📊 **数据统计** | 热门关键词、活跃用户、高被引文献、浏览次数 / 下载次数 / 收藏排行          |
| 🕒 **历史记录** | 检索历史 + 浏览历史，支持清空和快速重新搜索                      |
| 👤 **个人中心** | 修改邮箱 / 密码 / 安全问题（需验证当前密码）                    |

---

## 🛠️ 技术栈

- **后端框架**：Flask 3.1.3 + pyodbc
- **前端框架**：Tailwind CSS + Font Awesome + 原生 JavaScript
- **数据库**：SQL Server（2019 及以上）
- **PDF 解析**：pdfplumber（自动提取全文用于检索）
- **验证码生成**：Pillow（图形验证码）
- **密码加密**：Werkzeug（PBKDF2 哈希）
- **部署环境**：支持 Windows 本地部署，可迁移至 Linux

---

## 📁 系统架构

```text
AcademicSearchSystem
│
├── app.py                    # 程序入口，创建 Flask 应用
├── config.py                 # 配置文件（数据库连接、密钥、上传路径）
├── db.py                     # 数据库连接管理（请求级连接，自动关闭）
├── captcha.py                # 图形验证码生成工具
├── utils.py                  # 公共工具函数（关键词处理、分页计算）
├── requirements.txt          # 项目依赖清单
├── 项目各文件说明.md           # 项目文件功能详解文档
│
├── database/                 # 数据库脚本与设计文档
│   ├── 数据库设计.md          # 完整数据库设计文档（E-R图、表结构、约束）
│   └── 数据库表创建.sql       # 建表脚本（10张表，含主键/外键/唯一约束）
│
├── routes/                   # 蓝图模块（MVC 中的 Controller）
│   ├── auth.py               # 用户认证（登录 / 注册 / 找回密码）
│   ├── document.py           # 文献操作（上传 / 下载 / 编辑 / 删除）
│   ├── search.py             # 检索功能 + 历史记录管理
│   ├── citation.py           # 引用关系管理
│   ├── favorites.py          # 收藏功能
│   ├── profile.py            # 个人信息管理
│   └── stats.py              # 数据统计分析
│
├── templates/                # HTML 模板（MVC 中的 View）
│   ├── base.html             # 基础模板（导航栏 + 页脚）
│   ├── index.html            # 首页（打字机效果 + 功能介绍）
│   ├── login.html            # 登录页面
│   ├── register.html         # 注册页面
│   ├── forgot_password.html  # 找回密码页面
│   ├── search.html           # 检索页面（含高级筛选）
│   ├── document.html         # 文献详情页面
│   ├── upload.html           # 上传文献页面
│   ├── edit_document.html    # 编辑文献页面
│   ├── my_documents.html     # 我的文献列表
│   ├── favorites.html        # 我的收藏列表
│   ├── citation.html         # 设置引用关系页面
│   ├── history.html          # 历史记录页面
│   ├── profile.html          # 个人信息页面
│   ├── stats.html            # 数据统计页面
│   └── error.html            # 错误提示页面
│
├── static/                   # 静态资源
│   ├── css/
│   │   └── main.css          # 全局样式（含动画、交互效果）
│   └── js/
│       ├── app.js            # 全局 JS（折叠面板控制）
│       ├── captcha.js        # 验证码刷新交互
│       ├── citation.js       # 引用文献搜索
│       ├── document.js       # 收藏切换（异步 AJAX）
│       ├── favorites.js      # 取消收藏
│       ├── index.js          # 首页打字机效果
│       ├── search.js         # 搜索页交互
│       └── upload.js         # 上传页（日期选择 + 防重复提交）
│
└── uploads/                  # 上传的 PDF 文件存储目录（自动创建）
```

---

## 🗄️ 数据库设计

### 核心数据表

系统共包含 **10 张数据表**，设计遵循第三范式（3NF），确保数据一致性与完整性。

| 表名 | 说明 |
| :--- | :--- |
| **Users** | 用户信息表，存储账号、密码哈希、邮箱、安全问题与答案 |
| **Documents** | 文献信息表，存储标题、作者、摘要、分类、发表日期、文件路径、全文内容 |
| **Keywords** | 关键词表，存储所有关键词（去重） |
| **DocumentKeyword** | 文献-关键词映射表，建立文献与关键词的多对多关系，存储 TF-IDF 权重 |
| **SearchHistory** | 检索历史记录表，记录用户每次检索的关键词与时间 |
| **BrowseHistory** | 浏览历史记录表，记录用户每次查看的文献与时间 |
| **Citation** | 引用关系表，存储文献之间的引用网络（源文献 → 目标文献） |
| **Favorites** | 收藏表，记录用户收藏的文献 |
| **KeywordSearchCount** | 关键词搜索统计表，记录每个关键词被搜索的总次数（用于热门关键词排行） |
| **UserSearchCount** | 用户搜索统计表，记录每个用户的搜索总次数（用于活跃用户排行） |

### 表结构关系图

```mermaid
Users ||--o{ Documents : "上传"
Users ||--o{ Favorites : "收藏"
Users ||--o{ BrowseHistory : "浏览"
Users ||--o{ SearchHistory : "检索"
Users ||--o{ UserSearchCount : "统计"

Documents ||--o{ DocumentKeyword : "包含"
Keywords ||--o{ DocumentKeyword : "关联"

Documents ||--o{ Citation : "来源引用"
Documents ||--o{ Citation : "目标被引"

Users {
    int UserID PK
    string UserName UK
    string Password
    string Email UK
    string Question1
    string Answer1Hash
    string Question2
    string Answer2Hash
    int FailedAttempts
    datetime LockoutUntil
    datetime RegisterTime
}

Documents {
    int DocumentID PK
    string Title
    string Author
    string Abstract
    date PublishDate
    string Category
    string FilePath
    int UploadUserID FK
    datetime UploadTime
    int ViewCount
    int DownloadCount
    string KeywordsText
    string FullText
}

Keywords {
    int KeywordID PK
    string KeywordName UK
}

DocumentKeyword {
    int DocumentID PK,FK
    int KeywordID PK,FK
    float TF_IDF
}

Citation {
    int SourceDocumentID PK,FK
    int TargetDocumentID PK,FK
}

Favorites {
    int FavoriteID PK
    int UserID FK
    int DocumentID FK
    datetime CreateTime
}

BrowseHistory {
    int HistoryID PK
    int UserID FK
    int DocumentID FK
    datetime ViewTime
}

SearchHistory {
    int HistoryID PK
    int UserID FK
    string SearchKeyword
    datetime SearchTime
}

UserSearchCount {
    int UserID PK,FK
    int SearchCount
}

KeywordSearchCount {
    string Keyword PK
    int SearchCount
}
```

### 关键约束

- **主键约束**：每张表均设有自增主键（`ID` 或 `HistoryID` 等）
- **外键约束**：确保引用完整性（如 `Favorites.UserID` → `Users.UserID`）
- **唯一约束**：
  - `Users.UserName`（用户名唯一）
  - `Users.Email`（邮箱唯一）
  - `Keywords.KeywordName`（关键词唯一）
  - `Citation(SourceDocumentID, TargetDocumentID)`（引用关系唯一，禁止重复）
  - `Favorites(UserID, DocumentID)`（每个用户对同一文献只能收藏一次）

> **注**：当前版本暂未添加 `CHECK` 约束（如禁止自引用、TF-IDF 非负），由应用层代码保证数据一致性。生产环境如需强制校验，可自行添加。

### 索引建议（提升检索性能）

以下索引为性能优化建议，当前版本暂未在建表脚本中强制创建，可根据实际数据量按需添加：

```sql
-- 提升标题/作者/分类检索速度
CREATE INDEX IX_Documents_Title ON Documents(Title);
CREATE INDEX IX_Documents_Author ON Documents(Author);
CREATE INDEX IX_Documents_Category ON Documents(Category);
CREATE INDEX IX_Documents_PublishDate ON Documents(PublishDate);

-- 提升全文检索速度（需启用 SQL Server 全文索引）
-- CREATE FULLTEXT CATALOG ftCatalog AS DEFAULT;
-- CREATE FULLTEXT INDEX ON Documents(FullText) KEY INDEX PK_Documents;

-- 提升外键关联查询效率
CREATE INDEX IX_Documents_UploadUserID ON Documents(UploadUserID);
CREATE INDEX IX_Favorites_UserID ON Favorites(UserID);
CREATE INDEX IX_BrowseHistory_UserID ON BrowseHistory(UserID);
```

---

## 🔧 环境要求

### Python

```text
Python 3.10 或更高版本
```

### 数据库

```text
Microsoft SQL Server 2019 或更高版本（兼容 SQL Server 2016+）
```

### 操作系统

```text
Windows 10/11（开发环境）
Linux / macOS（可迁移部署，需配置 ODBC Driver 17/18）
```

---

## 📦 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/hainuo1/AcademicSearchSystem.git
cd AcademicSearchSystem
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

- 修改 `config.py` 中的 `DB_CONNECTION_STRING`，指向你的 SQL Server 实例。
- 在 SQL Server 中执行 `database/数据库表创建.sql`，自动创建数据库及所有表结构。

**Windows 身份验证示例：**

```python
DB_CONNECTION_STRING = (
    'DRIVER={SQL Server};'
    'SERVER=localhost;'
    'DATABASE=AcademicSearchDB;'
    'Trusted_Connection=yes;'
)
```

**SQL Server 身份验证示例：**

```python
DB_CONNECTION_STRING = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'
    'DATABASE=AcademicSearchDB;'
    'UID=your_username;'
    'PWD=your_password;'
)
```

> **提示**：如果你的 SQL Server 实例名称不是 `localhost`，请替换为实际的服务器名称（如 `destiny`）或 IP 地址。

### 4. 启动应用

```bash
python app.py
```

访问 `http://127.0.0.1:5000` 即可使用系统。

---

## 📌 分支说明

- **`main`**：当前最新版本（v2.0），包含所有新增功能与优化。
- **`v1.0`**：旧版本存档，保留原始代码与设计文档，便于回溯对比。

---

## 🔮 后续改进方向

未来可扩展的方向：

| 方向 | 描述 |
| :--- | :--- |
| 🔍 **Elasticsearch 全文检索** | 引入 Elasticsearch 替代 SQL LIKE，实现分词、模糊匹配、相关性排序 |
| 📄 **PDF 内容自动解析** | 完善 pdfplumber 集成，自动提取标题、作者、参考文献等结构化信息 |
| 📈 **TF-IDF 增量计算** | 新增文献时自动更新 TF-IDF 权重，替代固定的 1.0 |
| 🧠 **推荐算法** | 基于用户历史（检索、浏览、收藏）推荐相关文献 |
| 🕸️ **知识图谱** | 将引用关系可视化为知识图谱，展示学术脉络 |
| 🔧 **管理员后台** | 增加用户管理、文献审核、系统配置等管理员功能 |
| 🛡️ **RBAC 权限控制** | 基于角色的访问控制，区分普通用户与管理员 |
| 📱 **移动端适配** | 优化移动端界面，支持手机访问 |

---

## 🤝 贡献指南

本项目为个人毕业设计，欢迎提出建议或报告问题：

1. 在 GitHub 仓库中提交 **Issue**
2. 发送邮件至作者邮箱
3. 如有改进方案，欢迎提交 **Pull Request**

---

## 📬 联系方式

- **作者**：丁俊杰（hainuo1）
- **邮箱**：hainuo@stu.njau.edu.cn
- **GitHub**：[@hainuo1](https://github.com/hainuo1)
- **学校**：南京农业大学 · 信息与计算科学专业

---

## 📄 版权与使用声明

**版权所有 © 2026 丁俊杰（南京农业大学）**

本系统为南京农业大学信息与计算科学专业毕业设计作品，受《中华人民共和国著作权法》保护。

### 您被允许：
- ✅ **查看**：浏览、阅读本项目源代码及文档
- ✅ **转载**：在保留完整版权声明及原作者信息的前提下，转载本项目文档或代码片段
- ✅ **学习参考**：将本项目作为学习 Flask、数据库设计、Web 开发的参考资料

### 您被禁止：
- ❌ **商业使用**：不得将本系统或其任何部分用于商业目的
- ❌ **修改后发布**：不得对本项目进行修改、改编后以自己名义重新发布或提交
- ❌ **抄袭冒用**：严禁将本系统的设计思路、代码结构、界面布局等稍作修改后冒充为自己的原创作品，尤其在毕业设计、课程项目等学术场景中

### 学术诚信特别声明

> 本系统为作者独立完成的毕业设计作品。任何个人或组织若参考本项目进行毕业设计、课程项目或其他学术用途，**必须在参考文献或致谢中明确标注本项目的出处**，严禁整体或部分抄袭后作为自己的成果提交。

**转载时请注明出处**：
- GitHub 仓库：https://github.com/hainuo1/AcademicSearchSystem
- 作者：丁俊杰（hainuo1）
- 学校：南京农业大学 · 信息与计算科学专业

如需获得商业授权或合作使用，请联系作者：hainuo@stu.njau.edu.cn

---

**⭐ 如果这个项目对你有帮助，欢迎点亮 Star！**

**📌 查看旧版本（v1.0）：请切换至 `v1.0` 分支**
