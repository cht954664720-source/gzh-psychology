@echo off
REM Gemini Tool Quick Test
chcp 65001 >nul 2>&1

echo ============================================
echo Gemini 3 Pro Tool - Quick Test
echo ============================================
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env file...
    echo GEMINI_API_KEY=your_api_key_here > .env
    echo.
    echo [!] .env file created
    echo [!] Please edit .env and add your Gemini API Key
    echo.
    notepad .env
    echo.
    echo After saving the file, press any key to continue...
    pause >nul
) else (
    echo [OK] .env file exists
)

echo.
echo [Test] Running Gemini tool...
echo.

python gemini_tool.py "Say Hello"

echo.
echo ============================================
echo If you see the result above, it works!
echo ============================================
echo.
pause
