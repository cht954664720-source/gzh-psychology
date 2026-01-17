# 自动化公众号写稿系统 - CC + Gemini 3 Pro 版

> **核心理念**：用 CC（智谱）做调度，用 Gemini 3 Pro 做专家

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 Gemini API Key

创建 `.env` 文件：

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. 测试连接

**Windows**：
```bash
setup_and_test.bat
```

**Mac/Linux**：
```bash
python gemini_tool.py "测试"
```

### 4. 在 CC 中使用

#### 示例 1：普通问答
```
请运行：python gemini_tool.py "请介绍一下量子计算"
```

#### 示例 2：深度思考（复杂推理）
```
请调用 Gemini 3 Pro 深度分析：
"DeepSeek R1 对 AI 行业的影响"
```

#### 示例 3：生成完整公众号文章
```
请运行完整流程：
python gemini_tool.py --article --domain "情感,心理,人际关系"
```

#### 示例 4：AI 率检测和优化
```
1. 先帮我写一篇文章，保存为 article.md
2. 然后检测 AI 率：python gemini_tool.py --evaluate article.md
3. 如果超过 30%，优化它：python gemini_tool.py --humanize article.md
```

## 核心文件

| 文件 | 说明 |
|------|------|
| `gemini_tool.py` | **核心工具** - 可被 CC 调用的 Gemini 3 Pro 接口 |
| `main.py` | 完整的自动化流程（生成 + 上传） |
| `CC_WORKFLOW.md` | **重要** - CC 使用场景和工作流详解 |
| `setup_and_test.bat` | 配置和测试脚本（Windows） |

## 为什么用 Gemini 3 Pro？

根据你的 Pro 账号，你应该拥有：
- **Gemini 3.0 Pro** - 最强逻辑模型（深度思考、复杂推理）
- **Gemini 2.0 Flash** - 最快速度模型（快速问答）

代码会自动尝试使用 `gemini-3.0-pro`，如果不可用会回退到 `gemini-1.5-pro-latest`。

## 实际工作流

### 场景：每日自动更文

在 CC 中一次性完成：

```
请帮我完成以下任务：

1. 使用 Gemini 3 Pro 研究一个情感心理类的爆款选题
   （运行：python gemini_tool.py --deep-think "研究情感心理领域的爆款选题"）

2. 基于选题写一篇 2000 字的文章

3. 检测 AI 率并优化，直到降到 30% 以下

4. 上传到公众号草稿箱
```

### CC 会自动：
- 调用 Gemini 3 Pro 进行深度思考
- 管理文件读写
- 追踪优化进度
- 调用微信 API 上传

## 常用命令

```bash
# 普通问答
python gemini_tool.py "你的问题"

# 深度思考（复杂推理）
python gemini_tool.py --deep-think "复杂任务"

# 生成完整文章（包含选题、写作、优化）
python gemini_tool.py --article --domain "情感,心理"

# 评估 AI 率
python gemini_tool.py --evaluate "文本或文件路径"

# 人工化重写
python gemini_tool.py --humanize "文本或文件路径"

# 指定模型
python gemini_tool.py --model gemini-3.0-pro "问题"
```

## 文件说明

```
gzh情感心理/
├── gemini_tool.py          # 核心工具 - CC 调用 Gemini 3 Pro 的接口
├── main.py                 # 完整自动化流程
├── gemini_worker.py        # Gemini 工作流（旧版，main.py 中使用）
├── wechat_uploader.py      # 微信公众号上传
├── CC_WORKFLOW.md          # CC 使用场景详解（必看！）
├── README_QUICK.md         # 本文件 - 快速开始
├── requirements.txt        # 依赖列表
├── .env.example            # 环境变量示例
├── setup_and_test.bat      # Windows 配置测试脚本
└── run.bat                 # 快速启动
```

## 架构优势

### 传统方案 vs CC + Gemini 3 Pro

| 传统方案 | CC + Gemini 3 Pro |
|---------|------------------|
| 单一模型（要么贵要么弱） | 智谱（便宜）+ Gemini 3 Pro（强大） |
| 手动切换 | CC 智能调度 |
| 无法利用本地能力 | CC 管理文件，Gemini 提供智力 |
| 成本高 | 智谱处理简单任务，节省成本 |

### 黄金法则

```
简单任务（文件操作、日常问答）→ 智谱处理（便宜、快）
复杂任务（深度推理、长文分析）→ Gemini 3 Pro（强大、专业）
```

## 下一步

1. ✅ 运行 `setup_and_test.bat` 测试连接
2. ✅ 阅读 `CC_WORKFLOW.md` 了解详细用法
3. ✅ 在 CC 中尝试第一个任务

## 获取帮助

- 详细工作流：查看 `CC_WORKFLOW.md`
- 完整文档：查看 `README.md`
- 测试连接：运行 `setup_and_test.bat`

---

**祝你使用愉快！有问题直接在 CC 中问我就行 🚀**
