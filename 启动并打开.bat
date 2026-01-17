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

echo [1/2] 启动 Flask 后台服务...
echo.

REM 启动 Flask 服务（在新窗口中运行，这样用户可以看到日志）
start "公众号写稿系统 - 后台服务" cmd /k "python app.py"

REM 等待服务启动
echo 等待服务启动...
timeout /t 3 /nobreak >nul

echo.
echo [2/2] 打开应用界面...
echo.

REM 打开应用界面
start "" http://localhost:5000

echo.
echo ============================================
echo 系统已启动！
echo ============================================
echo.
echo 后台服务运行在单独的窗口中
echo 请不要关闭后台服务窗口
echo.
echo 如果浏览器没有自动打开，请手动访问：
echo http://localhost:5000
echo.
echo ============================================
echo.
echo 按任意键关闭此窗口（后台服务继续运行）...
pause >nul
