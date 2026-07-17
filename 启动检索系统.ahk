; ============================================
;  学术检索系统 4.0 — 一键启动器
;  双击此文件 → 启动后端 → 启动前端 → 打开浏览器
;  完成后脚本自动退出（前后端在各自命令行窗口运行）
;  关闭前端/后端：直接关闭对应的命令行窗口即可
; ============================================
#Requires AutoHotkey v2.0
#SingleInstance Force
SetWorkingDir A_ScriptDir

; ==================== 配置区 ====================
backDir  := "C:\Users\hainuo\Desktop\检索系统\4.0版本\backend"
frontDir := "C:\Users\hainuo\Desktop\检索系统\4.0版本\frontend"

; 如果你的 Python 使用 conda/虚拟环境，改为完整路径:
; pyCmd := "C:\Users\hainuo\anaconda3\python.exe"
pyCmd := "python"

browserUrl := "http://localhost:5173/welcome"
; ==============================================

; 1) 启动后端 Flask (端口 5000)
Run(A_ComSpec ' /k "title 检索系统-后端 && cd /d ' backDir ' && echo [后端] 正在启动 Flask 服务... && ' pyCmd ' app.py"', , 'Min')
Sleep(3000)

; 2) 启动前端 Vite (端口 5173)
Run(A_ComSpec ' /k "title 检索系统-前端 && cd /d ' frontDir ' && echo [前端] 正在启动 Vite 开发服务器... && npm run dev"', , 'Min')
Sleep(2500)

; 3) 打开浏览器
Run(browserUrl)

ExitApp()
