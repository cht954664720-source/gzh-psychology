@echo off
chcp 65001 >nul 2>&1

echo ============================================
echo   Stopping Flask Service...
echo ============================================
echo.

taskkill /f /im pythonw.exe >nul 2>&1

if %errorlevel% equ 0 (
    echo Service stopped successfully.
) else (
    echo No running service found.
)

echo.
echo ============================================
pause
