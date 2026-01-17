"""
Gemini 工作流脚本
功能：选题、写作、AI 检测、降重优化
"""

import google.generativeai as genai
from typing import Dict, Tuple
import os


class GeminiAgent:
    """Gemini AI 代理，用于处理公众号文章的选题、写作和优化"""

    def __init__(self, api_key: str, thinking_model: str = "gemini-2.0-flash-thinking-exp", pro_model: str = "gemini-1.5-pro"):
        """
        初始化 Gemini 代理

        Args:
            api_key: Google API Key
            thinking_model: 深度思考模型（用于选题和复杂分析）
            pro_model: Pro 模型（用于写作和优化）
        """
        genai.configure(api_key=api_key)

        # 配置深度思考模型（用于选题）
        self.thinking_model = thinking_model
        self.thinking_genai = genai.GenerativeModel(thinking_model)

        # 配置 Pro 模型（用于写作和优化）
        self.pro_model = pro_model
        self.pro_genai = genai.GenerativeModel(pro_model)

        print(f"[Gemini] 初始化完成 - Thinking: {thinking_model}, Pro: {pro_model}")

    def research_topic(self, domain: str = "科技,AI,互联网") -> Dict[str, str]:
        """
        利用深度思考模型研究爆款选题

        Args:
            domain: 内容领域，多个领域用逗号分隔

        Returns:
            包含 title 和 outline 的字典
        """
        print(f"[Gemini] 正在深度思考爆款选题...")
        print(f"[Gemini] 目标领域: {domain}")

        prompt = f"""你是一个顶尖的公众号运营专家，专门研究{domain}领域的爆款内容。

请深度分析当前（2026年1月）这些领域最有可能产生10万+阅读的选题。

要求：
1. 选题要具有时效性和争议性
2. 能引发读者强烈共鸣和转发欲望
3. 标题要吸睛但不标题党
4. 内容要有深度和独特观点

请给出：
- 一个最推荐的标题（不超过30字）
- 简要的内容大纲（200字左右）

直接输出，格式如下：
标题：《XXX》
大纲：XXX"""

        try:
            response = self.thinking_genai.generate_content(prompt)
            result = response.text

            # 解析结果
            lines = result.strip().split('\n')
            title = ""
            outline = ""

            for line in lines:
                if line.startswith("标题：") or line.startswith("标题:"):
                    title = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                elif line.startswith("大纲：") or line.startswith("大纲:"):
                    outline = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                elif line and not title and "《" in line and "》" in line:
                    # 提取标题
                    start = line.find("《") + 1
                    end = line.find("》")
                    if start > 0 and end > start:
                        title = line[start:end]

            if not title:
                title = "AI时代的思考：未来已来，你准备好了吗？"
            if not outline:
                outline = "探讨AI技术发展对人类社会的影响和启示"

            print(f"[Gemini] ✓ 选定题目：{title}")
            return {"title": title, "outline": outline}

        except Exception as e:
            print(f"[Gemini] ✗ 选题失败: {e}")
            # 返回默认选题
            return {
                "title": "AI时代的思考：技术革新与人文关怀",
                "outline": "探讨AI技术发展对人类社会的深远影响"
            }

    def write_article(self, topic: str, outline: str = "", length: int = 2000) -> str:
        """
        根据选题撰写文章

        Args:
            topic: 文章标题
            outline: 文章大纲
            length: 文章字数

        Returns:
            文章内容
        """
        print(f"[Gemini] 正在撰写文章...")
        print(f"[Gemini] 目标字数: {length}字")

        prompt = f"""你是一位资深的公众号专栏作家，擅长写情感、心理类的深度文章。

请根据以下信息写一篇文章：

标题：《{topic}》

大纲：{outline if outline else '请自拟大纲'}

要求：
1. 文章字数约{length}字
2. 风格要犀利、幽默、像人类写的
3. 多用短句，避免过于工整的排比
4. 加入一些个人观点和情感表达
5. 避免使用"综上所述"、"首先其次"等AI常用词
6. 用词要接地气，有生活气息
7. 可以适当使用反问、感叹等语气
8. 段落不要太长，3-5句话换段

请直接输出文章内容，不要任何开场白。"""

        try:
            response = self.pro_genai.generate_content(prompt)
            article = response.text.strip()

            print(f"[Gemini] ✓ 文章撰写完成 ({len(article)}字)")
            return article

        except Exception as e:
            print(f"[Gemini] ✗ 写作失败: {e}")
            return f"抱歉，文章生成出现问题。标题：{topic}"

    def evaluate_ai_score(self, text: str) -> int:
        """
        评估文章的 AI 浓度评分

        Args:
            text: 待检测的文本

        Returns:
            AI 浓度评分 (0-100)，100代表完全像AI，0代表完全像人
        """
        print(f"[Gemini] 正在评估AI浓度...")

        # 截取前2000字进行分析（避免超出限制）
        sample_text = text[:2000] if len(text) > 2000 else text

        prompt = f"""你是一个专业的AI内容检测专家。请分析以下文本的"AI浓度"。

分析标准：
1. 困惑度(Perplexity): 词汇使用是否丰富多样
2. 突发性(Burstiness): 句式长短是否多变
3. 情感表达: 是否有真实的人类情感
4. 用词习惯: 是否使用AI常见的连接词和句式

文本内容：
"""
{sample_text}

请给出一个0-100的评分：
- 0-30分：很自然，像人写的
- 30-60分：有些AI痕迹
- 60-100分：明显是AI写的

只需要输出一个数字（0-100之间的整数），不要任何解释。"""

        try:
            response = self.pro_genai.generate_content(prompt)
            result = response.text.strip()

            # 提取数字
            import re
            match = re.search(r'\d+', result)
            if match:
                score = int(match.group())
                # 确保在0-100范围内
                score = max(0, min(100, score))
            else:
                # 如果无法提取，使用默认值
                score = 70

            print(f"[Gemini] ✓ AI浓度评分：{score}%")
            return score

        except Exception as e:
            print(f"[Gemini] ✗ 评分失败: {e}")
            return 70  # 默认值

    def humanize_rewrite(self, text: str, current_score: int) -> str:
        """
        对文章进行"人话化"重写，降低AI检测率

        Args:
            text: 原文
            current_score: 当前AI评分

        Returns:
            重写后的文章
        """
        print(f"[Gemini] 正在进行人话化重写...")
        print(f"[Gemini] 当前AI率: {current_score}% -> 目标: <30%")

        prompt = f"""你是一位文字编辑，擅长将AI写的文章改写得像真人写的。

当前AI评分：{current_score}%
目标AI评分：<30%

请重写以下文章，要求：
1. 大幅增加口语化表达
2. 打乱句式结构，长短句交替
3. 加入更多个人观点、吐槽、感慨
4. 使用更多地道的中文表达
5. 可以适当使用一些网络流行语（但不要太多）
6. 打破段落规律，该短就短，该长就长
7. 加入一些反问、感叹、省略号等
8. 删除所有"综上所述"、"总而言之"、"首先其次"等AI痕迹明显的词
9. 可以加入一些"我觉得"、"说实话"等主观表达
10. 偶尔出现一些小瑕疵（如不完整的句子）会更像人

原文：
"""
{text}

请直接输出重写后的文章，不要任何开场白。"""

        try:
            response = self.pro_genai.generate_content(prompt)
            rewritten = response.text.strip()

            print(f"[Gemini] ✓ 重写完成 ({len(rewritten)}字)")
            return rewritten

        except Exception as e:
            print(f"[Gemini] ✗ 重写失败: {e}")
            return text  # 失败则返回原文


# 测试代码
if __name__ == "__main__":
    # 这里需要填入你的 API Key
    API_KEY = "YOUR_GEMINI_API_KEY_HERE"

    if API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        print("请先在代码中填入你的 Gemini API Key")
    else:
        agent = GeminiAgent(api_key=API_KEY)

        # 测试选题
        topic_result = agent.research_topic()
        print(f"\n选题结果：{topic_result}\n")

        # 测试写作
        article = agent.write_article(topic_result['title'], topic_result['outline'])
        print(f"\n文章预览（前500字）：\n{article[:500]}...\n")

        # 测试评分
        score = agent.evaluate_ai_score(article)
        print(f"\nAI评分：{score}\n")
