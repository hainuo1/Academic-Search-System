
# 学术文献检索系统
基于 Flask + SQL Server 的学术文献检索系统，南京农业大学信息与计算科学专业毕业设计项目。

## 核心功能
- 用户注册/登录/密码找回/个人信息修改
- 多维度搜索（标题/作者/分类/关键词）+ 高级组合筛选 + 分页
- 文献上传/下载/删除/详情查看
- 文献引用关系管理与展示
- TF-IDF 关键词权重排序
- 文献收藏/检索历史自动清理
- 系统数据统计（热门关键词、高被引文献）

## 技术栈
- 后端：Python Flask
- 数据库：Microsoft SQL Server
- 前端：HTML + Tailwind CSS + JavaScript
- 核心算法：TF-IDF 文本相似度计算

## 本地部署步骤
1. 执行 `AcademicSearchDB表创建.sql` 创建数据库及表结构
2. 修改 `app.py` 中的数据库连接字符串，匹配本地SQL Server配置
3. 安装依赖：
   ```bash
   pip install flask pyodbc
