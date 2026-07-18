; ============================================
;  气象科学研究数据平台 v5.0 — 一键启动器
;  双击此文件 → 启动后端 → 启动前端 → 打开浏览器
;  完成后脚本自动退出（前后端在各自命令行窗口运行）
;  关闭前端/后端：直接关闭对应的命令行窗口即可
; ============================================
#Requires AutoHotkey v2.0
#SingleInstance Force
SetWorkingDir A_ScriptDir

; ==================== 配置区 ====================
backDir  := "C:\Users\hainuo\Desktop\检索系统\5.0版本 - 副本\backend"
frontDir := "C:\Users\hainuo\Desktop\检索系统\5.0版本 - 副本\frontend"

; 如果你的 Python 使用 conda/虚拟环境，改为完整路径:
; pyCmd := "C:\Users\hainuo\anaconda3\python.exe"
pyCmd := "python"

browserUrl := "http://localhost:5173/welcome"
; ==============================================

; 1) 启动后端 Flask (端口 5000)
;    WorkingDir 参数设到项目目录，无需 cd /d，避免路径含空格的引号嵌套问题
Run(A_ComSpec ' /k "title 检索系统-后端 && echo [后端] 正在启动 Flask 服务... && ' pyCmd ' app.py"', backDir, 'Min')
Sleep(3000)

; 2) 启动前端 Vite (端口 5173)
Run(A_ComSpec ' /k "title 检索系统-前端 && echo [前端] 正在启动 Vite 开发服务器... && npm run dev"', frontDir, 'Min')
Sleep(2500)

; 3) 打开浏览器
Run(browserUrl)

ExitApp()
