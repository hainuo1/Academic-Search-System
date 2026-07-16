# 学术文献检索系统

基于 Flask + MySQL 的学术文献管理与检索平台，支持 PDF 全文提取、多维度检索、引用关系管理和数据统计。

## 功能概览

- **用户系统** — 注册、登录、密码找回（安全问题 + 图形验证码），失败锁定保护
- **文献检索** — 标题 / 作者 / 分类 / 关键词 / 全文 五种检索方式，关键词高亮，高级筛选
- **文献管理** — 上传 PDF（自动提取全文）、下载、编辑元数据、删除（级联清理）
- **引用关系** — 设置文献间引用关系，查看被引列表
- **收藏功能** — 一键收藏 / 取消，AJAX 无刷新切换
- **历史记录** — 检索历史 + 浏览历史，独立分页，支持重新搜索
- **数据统计** — 热门关键词、活跃用户、高被引、浏览 / 下载 / 收藏排行（TOP 10）

## 技术栈

| 层级 | 技术 |
|:---|:---|
| 后端 | Python 3, Flask 3.x (Blueprint) |
| 数据库 | MySQL, PyMySQL, utf8mb4 |
| 前端 | Jinja2, Tailwind CSS CDN, Vanilla JS |
| PDF | pdfplumber (上传自动提取全文) |
| 密码 | Werkzeug Security (PBKDF2) |

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/hainuo1/AcademicSearchSystem.git
cd AcademicSearchSystem

# 安装依赖
pip install -r requirements.txt

# 设置数据库密码（或使用默认值）
# Windows PowerShell: $env:DB_PASSWORD="你的密码"
# Linux/Mac: export DB_PASSWORD="你的密码"

# 创建数据库（MySQL）
# 参考 数据库设计.md 中的建表语句

# 启动
python app.py
# 访问 http://127.0.0.1:5000
```

## 项目结构

```
├── app.py              # 应用工厂入口
├── config.py           # 集中配置
├── db.py               # 数据库连接管理（请求级复用）
├── captcha.py          # 图形验证码生成
├── utils.py            # 工具函数（分页、关键词处理）
├── requirements.txt
├── routes/             # 蓝图路由（7 个模块）
├── templates/          # Jinja2 模板（16 个页面）
├── static/             # CSS + JS 静态资源
├── uploads/            # PDF 存储（运行时自动创建）
├── 数据库设计.md        # 数据库设计文档
└── 项目各文件说明.md    # 项目文件详解
```

## 数据库

10 张表，MySQL InnoDB，外键约束保证数据完整性。核心 ER 关系详见 `数据库设计.md`。

## License

本项目为南京农业大学本科毕业设计作品，仅供学习参考。

## 作者

丁俊杰 · 南京农业大学理学院 · hainuo@stu.njau.edu.cn
