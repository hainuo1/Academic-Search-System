# 📚 AcademicSearchSystem —— 学术文献检索系统

> 基于 Flask + SQL Server 的轻量级学术文献管理平台  
> 南京农业大学 · 信息与计算科学专业 · 毕业设计

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.3-green.svg)
![SQL Server](https://img.shields.io/badge/SQL%20Server-2019-red.svg)

---
## ✨ 核心功能
| 模块 | 功能描述 |
| :--- | :--- |
| 🔐 **用户认证** | 注册 / 登录 / 密码找回（安全问题 + 图形验证码），登录失败锁定机制 |
| 🔍 **智能检索** | 支持标题、作者、分类、关键词、**全文** 五种检索方式，并支持高级筛选（日期、分类等） |
| 📄 **文献管理** | 上传 PDF（自动提取全文）、下载、编辑、删除，个人文献库管理 |
| ⭐ **收藏系统** | 一键收藏 / 取消收藏，我的收藏分页展示 |
| 🔗 **引用关系** | 为文献添加引用关系，查看被引次数，追踪学术脉络 |
| 📊 **数据统计** | 热门关键词、活跃用户、高被引文献、浏览次数 / 下载次数 / 收藏排行 |
| 🕒 **历史记录** | 检索历史 + 浏览历史，支持清空和快速重新搜索 |
| 👤 **个人中心** | 修改邮箱 / 密码 / 安全问题（需验证当前密码） |

---
## 🛠️ 技术栈
- **后端**: Flask 3.1.3 + pyodbc
- **前端**: Tailwind CSS + Font Awesome + 原生 JavaScript
- **数据库**: SQL Server (2019 及以上)
- **PDF 解析**: pdfplumber (自动提取全文)
- **验证码**: Pillow (图形验证码)
- **部署**: 支持 Windows 本地部署（也可迁移至 Linux）

---
## 📦 快速开始
### 1. 克隆仓库

```bash
git clone https://github.com/hainuo1/AcademicSearchSystem.git
cd AcademicSearchSystem
```

### 2. 安装依赖

```
pip install -r requirements.txt
```

### 3. 配置数据库

- 修改 `config.py` 中的 `DB_CONNECTION_STRING`，指向你的 SQL Server 实例。
    
- 在数据库中执行 `学术搜索数据库表创建.sql` 创建所有表结构。

### 4. 启动应用

```bash
python app.py
```

访问 `http://127.0.0.1:5000` 即可使用。

---

## 📁 项目结构
```
AcademicSearchSystem/
├── app.py                 # 程序入口
├── config.py              # 配置文件（数据库连接、密钥等）
├── db.py                  # 数据库连接管理（请求级连接）
├── captcha.py             # 图形验证码生成
├── utils.py               # 公共工具函数（关键词处理、分页）
├── requirements.txt       # 依赖清单
├── routes/                # 蓝图模块
│   ├── auth.py            # 认证（登录/注册/找回密码）
│   ├── document.py        # 文献操作（上传/下载/编辑/删除）
│   ├── search.py          # 检索 + 历史记录
│   ├── citation.py        # 引用关系管理
│   ├── favorites.py       # 收藏功能
│   ├── profile.py         # 个人信息修改
│   └── stats.py           # 数据统计
├── templates/             # HTML 模板
│   ├── base.html          # 基础模板
│   ├── index.html         # 首页
│   ├── login.html         # 登录
│   ├── register.html      # 注册
│   ├── forgot_password.html # 找回密码
│   ├── search.html        # 检索页面
│   ├── document.html      # 文献详情
│   ├── upload.html        # 上传文献
│   ├── edit_document.html # 编辑文献
│   ├── my_documents.html  # 我的文献
│   ├── favorites.html     # 我的收藏
│   ├── citation.html      # 设置引用
│   ├── history.html       # 历史记录
│   ├── profile.html       # 个人信息
│   ├── stats.html         # 数据统计
│   └── error.html         # 错误页面
├── static/                # 静态资源
│   ├── css/
│   │   └── main.css       # 全局样式
│   └── js/
│       ├── app.js         # 全局 JS（折叠面板等）
│       ├── captcha.js     # 验证码刷新
│       ├── citation.js    # 引用搜索
│       ├── document.js    # 收藏切换
│       ├── favorites.js   # 取消收藏
│       ├── index.js       # 首页打字机效果
│       ├── search.js      # 搜索页（高亮等）
│       └── upload.js      # 上传页（日期选择+防重复提交）
└── uploads/               # 上传的 PDF 文件（自动创建）
```

---

## 🖼️ 界面预览

（如果你有系统截图，可以放在 `screenshots/` 文件夹下，然后在 README 里添加图片链接）

---

## 📌 分支说明

- **`main`**：当前最新版本（v2.0），包含所有新增功能和优化。
    
- **`v1.0`**：旧版本存档，保留所有原始代码，便于回溯。

---

## 🤝 贡献

本项目为个人毕业设计，欢迎提出建议或问题，请通过 Issues 或邮箱联系。

---

## 📬 联系方式

- 作者：丁俊杰（hainuo1）
    
- 邮箱：hainuo@stu.njau.edu.cn
    
- GitHub：[@hainuo1](https://github.com/hainuo1)
    

---

## 📄 许可

本项目仅供学习交流使用，未经授权不得用于商业用途。

---

**⭐ 如果这个项目对你有帮助，欢迎 Star！**
