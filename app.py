"""
自动化公众号写稿系统 - Web 界面
支持选择 Gemini 或智谱，实时追踪进度
"""

from flask import Flask, render_template, jsonify, request, make_response, send_from_directory
from flask_cors import CORS
import threading
import queue
import time
import os
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# 全局任务队列和状态
task_queue = queue.Queue()
current_status = {
    "running": False,
    "progress": 0,
    "current_step": "",
    "logs": [],
    "result": None,
    "provider": "gemini",  # gemini 或 zhipu
    "error": None
}


class TaskGenerator:
    """任务生成器，支持 Gemini 和智谱"""

    def __init__(self, provider="gemini", domain="情感,心理"):
        self.provider = provider
        self.domain = domain

    def add_log(self, message, level="info"):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        current_status["logs"].append({
            "time": timestamp,
            "level": level,
            "message": message
        })
        # 只保留最近 50 条日志
        if len(current_status["logs"]) > 50:
            current_status["logs"] = current_status["logs"][-50:]

    def update_progress(self, progress, step):
        """更新进度"""
        current_status["progress"] = progress
        current_status["current_step"] = step

    def run_with_gemini(self):
        """使用 Gemini 生成文章"""
        try:
            self.add_log("Starting Gemini 3 Pro...", "info")

            from dotenv import load_dotenv
            load_dotenv()
            import google.generativeai as genai

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise Exception("GEMINI_API_KEY not found")

            genai.configure(api_key=api_key)

            # 步骤 1: 选题
            self.update_progress(10, "Researching topic...")
            self.add_log("Step 1/4: Deep thinking for viral topic", "info")

            model = genai.GenerativeModel('models/gemini-3-pro-preview')
            topic_prompt = f"""作为公众号运营专家，请在 {self.domain} 领域构思一个爆款选题。

要求：
1. 标题吸睛（不超过 30 字）
2. 有争议性或共鸣点
3. 给出简要大纲

格式：
标题：《XXX》
大纲：XXX"""

            response = model.generate_content(topic_prompt)
            topic_result = response.text
            self.add_log(f"Topic selected: {topic_result[:100]}...", "success")

            # 解析标题
            title = "AI时代的思考"
            if "《" in topic_result and "》" in topic_result:
                start = topic_result.find("《") + 1
                end = topic_result.find("》")
                title = topic_result[start:end]

            # 步骤 2: 写作
            self.update_progress(30, "Writing article...")
            self.add_log(f"Step 2/4: Writing article (2000 words)", "info")

            article_prompt = f"""请写一篇公众号文章：

标题：《{title}》

要求：
1. 约 2000 字
2. 风格犀利、幽默、像人类
3. 多用短句
4. 加入个人观点
5. 避免AI常用词
6. 段落3-5句话换段

请直接输出文章："""

            response = model.generate_content(article_prompt)
            article = response.text
            self.add_log(f"Article written: {len(article)} characters", "success")

            # 步骤 3: 优化循环
            self.update_progress(50, "Optimizing (reducing AI score)...")
            self.add_log("Step 3/4: AI rate optimization (max 2 iterations)", "info")

            best_article = article
            best_score = 100

            for i in range(1, 3):
                self.add_log(f"Iteration {i}/2: Checking AI score...", "info")

                # 评估
                sample = article[:2000] if len(article) > 2000 else article
                eval_prompt = f"""请评估以下文本的 AI 浓度（0-100分）：

文本：
{sample}

只需输出一个数字（0-100），不要解释。"""

                response = model.generate_content(eval_prompt)
                import re
                match = re.search(r'\d+', response.text)
                score = int(match.group()) if match else 50
                score = max(0, min(100, score))

                self.add_log(f"  AI Score: {score}%", "info" if score >= 30 else "success")

                if score < best_score:
                    best_score = score
                    best_article = article

                if score < 30:
                    self.add_log(f"  Success! AI rate below 30%", "success")
                    article = best_article
                    break

                if i == 2:
                    self.add_log(f"  Max iterations reached, using best score: {best_score}%", "warning")
                    article = best_article
                    break

                self.add_log(f"  Rewriting to humanize...", "info")
                rewrite_prompt = f"""请重写以下文本，使其更像真人写的：

要求：
1. 增加口语化表达
2. 打乱句式结构
3. 加入个人观点和情感
4. 使用地道的中文
5. 避免"综上所述"、"首先其次"等 AI 用词

原文：
{article}

请直接输出重写后的内容："""

                response = model.generate_content(rewrite_prompt)
                article = response.text

                progress = 50 + (i * 10)
                self.update_progress(progress, f"Optimizing (iteration {i}/2)...")

            # 步骤 4: 保存
            self.update_progress(100, "Saving article...")
            self.add_log("Step 4/4: Saving article", "info")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"article_{timestamp}.md"

            with open(filename, 'w', encoding='utf-8') as f:
                # 元数据用HTML注释包裹
                f.write(f"<!--\n")
                f.write(f"Title: {title}\n")
                f.write(f"AI Score: {best_score}%\n")
                f.write(f"Provider: Gemini 3 Pro\n")
                f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"-->\n\n")
                # 只保存纯文章内容，不包含标题
                f.write(article)

            self.add_log(f"Article saved: {filename}", "success")

            # 构建预览内容（包含封面图）
            preview_content = article
            if cover_image_path:
                preview_content = f"![封面图]({cover_image_path})\n\n" + article

            current_status["result"] = {
                "title": title,
                "content": preview_content,
                "ai_score": best_score,
                "filename": filename,
                "provider": "Gemini 3 Pro"
            }

            self.add_log("Complete!", "success")
            current_status["running"] = False

        except Exception as e:
            self.add_log(f"Error: {str(e)}", "error")
            current_status["error"] = str(e)
            current_status["running"] = False

    def run_with_zhipu(self):
        """使用智谱生成文章"""
        try:
            self.add_log("Starting Zhipu GLM...", "info")

            from zhipuai import ZhipuAI

            api_key = os.getenv("ZHIPU_API_KEY")
            if not api_key:
                raise Exception("ZHIPU_API_KEY not found")

            client = ZhipuAI(api_key=api_key)

            # 步骤 1: 选题
            self.update_progress(10, "Researching topic...")
            self.add_log("Step 1/4: Analyzing viral topic", "info")

            topic_response = client.chat.completions.create(
                model="glm-4.7",
                messages=[
                    {
                        "role": "user",
                        "content": f"""作为公众号运营专家，请在 {self.domain} 领域构思一个爆款选题。

要求：
1. 标题吸睛（不超过 30 字）
2. 有争议性或共鸣点
3. 给出简要大纲

格式：
标题：《XXX》
大纲：XXX"""
                    }
                ]
            )

            topic_result = topic_response.choices[0].message.content
            self.add_log(f"Topic selected: {topic_result[:100]}...", "success")

            # 解析标题
            title = "AI时代的思考"
            if "《" in topic_result and "》" in topic_result:
                start = topic_result.find("《") + 1
                end = topic_result.find("》")
                title = topic_result[start:end]

            # 步骤 2: 写作
            self.update_progress(30, "Writing article...")
            self.add_log(f"Step 2/4: Writing article (2000 words)", "info")

            article_response = client.chat.completions.create(
                model="glm-4.7",
                messages=[
                    {
                        "role": "user",
                        "content": f"""请写一篇公众号文章：

标题：《{title}》

要求：
1. 约 2000 字
2. 风格犀利、幽默、像人类
3. 多用短句
4. 加入个人观点
5. 避免AI常用词（如"综上所述"、"首先其次"）
6. 段落3-5句话换段
7. 有情感共鸣

请直接输出文章，不要任何开场白。"""
                    }
                ]
            )

            article = article_response.choices[0].message.content
            self.add_log(f"Article written: {len(article)} characters", "success")

            # 步骤 3: 优化循环
            self.update_progress(50, "Optimizing (reducing AI score)...")
            self.add_log("Step 3/4: AI rate optimization (max 2 iterations)", "info")

            best_article = article
            best_score = 100

            for i in range(1, 3):
                self.add_log(f"Iteration {i}/2: Checking AI score...", "info")

                # 评估 AI 率
                sample = article[:2000] if len(article) > 2000 else article
                eval_response = client.chat.completions.create(
                    model="glm-4.7",
                    messages=[
                        {
                            "role": "user",
                            "content": f"""请评估以下文本的 AI 浓度（0-100分）：

文本：
{sample}

评估标准：
- 0-30分：像人写的
- 30-60分：有些 AI 痕迹
- 60-100分：明显是 AI 写的

只需输出一个数字（0-100），不要解释。"""
                        }
                    ]
                )

                import re
                score_text = eval_response.choices[0].message.content
                match = re.search(r'\d+', score_text)
                score = int(match.group()) if match else 50
                score = max(0, min(100, score))

                self.add_log(f"  AI Score: {score}%", "info" if score >= 30 else "success")

                if score < best_score:
                    best_score = score
                    best_article = article

                if score < 30:
                    self.add_log(f"  Success! AI rate below 30%", "success")
                    article = best_article
                    break

                if i == 2:
                    self.add_log(f"  Max iterations reached, using best score: {best_score}%", "warning")
                    article = best_article
                    break

                self.add_log(f"  Rewriting to humanize...", "info")
                rewrite_response = client.chat.completions.create(
                    model="glm-4.7",
                    messages=[
                        {
                            "role": "user",
                            "content": f"""请重写以下文本，使其更像真人写的：

当前 AI 评分：{score}分
目标评分：< 30分

要求：
1. 大幅增加口语化表达
2. 打乱句式结构，长短句交替
3. 加入更多个人观点、吐槽、感慨
4. 使用更多地道的中文表达
5. 删除所有"综上所述"、"总而言之"、"首先其次"等 AI 痕迹明显的词
6. 可以加入一些"我觉得"、"说实话"等主观表达
7. 偶尔出现一些小瑕疵会更像人

原文：
{article}

请直接输出重写后的文章内容。"""
                        }
                    ]
                )

                article = rewrite_response.choices[0].message.content

                progress = 50 + (i * 10)
                self.update_progress(progress, f"Optimizing (iteration {i}/2)...")

            # 步骤 4: 保存
            self.update_progress(100, "Saving article...")
            self.add_log("Step 4/4: Saving article", "info")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"article_zhipu_{timestamp}.md"

            with open(filename, 'w', encoding='utf-8') as f:
                # 元数据用HTML注释包裹
                f.write(f"<!--\n")
                f.write(f"Title: {title}\n")
                f.write(f"AI Score: {best_score}%\n")
                f.write(f"Provider: Zhipu GLM-4.7\n")
                f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"-->\n\n")
                # 只保存纯文章内容，不包含标题
                f.write(article)

            self.add_log(f"Article saved: {filename}", "success")

            # 构建预览内容（包含封面图）
            preview_content = article
            if cover_image_path:
                preview_content = f"![封面图]({cover_image_path})\n\n" + article

            current_status["result"] = {
                "title": title,
                "content": preview_content,
                "ai_score": best_score,
                "filename": filename,
                "provider": "Zhipu GLM-4.7"
            }

            self.add_log("Complete!", "success")
            current_status["running"] = False

        except Exception as e:
            self.add_log(f"Error: {str(e)}", "error")
            current_status["error"] = str(e)
            current_status["running"] = False

    def run_with_gemini_web(self):
        """使用 Gemini Web 客户端生成文章"""
        import subprocess
        import json

        try:
            self.add_log("Starting Gemini Web Client...", "info")

            script_dir = r"P:\claude-skills\gemini-web\scripts"

            # 步骤 1: 选题
            self.update_progress(10, "Researching topic...")
            self.add_log("Step 1/4: Deep thinking for viral topic", "info")

            topic_prompt = f"""作为公众号运营专家，请在 {self.domain} 领域构思一个爆款选题。

要求：
1. 标题吸睛（不超过 30 字）
2. 有争议性或共鸣点
3. 给出简要大纲

格式：
标题：《XXX》
大纲：XXX"""

            self.add_log("Generating topic with Gemini Web...", "info")
            topic_result = self._call_gemini_web(topic_prompt)

            # 解析标题
            title = "AI时代的思考"
            if "《" in topic_result and "》" in topic_result:
                start = topic_result.find("《") + 1
                end = topic_result.find("》")
                title = topic_result[start:end]

            self.add_log(f"Topic selected: {title}", "success")

            # 步骤 2: 写作
            self.update_progress(30, "Writing article...")
            self.add_log(f"Step 2/4: Writing article (2000 words)", "info")

            article_prompt = f"""请写一篇公众号文章：

标题：《{title}》

领域：{self.domain}

要求：
1. 开头用故事或场景引入
2. 中间用小标题分段，每段有观点有案例
3. 结尾有共鸣或行动号召
4. 语言口语化，接地气
5. 避免专业术语，用生活化比喻
6. 字数2000字左右

请直接输出文章内容，不要输出标题。"""

            self.add_log("Writing article with Gemini Web...", "info")
            article = self._call_gemini_web(article_prompt)
            self.add_log(f"Article written: {len(article)} chars", "success")

            # 步骤 3: 人工化
            self.update_progress(60, "Humanizing...")
            self.add_log("Step 3/4: Removing AI traces", "info")

            best_score = 100
            best_article = article

            for i in range(2):
                self.add_log(f"Iteration {i+1}/2: Checking AI score...", "info")

                import requests
                check_response = requests.post(
                    'https://api.gptzero.me/v2/predict/text',
                    json={'document': best_article},
                    headers={'Accept': 'application/json'}
                )

                if check_response.status_code == 200:
                    import re
                    match = re.search(r'\d+', check_response.text)
                    score = int(match.group()) if match else 50
                    score = max(0, min(100, score))

                    self.add_log(f"  AI Score: {score}%", "info" if score >= 30 else "success")

                    if score < best_score:
                        best_score = score
                        best_article = article

                    if score < 30:
                        self.add_log(f"  Success! AI rate below 30%", "success")
                        article = best_article
                        break

                if i == 1:
                    self.add_log(f"  Max iterations reached, using best score: {best_score}%", "warning")
                    article = best_article
                    break

                self.add_log(f"  Rewriting to humanize...", "info")
                rewrite_prompt = f"""请重写以下文本，使其更像真人写的：

要求：
1. 大幅增加口语化表达
2. 打乱句式结构，长短句交替
3. 加入更多个人观点、吐槽、感慨
4. 使用更多地道的中文表达
5. 删除所有"综上所述"、"总而言之"、"首先其次"等 AI 痕迹明显的词
6. 可以加入一些"我觉得"、"说实话"等主观表达
7. 偶尔出现一些小瑕疵会更像人

原文：
{article}

请直接输出重写后的文章内容。"""

                article = self._call_gemini_web(rewrite_prompt)

                progress = 50 + (i * 10)
                self.update_progress(progress, f"Optimizing (iteration {i}/2)...")

            # 步骤 4: 生成封面图
            self.update_progress(90, "Generating cover image...")
            self.add_log("Step 4/5: Generating cover image", "info")

            cover_image_path = None
            try:
                # 读取封面图配置
                import json
                import os
                config_file = os.path.join(os.path.dirname(__file__), "prompts_config.json")

                cover_config = {"enabled": True, "style": "auto", "methods": ["placeholder", "zhipu", "gemini-web", "dalle"]}
                if os.path.exists(config_file):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        all_config = json.load(f)
                        provider_key = "gemini-web"
                        if provider_key in all_config and "cover" in all_config[provider_key]:
                            cover_config = all_config[provider_key]["cover"]

                # 检查是否启用封面图
                if not cover_config.get("enabled", True):
                    self.add_log("  Cover generation disabled in config", "info")
                else:
                    from cover_generator import CoverGenerator
                    cover_gen = CoverGenerator()

                    # 确定风格
                    cover_style = cover_config.get("style", "auto")
                    if cover_style == "auto":
                        # 自动选择风格
                        content_lower = article.lower()
                        if any(word in content_lower for word in ['ai', '科技', '技术', '数字', '算法']):
                            cover_style = 'tech'
                        elif any(word in content_lower for word in ['情感', '成长', '生活', '人生']):
                            cover_style = 'warm'
                        elif any(word in content_lower for word in ['自然', '环保', '健康']):
                            cover_style = 'nature'
                        else:
                            cover_style = 'elegant'

                    # 按配置的优先级尝试生成
                    methods = cover_config.get("methods", ["placeholder", "zhipu", "gemini-web", "dalle"])
                    cover_result = cover_gen.generate_cover(title, article, style=cover_style, output_dir=".", methods=methods)

                    if cover_result["success"]:
                        cover_image_path = cover_result["image_path"]
                        self.add_log(f"  Cover generated: {cover_image_path} (method: {cover_result['method']})", "success")
                    else:
                        self.add_log(f"  Cover generation skipped: {cover_result.get('error', 'Unknown error')}", "warning")

            except Exception as e:
                self.add_log(f"  Cover generation error: {str(e)}", "warning")

            # 步骤 5: 保存
            self.update_progress(100, "Saving article...")
            self.add_log("Step 5/5: Saving article", "info")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"article_gemini_web_{timestamp}.md"

            with open(filename, 'w', encoding='utf-8') as f:
                # 元数据用HTML注释包裹
                f.write(f"<!--\n")
                f.write(f"Title: {title}\n")
                f.write(f"AI Score: {best_score}%\n")
                f.write(f"Provider: Gemini Web (Client)\n")
                f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                if cover_image_path:
                    f.write(f"Cover: {cover_image_path}\n")
                f.write(f"-->\n\n")

                # 如果有封面图，在文章开头插入
                if cover_image_path:
                    f.write(f"![封面图]({cover_image_path})\n\n")

                # 写入文章内容
                f.write(article)

            self.add_log(f"Article saved: {filename}", "success")

            # 构建预览内容（包含封面图）
            preview_content = article
            if cover_image_path:
                preview_content = f"![封面图]({cover_image_path})\n\n" + article

            current_status["result"] = {
                "title": title,
                "content": preview_content,
                "ai_score": best_score,
                "filename": filename,
                "provider": "Gemini Web (Client)"
            }

            self.add_log("Complete!", "success")
            current_status["running"] = False

        except Exception as e:
            self.add_log(f"Error: {str(e)}", "error")
            current_status["error"] = str(e)
            current_status["running"] = False

    def _call_gemini_web(self, prompt):
        """调用 Gemini Web Skill"""
        import subprocess
        import json
        import sys
        import os

        script_path = r"P:\claude-skills\gemini-web\scripts\main.ts"

        # 创建临时 prompt 文件（使用绝对路径避免 hash 负数问题）
        temp_prompt_file = os.path.abspath(f"temp_gemini_prompt_{abs(hash(prompt))}.txt")
        with open(temp_prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)

        try:
            # Windows 需要 shell=True 才能找到 npx
            use_shell = sys.platform == 'win32'

            cmd = f'npx -y bun "{script_path}" --promptfiles "{temp_prompt_file}" --json'

            self.add_log(f"Calling Gemini Web with prompt length: {len(prompt)}", "info")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                encoding='utf-8',
                shell=use_shell,
                cwd=r"P:\claude-skills\gemini-web\scripts"
            )

            # 记录命令输出用于调试
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                self.add_log(f"Gemini Web returncode: {result.returncode}", "error")
                self.add_log(f"stderr: {result.stderr[:500] if result.stderr else 'None'}", "error")
                self.add_log(f"stdout: {result.stdout[:500] if result.stdout else 'None'}", "error")
                raise Exception(f"Gemini Web failed: {error_msg}")

            output = result.stdout.strip()
            if not output:
                raise Exception("Empty response from Gemini Web")

            # 输出可能包含日志行，需要提取 JSON 部分
            # 查找第一个 '{' 开始的位置
            json_start = output.find('{')
            if json_start > 0:
                output = output[json_start:]

            data = json.loads(output)
            return data.get('text', '')
        finally:
            if os.path.exists(temp_prompt_file):
                os.remove(temp_prompt_file)

    def run_with_gemini_deepseek(self):
        """使用 Gemini Web + DeepSeek 组合生成文章

        流程：
        1. Gemini Web - 深度研究生成标题和大纲
        2. DeepSeek - 按大纲写文章
        3. Gemini Web - 分析AI率（2次迭代）
        """
        try:
            self.add_log("Starting Gemini Web + DeepSeek workflow...", "info")

            # 步骤 1: Gemini Web 深度研究生成标题和大纲
            self.update_progress(10, "Researching and outlining...")
            self.add_log("Step 1/4: Gemini Web deep research for title and outline", "info")

            topic_prompt = f"""你是一位经验丰富的公众号文章编辑。请深度研究以下领域：

领域：{self.domain}

请完成以下任务：
1. 深度分析这个领域的热点话题和用户痛点
2. 提出一个有吸引力、有争议性、能引发共鸣的文章标题
3. 设计详细的文章大纲（包含开头、3-5个主要部分、结尾）

请直接输出格式如下：
标题：《文章标题》

大纲：
一、开头
- 要点1

二、主体部分1
- 要点1
- 要点2

三、结尾
- 要点"""

            outline_text = self._call_gemini_web(topic_prompt)
            self.add_log(f"Outline generated: {len(outline_text)} characters", "success")

            # 提取标题
            import re
            title_match = re.search(r'标题[：:]\s*《(.+?)》', outline_text)
            title = title_match.group(1) if title_match else self.domain
            self.add_log(f"Title: {title}", "info")

            # 步骤 2: DeepSeek 按大纲写文章
            self.update_progress(30, "Writing article...")
            self.add_log("Step 2/4: DeepSeek writing article based on outline", "info")

            article_prompt = f"""请根据以下大纲写一篇完整的公众号文章：

标题：《{title}》

{outline_text}

要求：
1. 约 2000 字
2. 风格犀利、幽默、像人类
3. 多用短句
4. 加入个人观点
5. 避免AI常用词
6. 段落3-5句话换段

请直接输出文章，不要输出标题："""

            import requests
            deepseek_api_key = "sk-b509aad3ce224271b0b8fb336063b4e7"
            deepseek_response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {deepseek_api_key}'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [
                        {'role': 'user', 'content': article_prompt}
                    ],
                    'temperature': 0.7
                },
                timeout=120
            )

            if deepseek_response.status_code != 200:
                raise Exception(f"DeepSeek API error: {deepseek_response.status_code}")

            article = deepseek_response.json()['choices'][0]['message']['content']
            self.add_log(f"Article written: {len(article)} characters", "success")

            # 步骤 3: Gemini Web 优化循环（2次迭代）
            self.update_progress(60, "Optimizing (reducing AI score)...")
            self.add_log("Step 3/4: AI rate optimization (max 2 iterations)", "info")

            best_article = article
            best_score = 100

            for i in range(1, 3):
                self.add_log(f"Iteration {i}/2: Checking AI score...", "info")

                # 评估
                sample = article[:2000] if len(article) > 2000 else article
                eval_prompt = f"""请评估以下文本的 AI 浓度（0-100分）：

文本：
{sample}

只需输出一个数字（0-100），不要解释。"""

                eval_result = self._call_gemini_web(eval_prompt)
                match = re.search(r'\d+', eval_result)
                score = int(match.group()) if match else 50
                score = max(0, min(100, score))

                self.add_log(f"  AI Score: {score}%", "info" if score >= 30 else "success")

                if score < best_score:
                    best_score = score
                    best_article = article

                if score < 30:
                    self.add_log(f"  Success! AI rate below 30%", "success")
                    article = best_article
                    break

                if i == 2:
                    self.add_log(f"  Max iterations reached, using best score: {best_score}%", "warning")
                    article = best_article
                    break

                self.add_log(f"  Rewriting to humanize...", "info")
                rewrite_prompt = f"""请重写以下文本，使其更像真人写的：

要求：
1. 增加口语化表达
2. 打乱句式结构
3. 加入个人观点和情感
4. 使用地道的中文
5. 避免"综上所述"、"首先其次"等 AI 用词

原文：
{article}

请直接输出重写后的内容："""

                article = self._call_gemini_web(rewrite_prompt)

                progress = 50 + (i * 10)
                self.update_progress(progress, f"Optimizing (iteration {i}/2)...")

            # 步骤 4: 生成封面图
            self.update_progress(90, "Generating cover image...")
            self.add_log("Step 4/5: Generating cover image", "info")

            cover_image_path = None
            try:
                # 读取封面图配置
                import json
                import os
                config_file = os.path.join(os.path.dirname(__file__), "prompts_config.json")

                cover_config = {"enabled": True, "style": "auto", "methods": ["placeholder", "zhipu", "gemini-web", "dalle"]}
                if os.path.exists(config_file):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        all_config = json.load(f)
                        provider_key = "gemini-deepseek"
                        if provider_key in all_config and "cover" in all_config[provider_key]:
                            cover_config = all_config[provider_key]["cover"]

                # 检查是否启用封面图
                if not cover_config.get("enabled", True):
                    self.add_log("  Cover generation disabled in config", "info")
                else:
                    from cover_generator import CoverGenerator
                    cover_gen = CoverGenerator()

                    # 确定风格
                    cover_style = cover_config.get("style", "auto")
                    if cover_style == "auto":
                        # 自动选择风格
                        content_lower = article.lower()
                        if any(word in content_lower for word in ['ai', '科技', '技术', '数字', '算法']):
                            cover_style = 'tech'
                        elif any(word in content_lower for word in ['情感', '成长', '生活', '人生']):
                            cover_style = 'warm'
                        elif any(word in content_lower for word in ['自然', '环保', '健康']):
                            cover_style = 'nature'
                        else:
                            cover_style = 'elegant'

                    # 按配置的优先级尝试生成
                    methods = cover_config.get("methods", ["placeholder", "zhipu", "gemini-web", "dalle"])
                    cover_result = cover_gen.generate_cover(title, article, style=cover_style, output_dir=".", methods=methods)

                    if cover_result["success"]:
                        cover_image_path = cover_result["image_path"]
                        self.add_log(f"  Cover generated: {cover_image_path} (method: {cover_result['method']})", "success")
                    else:
                        self.add_log(f"  Cover generation skipped: {cover_result.get('error', 'Unknown error')}", "warning")

            except Exception as e:
                self.add_log(f"  Cover generation error: {str(e)}", "warning")

            # 步骤 5: 保存
            self.update_progress(100, "Saving article...")
            self.add_log("Step 5/5: Saving article", "info")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"article_gemini_deepseek_{timestamp}.md"

            with open(filename, 'w', encoding='utf-8') as f:
                # 元数据用HTML注释包裹
                f.write(f"<!--\n")
                f.write(f"Title: {title}\n")
                f.write(f"AI Score: {best_score}%\n")
                f.write(f"Provider: Gemini Web + DeepSeek\n")
                f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                if cover_image_path:
                    f.write(f"Cover: {cover_image_path}\n")
                f.write(f"-->\n\n")

                # 如果有封面图，在文章开头插入
                if cover_image_path:
                    f.write(f"![封面图]({cover_image_path})\n\n")

                # 写入文章内容
                f.write(article)

            self.add_log(f"Article saved: {filename}", "success")

            # 构建预览内容（包含封面图）
            preview_content = article
            if cover_image_path:
                preview_content = f"![封面图]({cover_image_path})\n\n" + article

            current_status["result"] = {
                "title": title,
                "content": preview_content,
                "ai_score": best_score,
                "filename": filename,
                "provider": "Gemini Web + DeepSeek"
            }

            self.add_log("Complete!", "success")
            current_status["running"] = False

        except Exception as e:
            self.add_log(f"Error: {str(e)}", "error")
            current_status["error"] = str(e)
            current_status["running"] = False

    def run(self):
        """运行任务"""
        try:
            if self.provider == "gemini":
                self.run_with_gemini()
            elif self.provider == "gemini-web":
                self.run_with_gemini_web()
            elif self.provider == "gemini-deepseek":
                self.run_with_gemini_deepseek()
            else:
                self.run_with_zhipu()
        except Exception as e:
            self.add_log(f"Fatal error: {str(e)}", "error")
            current_status["error"] = str(e)
            current_status["running"] = False


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/start', methods=['POST'])
def start_task():
    """启动任务"""
    if current_status["running"]:
        return jsonify({"error": "Task already running"})

    data = request.json
    provider = data.get("provider", "gemini")
    domain = data.get("domain", "情感,心理")

    # 重置状态
    current_status["running"] = True
    current_status["progress"] = 0
    current_status["current_step"] = "Initializing..."
    current_status["logs"] = []
    current_status["result"] = None
    current_status["error"] = None
    current_status["provider"] = provider

    # 启动任务线程
    def task_thread():
        generator = TaskGenerator(provider=provider, domain=domain)
        generator.run()

    thread = threading.Thread(target=task_thread)
    thread.daemon = True
    thread.start()

    return jsonify({"success": True, "message": f"Task started with {provider}"})


@app.route('/api/status')
def get_status():
    """获取当前状态"""
    return jsonify(current_status)


@app.route('/api/stop', methods=['POST'])
def stop_task():
    """停止任务"""
    current_status["running"] = False
    current_status["current_step"] = "Stopped by user"
    return jsonify({"success": True, "message": "Task stopped"})


@app.route('/api/upload-wechat', methods=['POST'])
def upload_to_wechat():
    """上传到微信公众号草稿箱"""
    try:
        data = request.json
        title = data.get("title")
        content = data.get("content")

        if not title or not content:
            return jsonify({"success": False, "error": "标题或内容不能为空"})

        # 导入微信上传模块
        from dotenv import load_dotenv
        import os
        load_dotenv()

        wechat_app_id = os.getenv("WECHAT_APP_ID")
        wechat_app_secret = os.getenv("WECHAT_APP_SECRET")

        if not wechat_app_id or not wechat_app_secret:
            return jsonify({
                "success": False,
                "error": "未配置微信公众号信息，请在 .env 文件中添加 WECHAT_APP_ID 和 WECHAT_APP_SECRET"
            })

        # 导入并使用 wechat_uploader
        import sys
        sys.path.append(os.path.dirname(__file__))
        from wechat_uploader import WeChatUploader
        from wechatpy.exceptions import WeChatClientException

        uploader = WeChatUploader(wechat_app_id, wechat_app_secret)

        # 检查客户端是否初始化成功
        if not uploader.client:
            return jsonify({
                "success": False,
                "error": "微信客户端初始化失败，请检查 AppID 和 AppSecret 是否正确"
            })

        # 转换 Markdown 为 HTML
        html_content = uploader.markdown_to_html(content)

        # 上传到草稿箱
        success = uploader.upload_draft(
            title=title,
            content=html_content,
            author="AI助手",
            digest=f"{title} - AI自动生成",
            show_cover_pic=0  # 暂时不显示封面（需要额外配置）
        )

        if success:
            return jsonify({
                "success": True,
                "message": "上传成功！请登录公众号后台查看草稿箱"
            })
        else:
            return jsonify({
                "success": False,
                "error": "上传失败，请检查后端日志获取详细错误信息"
            })

    except WeChatClientException as e:
        # 微信API错误
        error_msg = f"微信API错误 (错误码: {e.errcode}): {e.errmsg}"

        # 添加常见错误的中文提示
        if e.errcode == 40001:
            error_msg += "\n\n提示：AppID 或 AppSecret 可能不正确，请检查 .env 文件中的配置"
        elif e.errcode == 40164:
            error_msg += "\n\n提示：IP地址不在白名单中\n解决方法：\n1. 登录微信公众平台 https://mp.weixin.qq.com\n2. 进入「开发」->「基本配置」\n3. 在「IP白名单」中添加你的服务器IP地址"
        elif e.errcode == 45009:
            error_msg += "\n\n提示：接口调用超过限制，请稍后再试"
        elif e.errcode == 40006:
            error_msg += "\n\n提示：文章内容格式不正确，请检查"

        return jsonify({
            "success": False,
            "error": error_msg,
            "errcode": e.errcode,
            "errmsg": e.errmsg
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"上传失败: {str(e)}\n\n类型: {type(e).__name__}"
        })


@app.route('/api/test-wechat', methods=['GET'])
def test_wechat():
    """测试微信连接配置"""
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()

        wechat_app_id = os.getenv("WECHAT_APP_ID")
        wechat_app_secret = os.getenv("WECHAT_APP_SECRET")

        result = {
            "success": True,
            "config": {
                "app_id": wechat_app_id[:10] + "..." if wechat_app_id else None,
                "app_secret_set": bool(wechat_app_secret),
            }
        }

        if not wechat_app_id or not wechat_app_secret:
            result["success"] = False
            result["error"] = "未配置 WECHAT_APP_ID 或 WECHAT_APP_SECRET"
            return jsonify(result)

        # 尝试初始化微信客户端
        from wechat_uploader import WeChatUploader
        uploader = WeChatUploader(wechat_app_id, wechat_app_secret)

        if not uploader.client:
            result["success"] = False
            result["error"] = "微信客户端初始化失败"
            return jsonify(result)

        # 尝试获取 access_token
        try:
            token = uploader.get_access_token()
            if token:
                result["access_token"] = token[:20] + "..."
                result["message"] = "微信连接正常"
            else:
                result["success"] = False
                result["error"] = "无法获取 Access Token"
        except Exception as e:
            result["success"] = False
            result["error"] = f"获取 Access Token 失败: {str(e)}"

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route('/api/upload-wechat-browser', methods=['POST'])
def upload_to_wechat_browser():
    """使用网页版微信公众号上传（适合个人公众号）"""
    try:
        import os
        import subprocess
        import uuid
        import sys

        data = request.json
        title = data.get("title")
        content = data.get("content")
        theme = data.get("theme", "default")

        if not content:
            return jsonify({"success": False, "error": "内容不能为空"})

        # 生成临时文件（使用项目目录）
        temp_filename = f"temp_publish_{uuid.uuid4().hex[:8]}.md"
        temp_copy = os.path.abspath(temp_filename)

        # 写入临时文件
        try:
            with open(temp_copy, 'w', encoding='utf-8') as f:
                f.write(f"# {title or '未命名'}\n\n")
                f.write(content)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"写入临时文件失败: {str(e)}"
            })

        # 在 scripts 目录中运行脚本
        script_dir = r"P:\claude-skills\post-to-wechat\scripts"

        # 检查脚本目录是否存在
        if not os.path.exists(script_dir):
            return jsonify({
                "success": False,
                "error": f"脚本目录不存在: {script_dir}"
            })

        print(f"[DEBUG] temp_file: {temp_copy}", file=sys.stderr)
        print(f"[DEBUG] script_dir: {script_dir}", file=sys.stderr)

        # 使用 start 命令打开新窗口
        # 修复：路径可能包含空格，需要正确转义
        cmd = f'start "微信发布" cmd /k "cd /d \"{script_dir}\" && echo 正在运行微信发布脚本... && echo. && echo 工作目录: %CD% && echo. && npx -y bun wechat-article.ts --markdown \"{temp_copy}\" --theme {theme} && echo. && echo 发布完成！ && pause"'

        print(f"[DEBUG] Running command...", file=sys.stderr)

        try:
            result = subprocess.Popen(cmd, shell=True)
            print(f"[DEBUG] Process started with PID: {result.pid}", file=sys.stderr)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"启动进程失败: {str(e)}"
            })

        return jsonify({
            "success": True,
            "message": "已打开新窗口运行微信发布脚本",
            "tempFile": temp_filename,
            "note": "请查看新打开的命令行窗口，Chrome 浏览器应该会自动打开"
        })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] {error_details}", file=sys.stderr)
        return jsonify({
            "success": False,
            "error": f"启动失败: {str(e)}"
        })


@app.route('/api/history')
def get_history():
    """获取历史文章列表（支持分页）"""
    # 禁用缓存
    from flask import make_response
    try:
        import glob
        import os
        from datetime import datetime

        # 获取分页参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        # 获取所有文章文件
        files = glob.glob("article*.md")
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)  # 按修改时间倒序

        # 分页
        total = len(files)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        files_page = files[start_idx:end_idx]

        history = []
        for filepath in files_page:
            try:
                filename = os.path.basename(filepath)
                stat = os.stat(filepath)
                size = stat.st_size
                mtime = stat.st_mtime

                # 读取文件前几行获取标题和provider
                title = filename  # 默认使用文件名
                provider = "Unknown"
                ai_score = None

                with open(filepath, 'r', encoding='utf-8') as f:
                    in_comment = False
                    title_found = False  # 标记是否已找到标题

                    for i, line in enumerate(f):
                        # 检查HTML注释格式的元数据
                        if line.strip() == '<!--':
                            in_comment = True
                            continue
                        if line.strip() == '-->':
                            in_comment = False
                            continue
                        if in_comment:
                            if 'Title:' in line:
                                title = line.split('Title:')[1].strip()
                                title_found = True
                            elif 'Provider:' in line:
                                provider = line.split('Provider:')[1].strip()
                            elif 'AI Score:' in line:
                                score_text = line.split('AI Score:')[1].strip()
                                ai_score = score_text.replace('%', '').strip()
                            continue

                        # 旧格式兼容（如果不在注释中）
                        elif i < 15:  # 只检查前15行
                            # 尝试解析 Markdown 标题 (# 标题)
                            if not title_found and line.strip().startswith('# '):
                                title = line.strip()[2:].strip()
                                title_found = True
                            # 旧格式的 **Provider**: xxx
                            elif '**Provider**' in line or 'Provider**' in line:
                                provider = line.split('**:**')[1].strip() if '**:**' in line else line.replace('**Provider**: ', '').replace('**Provider**:', '').strip()
                            # 旧格式的 **AI Score**: xxx
                            elif '**AI Score**' in line or 'AI Score**' in line:
                                score_text = line.split('**:**')[1].strip() if '**:**' in line else line.replace('**AI Score**: ', '').replace('**AI Score**:', '').strip()
                                ai_score = score_text.replace('%', '').strip()

                # 简化provider名称（注意：更具体的判断要放在前面）
                provider_short = provider
                if 'Gemini 3 Pro' in provider:
                    provider_short = 'Gemini API'
                elif 'Gemini Web + DeepSeek' in provider:
                    provider_short = 'Gemini Web + DeepSeek'
                elif 'Gemini Web' in provider:
                    provider_short = 'Gemini Web'
                elif 'Zhipu GLM' in provider:
                    provider_short = '智谱 GLM'

                history.append({
                    "filename": filename,
                    "title": title,
                    "size": size,
                    "modified_time": mtime,
                    "provider": provider_short,
                    "ai_score": ai_score
                })
            except Exception as e:
                print(f"Error reading file {filepath}: {e}")

        response = make_response(jsonify({
            "success": True,
            "history": history,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page
            }
        }))
        # 禁用缓存
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/history/<filename>')
def get_history_file(filename):
    """读取历史文章内容"""
    try:
        import os

        # 安全检查：确保文件名不包含路径
        if '/' in filename or '\\' in filename:
            return jsonify({"success": False, "error": "Invalid filename"})

        filepath = os.path.join(os.path.dirname(__file__), filename)

        # 确保文件存在且是文章文件
        if not os.path.exists(filepath):
            return jsonify({"success": False, "error": "File not found"})

        if not filename.startswith("article"):
            return jsonify({"success": False, "error": "Invalid file"})

        # 读取文件内容
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        return jsonify({
            "success": True,
            "filename": filename,
            "content": content
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/prompts-config', methods=['GET'])
def get_prompts_config():
    """获取提示词配置"""
    try:
        import json
        config_file = os.path.join(os.path.dirname(__file__), "prompts_config.json")

        if not os.path.exists(config_file):
            # 如果配置文件不存在，返回默认配置
            return jsonify({
                "success": True,
                "config": {
                    "gemini-web": {
                        "name": "Gemini Web (Client)",
                        "steps": [
                            {
                                "name": "选题生成",
                                "prompt": "作为公众号运营专家，请在 {domain} 领域构思一个爆款选题。\\n\\n要求：\\n1. 标题吸睛（不超过 30 字）\\n2. 有争议性或共鸣点\\n3. 给出简要大纲\\n\\n格式：\\n标题：《XXX》\\n大纲：XXX"
                            }
                        ],
                        "ai_iterations": 2,
                        "target_ai_score": 30,
                        "article_length": 2000
                    }
                }
            })

        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        response = make_response(jsonify({
            "success": True,
            "config": config
        }))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/prompts-config', methods=['POST'])
def save_prompts_config():
    """保存提示词配置"""
    try:
        import json
        data = request.json
        config = data.get("config")

        if not config:
            return jsonify({"success": False, "error": "配置不能为空"})

        config_file = os.path.join(os.path.dirname(__file__), "prompts_config.json")

        # 保存配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        return jsonify({
            "success": True,
            "message": "配置已保存"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/cover/<path:filename>')
def serve_cover(filename):
    """提供封面图片访问"""
    import os
    cover_dir = os.path.dirname(__file__)
    return send_from_directory(cover_dir, filename)


if __name__ == '__main__':
    print("=" * 60)
    print("Auto Article Generator - Web Interface")
    print("=" * 60)
    print()
    print("Starting server...")
    print("Open your browser: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    app.run(debug=True, host='0.0.0.0', port=5000)
