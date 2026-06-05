@echo off
chcp 65001 >nul
echo ================================================
echo   贵港旅游智能助手 v4.0 - 启动脚本
echo ================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖
echo [1/3] 检查依赖包...
pip install -q flask requests simplejson
if %errorlevel% neq 0 (
    echo [警告] 部分依赖包安装失败，可能影响功能
)

REM 启动Flask服务
echo.
echo [2/3] 启动Flask服务...
echo ------------------------------------------------
echo   服务地址: http://localhost:5001
echo   公网地址: http://64010bd1.r5.cpolar.top
echo              https://64010bd1.r5.cpolar.top
echo ------------------------------------------------
echo.
echo [提示] 按 Ctrl+C 停止服务
echo [提示] 首次访问可能需要等待几秒
echo.
echo ================================================
echo   正在启动...
echo ================================================
echo.

cd /d %~dp0
python app.py

pause
