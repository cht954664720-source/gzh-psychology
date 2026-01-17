# 自动化公众号写稿系统

这是一个基于 Gemini AI 和微信公众号 API 的自动化文章生成系统，能够自动选题、写作、检测 AI 率并优化，最终发布到公众号草稿箱。

## 功能特点

- **智能选题**：利用 Gemini 2.0 Flash Thinking 模型进行深度思考，挖掘爆款选题
- **自动写作**：使用 Gemini 1.5 Pro 生成高质量文章
- **AI 率检测**：自动评估文章的 AI 浓度（0-100%）
- **智能优化**：自动进行"人话化"重写，最多迭代 5 次，直到 AI 率降到 30% 以下
- **自动发布**：一键上传到微信公众号草稿箱
- **本地保存**：自动保存 Markdown 和 JSON 格式的文章

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：

```env
# Gemini API Key（必填）
GEMINI_API_KEY=your_gemini_api_key_here

# 微信公众号配置（可选，不上传草稿可不填）
WECHAT_APP_ID=your_wechat_app_id_here
WECHAT_APP_SECRET=your_wechat_app_secret_here
```

#### 获取 Gemini API Key

1. 访问 [Google AI Studio](https://aistudio.google.com/apikey)
2. 登录你的 Google 账号
3. 点击 "Create API key"
4. 复制生成的 API Key

#### 获取微信公众号 AppID 和 AppSecret

1. 登录 [微信公众平台](https://mp.weixin.qq.com)
2. 进入「开发」->「基本配置」
3. 查看并复制 AppID 和 AppSecret

**注意**：个人订阅号的 API 权限受限，建议使用「公众平台测试号」来测试完整功能。

### 3. 运行系统

#### 仅生成文章（不上传）

```bash
python main.py
```

#### 生成并自动上传到草稿箱

```bash
python main.py --upload
# 或
python main.py -u
```

### 4. 查看结果

程序运行后会生成以下文件：

- `article_YYYYMMDD_HHMMSS.md` - Markdown 格式的文章
- `article_YYYYMMDD_HHMMSS_data.json` - 详细的生成数据（包括优化历史）

## 工作流程

```
1. 选题研究
   ↓
2. 撰写初稿 (2000字)
   ↓
3. 优化循环 (最多5次)
   ├─ 检测 AI 率
   ├─ 是否 < 30%？
   │    ├─ 是 → 完成
   │    └─ 否 → 继续
   ├─ 人话化重写
   └─ 返回检测
   ↓
4. 保存到本地
   ↓
5. 上传到草稿箱 (可选)
```

## 配置说明

### Gemini 模型选择

在 `gemini_worker.py` 中可以配置使用的模型：

- **thinking_model**: 深度思考模型（默认：`gemini-2.0-flash-thinking-exp`）
  - 用于选题和复杂分析
  - 推理能力强，速度较快

- **pro_model**: 专业模型（默认：`gemini-1.5-pro`）
  - 用于写作和优化
  - 文本生成质量高

### 微信公众号配置

#### 1. 配置服务器 IP 白名单

为了安全起见，微信公众号要求配置服务器 IP 白名单：

1. 登录微信公众平台
2. 进入「开发」->「基本配置」
3. 找到「IP 白名单」
4. 添加你的服务器 IP（如果是本地测试，需要查看你的公网 IP）

#### 2. 配置默认封面图

在 `wechat_uploader.py` 中修改：

```python
default_media_id = "YOUR_DEFAULT_THUMB_MEDIA_ID"
```

获取 media_id 的方式：

1. 登录微信公众平台
2. 进入「素材管理」
3. 上传一张图片
4. 在素材库中找到该图片，复制其 media_id

## 高级用法

### 测试单个组件

#### 测试 Gemini 工作流

编辑 `gemini_worker.py`，在文件末尾填入 API Key：

```python
API_KEY = "your_actual_api_key"
```

然后运行：

```bash
python gemini_worker.py
```

#### 测试微信上传

编辑 `wechat_uploader.py`，在文件末尾填入配置：

```python
APP_ID = "your_actual_app_id"
APP_SECRET = "your_actual_app_secret"
```

然后运行：

```bash
python wechat_uploader.py
```

### 自定义参数

在 `main.py` 的 `AutoArticleSystem` 类中可以修改默认参数：

```python
self.max_iterations = 5  # 最大优化次数
self.target_ai_score = 30  # 目标AI评分
self.article_length = 2000  # 文章字数
self.domain = "情感,心理,人际关系"  # 内容领域
```

## 常见问题

### 1. Gemini API 调用失败

**错误**：`API key not valid`

**解决**：检查 API Key 是否正确，确保复制时没有多余的空格

### 2. 微信上传失败

**错误**：`errcode: 40164, errmsg: invalid ip`

**解决**：在公众号后台配置 IP 白名单

### 3. AI 评分始终降不下来

**原因**：某些题材本身就容易产生 AI 痕迹

**解决**：
- 增加最大迭代次数（`max_iterations`）
- 调整内容领域（`domain`）
- 手动编辑最后生成的文章

### 4. 文章生成速度慢

**原因**：Gemini API 响应时间受网络影响

**解决**：
- 使用代理加速
- 减少文章字数
- 使用更快的模型（如 `gemini-2.0-flash`）

## 项目结构

```
gzh情感心理/
├── main.py                 # 主程序
├── gemini_worker.py        # Gemini 工作流（选题、写作、检测、优化）
├── wechat_uploader.py      # 微信公众号上传
├── requirements.txt        # 依赖列表
├── .env.example            # 环境变量示例
├── .env                    # 环境变量（需自己创建）
├── README.md               # 使用说明
└── 思路产生.txt             # 原始思路记录
```

## 注意事项

1. **API 费用**：Gemini API 有免费额度，但超出后会产生费用，请注意使用量
2. **内容审核**：自动生成的内容需要人工审核后再发布
3. **版权问题**：AI 生成内容的版权归属尚有争议，请谨慎使用
4. **账号安全**：不要将 `.env` 文件上传到公开仓库

## 未来优化方向

- [ ] 支持多平台发布（知乎、简书等）
- [ ] 增加 AI 检测器的真实 API 集成（如 GPTZero）
- [ ] 支持批量生成文章
- [ ] 增加定时任务功能
- [ ] 支持图片自动生成
- [ ] 增加更多内容风格模板

## 技术栈

- **AI 模型**：Google Gemini 2.0 Flash Thinking & 1.5 Pro
- **微信 SDK**：WeChatPy
- **语言**：Python 3.11+
- **配置管理**：python-dotenv

## 许可证

本项目仅供学习和研究使用，请勿用于非法用途。

## 联系方式

如有问题或建议，欢迎提出 Issue。

---

**祝你使用愉快！**
