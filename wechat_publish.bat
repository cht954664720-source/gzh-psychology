@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo 微信公众号文章发布工具
echo ============================================
echo.
set "ARTICLE_FILE=%1"
set "THEME=%2"

if "%ARTICLE_FILE%"=="" (
    echo 用法: wechat_publish.bat "文章路径" [主题]
    echo.
    echo 示例:
    echo   wechat_publish.bat "article_zhipu_20260115_022747.md"
    echo   wechat_publish.bat "article_zhipu_20260115_022747.md" grace
    echo.
    pause
    exit /b 1
)

if not exist "%ARTICLE_FILE%" (
    echo 错误: 找不到文章文件 "%ARTICLE_FILE%"
    pause
    exit /b 1
)

echo 正在发布文章: %ARTICLE_FILE%
echo 主题: %THEME%
echo.
echo 即将打开浏览器...
echo.

npx -y bun baoyu-skills\skills\post-to-wechat\scripts\wechat-article.ts --markdown "%ARTICLE_FILE%" --theme %THEME%

echo.
echo ============================================
echo 发布完成！
echo ============================================
pause
