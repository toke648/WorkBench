@echo off
chcp 65001 >nul
title 刀剑神域 · 漫画阅读器
cd /d "%~dp0"
echo ============================================
echo   刀剑神域 漫画阅读器 正在启动...
echo   启动后请勿关闭本窗口（关闭即停止服务）
echo ============================================
echo.
start "" "http://localhost:8080"
node server.js
pause
