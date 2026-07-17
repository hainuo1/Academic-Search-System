@echo off
chcp 65001 >nul
echo ========================================
echo  学术文献检索系统 4.0 — Git 推送脚本
echo ========================================
echo.

cd /d "C:\Users\hainuo\Desktop\检索系统\4.0版本"

echo [1/5] 确保关联了远程仓库...
git remote -v | findstr "AcademicSearchSystem" >nul
if errorlevel 1 (
    echo 未找到远程仓库，正在添加...
    git remote add origin https://github.com/hainuo1/AcademicSearchSystem.git
) else (
    echo 远程仓库已关联 ✓
)

echo.
echo [2/5] 拉取远程最新状态...
git fetch origin

echo.
echo [3/5] 创建并切换到 v4.0.0 分支...
git checkout -b v4.0.0

echo.
echo [4/5] 添加所有文件到暂存区...
git add .

echo.
echo [5/5] 提交并推送到 GitHub...
git commit -m "v4.0.0: 前后端分离架构重构 — Vue 3 + Vite 前端，Flask REST API 后端，JWT 认证，MySQL 数据库"
git push -u origin v4.0.0

echo.
echo ========================================
echo  推送完成！
echo  访问: https://github.com/hainuo1/AcademicSearchSystem/tree/v4.0.0
echo ========================================
pause
