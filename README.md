# 📚 AcademicSearchSystem 4.0 —— 学术文献检索系统

> 基于 Vue 3 + Flask + MySQL 的前后端分离学术文献管理平台
> 南京农业大学 · 信息与计算科学专业 · 毕业设计

![Vue](https://img.shields.io/badge/Vue-3.5-green.svg)  ![Flask](https://img.shields.io/badge/Flask-3.1-blue.svg)  ![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)

---

## 📖 项目概述

学术文献检索系统是一个基于 Web 的学术文献管理与检索平台，4.0 版本在架构上彻底升级为**前后端分离**架构——前端使用 Vue 3 + Vite 构建 SPA 单页应用，后端使用 Flask 提供 REST API 纯数据服务，前后端通过 HTTP + JSON 通信，JWT 无状态认证。

系统支持文献上传、多维度检索、引用关系管理、收藏管理、历史记录追踪、数据统计分析等核心功能。

---

## ✨ 核心功能

| 模块 | 功能描述 |
|:---|:---|
| 🏠 **欢迎首页** | 系统介绍 + 功能卡片 + 登录/注册入口，无需登录即可浏览 |
| 🔐 **用户认证** | 注册 / 登录 / 密码找回（安全问题 + 图形验证码），JWT 无状态认证，登录失败锁定机制 |
| 🔍 **智能检索** | 5 种检索方式 + 高级筛选（日期/分类）+ 分类浏览，搜索关键词高亮 |
| 📄 **文献管理** | 上传 PDF（自动提取全文）、下载、编辑、删除，个人文献库 |
| ⭐ **收藏系统** | 一键收藏/取消收藏，收藏列表分页 |
| 🔗 **引用分析** | 设置文献引用关系，搜索可引用文献，查看引用网络 |
| 📊 **数据统计** | 6 类 TOP10 排行：热门关键词、活跃用户、高被引、高浏览、高下载、高收藏 |
| 📝 **历史记录** | 检索历史 + 浏览历史，支持点击关键词重新搜索 |

---

## 🏗️ 技术架构

```
浏览器 (localhost:5173)
    ↓
Vite 开发服务器 → Vue 3 SPA
    ↓ axios + JWT Token (Authorization Header)
Flask API Server (localhost:5000)
    ↓ PyMySQL
MySQL 数据库 (localhost:3306)
```

| 层级 | 技术 | 说明 |
|:---|:---|:---|
| 前端框架 | Vue 3（Composition API） | `<script setup>` 语法，单文件组件（SFC） |
| 前端构建 | Vite 6 | 开发服务器 (5173)，热更新，生产打包 |
| 前端路由 | Vue Router 4 | 15 个路由，前端路由守卫 |
| 状态管理 | Pinia 2 | auth（用户状态）+ flash（消息提示） |
| HTTP 客户端 | axios | 请求拦截自动带 Token，响应拦截 401 自动跳转 |
| CSS | Tailwind CSS（CDN） | 实用优先样式框架 |
| 后端框架 | Flask 3.x | Blueprint 模块化路由，仅返回 JSON |
| 数据库 | MySQL 8.0 | PyMySQL 驱动，utf8mb4 |
| 认证 | JWT（PyJWT） | 24h 过期，@login_required 装饰器 |
| 跨域 | flask-cors | 允许 localhost:5173 → 5000 |
| 一键启动 | AutoHotkey v2 | 双击启动前后端 + 打开浏览器 |

---

## 🚀 快速开始

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

然后运行项目附带的 `数据库设计.md` 中的建表 SQL，或在 MySQL 客户端中执行。

修改 `backend/config.py` 中的数据库密码，或设置环境变量：
```bash
set DB_PASSWORD=你的密码    # Windows
export DB_PASSWORD="你的密码"  # macOS / Linux
```

### 方式一：AutoHotkey 一键启动（推荐）

双击 `启动检索系统.ahk` → 自动启动后端 → 启动前端 → 打开浏览器。

### 方式二：手动启动

**后端：**
```bash
cd backend
pip install -r requirements.txt
python app.py          # http://localhost:5000
```

**前端：**
```bash
cd frontend
npm install            # 首次运行
npm run dev            # http://localhost:5173
```

浏览器访问 `http://localhost:5173/welcome`

---

## 📂 项目结构

```
检索系统4.0/
├── README.md
├── requirements.txt           # Python 后端依赖
├── .gitignore
├── 启动检索系统.ahk            # AutoHotkey 一键启动
├── 项目各文件说明.md            # 文件结构 + 模块说明
├── 数据库设计.md               # ER 图 + 10 张表结构 + 约束
│
├── backend/                   # Flask API 后端
│   ├── app.py                 #   入口：创建应用、注册蓝图、配置 CORS
│   ├── config.py              #   配置：密钥、数据库、上传限制
│   ├── db.py                  #   数据库层：连接管理 + Row 封装
│   ├── utils.py               #   工具箱：JWT、分页、@login_required
│   ├── captcha.py             #   图形验证码
│   ├── requirements.txt
│   ├── uploads/               #   PDF 存储
│   └── routes/                #   7 个蓝图路由
│       ├── auth.py            #     认证（登录/注册/找回密码）
│       ├── search.py          #     检索 + 历史
│       ├── document.py        #     文献 CRUD
│       ├── favorites.py       #     收藏
│       ├── citation.py        #     引用关系
│       ├── profile.py         #     个人信息
│       └── stats.py           #     统计排行
│
└── frontend/                  # Vue 3 前端
    ├── index.html             #   浏览器入口
    ├── package.json           #   前端依赖
    ├── vite.config.js         #   Vite 配置
    └── src/
        ├── main.js            #   Vue 启动器
        ├── App.vue            #   根组件（导航栏 + 页脚）
        ├── api/index.js       #   axios 实例 + 拦截器
        ├── router/index.js    #   路由表 + 守卫
        ├── stores/            #   Pinia 状态管理
        └── views/             #   15 个页面组件
```

---

## 🔗 配套文档

本项目的开发手册已随仓库提供，分为两篇：

- [🌐 现代 Web 开发参考手册（第一篇）：传统后端渲染时代](./🌐%20现代%20Web%20开发参考手册（第一篇）.md) — Web 基础概念，HTML/CSS/JS，HTTP，数据库，传统后端渲染全流程
- [🌐 现代 Web 开发参考手册（第二篇）：前后端分离时代](./🌐%20现代%20Web%20开发参考手册（第二篇）.md) — 前后端分离架构，Vue 3 实战，JWT 认证，工程化部署

---

## 📄 版权

© 2026 南京农业大学 · 信息与计算科学专业 · 毕业设计项目

**⭐ 如果这个项目对你有帮助，欢迎点亮 Star！**
