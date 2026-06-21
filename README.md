
# AcademicSearchSystem

基于 Flask + SQL Server 构建的学术文献检索系统。

南京农业大学信息与计算科学专业毕业设计项目。

本项目实现了用户管理、文献上传、多维度检索、引用关系管理、收藏管理、检索历史统计等核心功能，可作为信息检索、数据库系统、Web 开发等课程的综合实践项目。

---

# 项目概述

学术文献检索系统是一个基于 Web 的学术文献管理与检索平台，使用以下技术栈开发：

- Python Flask
- Microsoft SQL Server
- HTML / CSS / JavaScript
- pyodbc

系统支持的功能包括：

- 文献上传
- 元数据管理
- 关键词检索
- TF-IDF 排序
- 引用关系构建
- 收藏管理
- 检索历史记录
- 统计分析

---

# 系统架构

```text
AcademicSearchSystem
│
├── app.py
│
├── templates/
│   ├── base.html
│   ├── citation.html
│   ├── document.html
│   ├── error.html
│   ├── favorites.html
│   ├── forgot_password.html
│   ├── history.html
│   ├── index.html
│   ├── login.html
│   ├── my_documents.html
│   ├── profile.html
│   ├── register.html
│   ├── search.html
│   ├── stats.html
│   └── upload.html
│
├── uploads/
│
├── AcademicSearchDB表创建.sql
├── AcademicSearchDB数据库表的设计.md
├── requirements.txt
├── LICENSE
└── README.md
```

---

# 主要功能

## 1. 用户管理

- 用户注册
- 用户登录
- 密码找回
- 个人信息管理
- 邮箱修改
- 密码修改

---

## 2. 文献管理

- 上传 PDF 文档
- 查看文献详情
- 下载文献
- 删除个人文献

支持的元数据字段：

- 标题
- 作者
- 摘要
- 分类
- 发表日期
- 关键词

---

## 3. 文献检索

支持多种检索模式：

### 标题检索

按文献标题进行检索。

### 作者检索

按作者姓名进行检索。

### 分类检索

按文献分类进行检索。

### 关键词检索

基于以下数据关系：

```text
Documents
    ↓
DocumentKeyword
    ↓
Keywords
```

结合 TF-IDF 权重对检索结果按相关度排序。

### 高级检索

支持多条件组合筛选：

- 标题
- 作者
- 分类
- 关键词
- 起始日期
- 结束日期

---

## 4. 引用管理

用户可在文献之间创建引用关系。

功能包括：

- 引用搜索
- 引用选择
- 取消引用
- 引用次数统计

约束规则：

- 禁止自引用
- 禁止重复引用

---

## 5. 收藏管理

- 添加收藏
- 取消收藏
- AJAX 异步更新
- 分页展示

---

## 6. 检索历史

系统自动记录：

- 用户
- 检索关键词
- 检索时间

特性：

- 自动清理超出 100 条的记录
- 分页管理

---

## 7. 统计分析

- 热门检索关键词
- 活跃用户排行
- 高被引文献排行

---

# 数据库设计

## 核心数据表

| 表名 | 说明 |
| --- | --- |
| Users | 用户信息表 |
| Documents | 文献信息表 |
| Keywords | 关键词表 |
| DocumentKeyword | 文献-关键词映射表 |
| SearchHistory | 检索历史记录表 |
| Citation | 引用关系表 |
| Favorites | 用户收藏表 |

---

## 关键约束

- 主键约束
- 外键约束
- 唯一约束
- 检查约束

涉及字段：

```text
UserName
Email
KeywordName
(SourceDocumentID, TargetDocumentID)
(UserID, DocumentID)
```

其他约束：

```text
禁止自引用
TF-IDF >= 0
密码长度校验
邮箱格式校验
```

---

## 索引设计

```text
IX_Documents_Title
IX_Documents_Author
IX_Keywords_Name
IX_DocumentKeyword_KeywordID
IX_SearchHistory_UserID
IX_Citation_Source
IX_Citation_Target
IX_Favorites_UserID
IX_Favorites_DocumentID
```

索引用于提升大规模文献集合下的检索性能。

---

# 环境要求

## Python

```text
Python 3.11+
```

## 数据库

```text
Microsoft SQL Server
```

---

# 安装步骤

安装依赖：

```bash
pip install -r requirements.txt
```

---

# 部署指南

## 第一步：初始化数据库

执行 SQL 脚本：

```text
AcademicSearchDB表创建.sql
```

该脚本将自动完成以下操作：

- 创建数据库 AcademicSearchDB
- 创建所有数据表
- 创建约束
- 创建索引

---

## 第二步：配置数据库连接

修改 `app.py` 中的数据库连接字符串。

示例配置（Windows 身份验证）：

```python
conn = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=YOUR_SERVER_NAME;'
    'DATABASE=AcademicSearchDB;'
    'Trusted_Connection=yes;'
)
```

示例配置（SQL Server 身份验证）：

```python
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=YOUR_SERVER_NAME;'
    'DATABASE=AcademicSearchDB;'
    'UID=YOUR_USERNAME;'
    'PWD=YOUR_PASSWORD;'
)
```

---

## 第三步：运行应用

```bash
python app.py
```

在浏览器中打开：

```text
http://127.0.0.1:5000
```

---

# 当前版本

```text
版本号：v1.0 Freeze Release
```

状态：

```text
所有核心功能已实现
系统测试通过
项目已归档，用于毕业设计
```

---

# 后续改进方向

未来可扩展的方向：

- Elasticsearch 全文检索
- PDF 内容自动解析
- TF-IDF 自动增量计算
- 推荐算法
- 知识图谱构建
- 管理员后台
- 基于角色的访问控制（RBAC）

---

# 作者

学术文献检索系统

使用以下技术构建：

- Flask
- SQL Server
- HTML / CSS / JavaScript

用于学术信息检索与数据库系统课程实践。


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
