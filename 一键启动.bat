@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

title 公众号写稿系统 - 启动中...

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    cls
    echo ============================================
    echo 错误：未找到 Python
    echo ============================================
    echo.
    echo 请先安装 Python 3.8 或更高版本
    echo.
    echo 下载地址：https://www.python.org/downloads/
    echo.
    echo 安装时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   公众号写稿系统 - 正在启动
echo ============================================
echo.

REM 检查是否已经在运行
tasklist /FI "WINDOWTITLE eq 公众号写稿系统 - 后台服务*" 2>nul | find /c "cmd.exe" >nul
if %errorlevel% gtr 0 (
    echo [检测] 后台服务已在运行
    echo.
    echo 直接打开应用界面...
    echo.
    start "" http://localhost:5000
    goto :end
)

echo [1/3] 启动 Flask 后台服务...
echo.

REM 在最小化窗口中启动服务
start /MIN "公众号写稿系统 - 后台服务（请勿关闭）" cmd /c "python app.py"

REM 等待服务启动
echo [2/3] 等待服务启动...
timeout /t 4 /nobreak >nul

echo [3/3] 打开应用界面...
echo.

REM 打开浏览器
start "" http://localhost:5000

echo.
echo ============================================
echo   系统已启动！
echo ============================================
echo.
echo 后台服务已在后台运行
echo 请勿关闭名为"公众号写稿系统 - 后台服务"的窗口
echo.
echo 如需停止服务，请关闭后台服务窗口
echo.
echo ============================================
echo.
echo 按任意键关闭此窗口...
pause >nul

:end
