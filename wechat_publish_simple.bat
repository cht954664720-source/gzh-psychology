@echo off
cd /d %%~dp0
npx -y bun baoyu-skillsskillspost-to-wechatscriptswechat-article.ts --markdown %~1 --theme %~2
pause
