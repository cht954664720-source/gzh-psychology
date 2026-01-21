@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

title Auto Article Generator

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    cls
    echo ============================================
    echo Error: Python not found
    echo ============================================
    echo.
    echo Please install Python 3.8 or higher
    echo.
    echo Download: https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Starting System...
echo ============================================
echo.

REM Check if service is already running (port 5000 LISTENING)
netstat -ano | findstr ":5000.*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Service is already running
    echo.
    echo Opening browser...
    echo.
    start "" http://localhost:5000
    goto :end
)

echo [1/3] Starting Flask service...
echo.

REM Start service in background (no window)
start "" /B pythonw app.py >nul 2>&1

REM Wait for service to be ready
echo [2/3] Waiting for service...
set WAIT_COUNT=0
:WAIT_LOOP
timeout /t 2 /nobreak >nul
set /a WAIT_COUNT+=2
netstat -ano | findstr ":5000.*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo Service is ready!
    goto :OPEN_BROWSER
)
if %WAIT_COUNT% lss 15 (
    echo Waiting... (%WAIT_COUNT%s)
    goto :WAIT_LOOP
) else (
    echo WARNING: Service startup timeout, trying anyway
)

:OPEN_BROWSER
echo [3/3] Opening browser...
echo.

echo Opening browser...
start "" "http://localhost:5000" 2>nul

echo.
echo ============================================
echo   System Started!
echo ============================================
echo.
echo Backend service is running in background (no window)
echo.
echo To stop the service, close this window and run: taskkill /f /im pythonw.exe
echo.
echo ============================================
echo.
echo Press any key to close this window...
pause >nul

:end
