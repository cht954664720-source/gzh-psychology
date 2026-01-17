# CC + Gemini 3 Pro 工作流指南

## 架构说明

```
┌─────────────────┐
│  Claude Code    │
│   (智谱主控)     │  ← 负责文件操作、流程控制、调度
└────────┬────────┘
         │ 调用工具
         ↓
┌─────────────────┐
│  Gemini 3 Pro   │  ← 负责深度思考、复杂推理
│    (超级专家)    │
└─────────────────┘
```

## 核心理念

- **智谱 GLM（大脑）**：处理日常任务、文件操作、简单逻辑
- **Gemini 3 Pro（专家）**：只在遇到难题时被调用，深度思考、复杂推理

## 配置步骤

### 1. 设置环境变量

在 `.env` 文件中添加：

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

或者在 CC 中直接运行：

```bash
export GEMINI_API_KEY="your_api_key"
```

### 2. 测试 Gemini 工具

在 CC 终端中运行：

```bash
python gemini_tool.py "测试一下"
```

如果能正常回复，说明配置成功！

## CC 使用场景

### 场景 1：日常问答（智谱自己处理）

```bash
# CC 会直接回答，不调用 Gemini
"帮我把这个文件重命名为 test.txt"
```

### 场景 2：深度思考（调用 Gemini）

```bash
# CC 会调用 Gemini 3 Pro 进行深度分析
"请使用 Gemini 工具深度分析一下：DeepSeek 对 AI 行业的影响"
```

在 CC 中的具体指令：

```
请运行 gemini_tool.py --deep-think "DeepSeek 对 AI 行业的深远影响，包括技术路线、商业模式、竞争格局的变化"
```

### 场景 3：完整公众号文章生成（全流程）

```bash
# CC 调用 Gemini 完成整个流程
"请运行 gemini_tool.py --article --domain '情感,心理,人际关系'"
```

### 场景 4：AI 率检测和优化

```bash
# 1. 先写一篇文章
"请帮我写一篇关于 AI 时代的文章，保存为 article.md"

# 2. 检测 AI 率
"请运行 gemini_tool.py --evaluate article.md"

# 3. 如果 AI 率高，进行优化
"请运行 gemini_tool.py --humanize article.md，保存为 article_v2.md"
```

## 实用 Prompt 模板

### 模板 1：爆款选题研究

```
请调用 Gemini 工具进行深度思考：

"在情感、心理、人际关系领域，研究一个最有可能成为 10 万+ 的公众号选题。

要求：
1. 具有时效性（2026年1月）
2. 能引发共鸣
3. 有争议或讨论点
4. 给出标题和 200 字大纲"
```

### 模板 2：文章 + 优化循环

```
请帮我完成以下任务：

1. 运行 gemini_tool.py --article --domain "情感,心理"，这会生成一篇文章并保存
2. 查看生成的 AI 评分
3. 如果评分 > 30%，请继续使用 gemini_tool.py --humanize 优化，直到 AI 率 < 30%
4. 将最终满意的文章上传到公众号草稿箱（使用 wechat_uploader.py）
```

### 模板 3：复杂问题分析

```
我有一个复杂问题需要深度分析：

"{你的问题}"

请：
1. 先自己思考一下，给出初步分析
2. 然后调用 gemini_tool.py --deep-think 让 Gemini 3 Pro 进行深度推理
3. 综合你们的答案，给我一个完整的报告
```

## 完整自动化示例

创建一个 `auto_article.sh` 脚本：

```bash
#!/bin/bash

# 自动化公众号文章生成和发布

echo "开始自动化流程..."

# 步骤 1：使用 Gemini 3 Pro 生成文章
echo "[1/3] 正在生成文章..."
python gemini_tool.py --article --domain "情感,心理"

# 步骤 2：获取最新生成的文件名
LATEST_FILE=$(ls -t gemini_article_*.md | head -1)
echo "生成文件：$LATEST_FILE"

# 步骤 3：上传到微信公众号（需要配置 wechat_uploader.py）
echo "[2/3] 上传到草稿箱..."
python main.py --upload

echo "[3/3] 完成！"
```

在 CC 中一键运行：

```
请运行 bash auto_article.sh
```

## 常用命令速查

| 命令 | 说明 |
|------|------|
| `python gemini_tool.py "问题"` | 普通问答 |
| `python gemini_tool.py --deep-think "任务"` | 深度思考 |
| `python gemini_tool.py --article --domain "领域"` | 生成完整文章 |
| `python gemini_tool.py --evaluate "文本"` | 评估 AI 率 |
| `python gemini_tool.py --humanize "文本"` | 人工化重写 |
| `python gemini_tool.py --article --domain "情感" --model gemini-3.0-pro` | 指定模型 |

## 高级技巧

### 技巧 1：让 CC 自动判断何时调用 Gemini

告诉 CC：

```
你是一个智能助手。当遇到以下情况时，请自动调用 Gemini 3 Pro：
- 需要深度推理或复杂分析
- 处理长文档（>5000字）
- 需要多模态理解（图片、视频）
- 要求最高的输出质量

其他简单任务，你自己处理即可。
```

### 技巧 2：对比智谱和 Gemini 的答案

```
"这个问题分别请智谱和 Gemini 回答，然后对比差异：
{问题}

请：
1. 先自己（智谱）回答
2. 再调用 Gemini 工具
3. 最后对比两者的优劣"
```

### 技巧 3：创建快捷别名

在 CC 的 `claude.md` 文件中添加：

```markdown
# 快捷命令

- gx: 运行 gemini_tool.py
- gx-deep: 运行 gemini_tool.py --deep-think
- gx-art: 运行 gemini_tool.py --article
```

然后可以直接说：

```
请 gx-deep "分析一下这个"
```

## 故障排除

### 问题 1：提示 "未找到 GEMINI_API_KEY"

**解决**：
```bash
# 方式 1：设置环境变量
export GEMINI_API_KEY="your_key"

# 方式 2：在运行时指定
python gemini_tool.py --api-key "your_key" "问题"
```

### 问题 2：Gemini 3 Pro 不可用

**解决**：尝试其他模型
```bash
python gemini_tool.py --model gemini-1.5-pro-latest "问题"
```

### 问题 3：API 调用失败

**可能原因**：
- API Key 无效
- 网络问题（需要科学上网）
- 配额用完

**解决**：检查 API Key 和网络连接

## 总结

**黄金法则**：
- 日常琐事 → 智谱处理
- 深度难题 → 调用 Gemini 3 Pro
- 成本优先 → 多用智谱（便宜）
- 质量优先 → 多用 Gemini（强大）

祝你使用愉快！
