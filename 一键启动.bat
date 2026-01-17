@echo off
chcp 65001 >nul 2>&1

echo ============================================
echo 自动化公众号写稿系统 - 一键启动
echo ============================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python
    echo 请先安装 Python 3.8 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/2] 启动 Python 服务器...
echo.

REM 启动 Python 服务器（后台运行）
start /B python app.py

REM 等待服务器启动
echo 等待服务器启动...
timeout /t 3 /nobreak >nul

echo.
echo [2/2] 打开浏览器...
echo.

REM 打开启动器页面
start "" "启动器.html"

echo.
echo ============================================
echo 系统已启动！
echo ============================================
echo.
echo 如果浏览器没有自动打开，请手动访问：
echo http://localhost:5000
echo.
echo 提示：关闭此窗口不会影响系统运行
echo ============================================
echo.

REM 询问是否保持窗口打开
echo 按任意键关闭此窗口（服务器继续运行）...
pause >nul
