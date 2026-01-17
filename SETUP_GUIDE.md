# 快速配置指南

## 第一步：获取 Gemini API Key

1. 访问：https://aistudio.google.com/apikey
2. 登录你的 Google 账号
3. 点击 "Create API key"
4. 复制生成的 Key（以 `AIza` 开头）

## 第二步：创建 .env 文件

在项目目录创建 `.env` 文件，内容如下：

```env
GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

把上面复制的 Key 粘贴进去，替换 `x` 部分。

## 第三步：测试

在终端运行：

```bash
python gemini_tool.py "测试"
```

如果看到回复，说明配置成功！

## 常见问题

### Q: 提示 "未安装 google-generativeai"
**A:** 运行 `pip install google-generativeai`

### Q: 提示 "API Key 无效"
**A:** 检查 Key 是否正确复制，不要有多余空格

### Q: 网络错误
**A:** Gemini API 需要科学上网

## 在 CC 中使用

配置好后，在 CC 中就可以这样用：

```
请运行：python gemini_tool.py "你的问题"
```
