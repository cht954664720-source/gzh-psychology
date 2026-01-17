@echo off
chcp 65001 >nul 2>&1
echo ============================================
echo Testing Gemini API
echo ============================================
echo.
python auto_test.py
echo.
echo ============================================
echo Press any key to close...
echo ============================================
pause >nul
