@echo off
chcp 65001 >nul 2>&1

echo ============================================
echo Auto Article Generator - Web Interface
echo ============================================
echo.

echo Starting web server...
echo.

python app.py

pause
