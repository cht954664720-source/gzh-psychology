"""
Gemini 3 Pro 工具脚本
可以被 Claude Code (CC) 直接调用的超级专家工具

使用方法（在 CC 中）：
1. 基础问答：
   python gemini_tool.py "你的问题"

2. 深度思考：
   python gemini_tool.py --deep-think "复杂任务"

3. 评估 AI 率：
   python gemini_tool.py --evaluate "你的文本"

4. 人工化重写：
   python gemini_tool.py --humanize "你的文本"

5. 公众号完整流程：
   python gemini_tool.py --article --domain "情感,心理"
"""

import sys
import os
import json
import argparse
from datetime import datetime

# 首先加载 .env 文件
try:
    from dotenv import load_dotenv
    # 加载当前目录的 .env 文件
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass

# 检查是否安装了 google-generativeai
try:
    import google.generativeai as genai
except ImportError:
    print("错误：未安装 google-generativeai 库")
    print("请运行: pip install google-generativeai")
    sys.exit(1)


class GeminiTool:
    """Gemini 3 Pro 工具类"""

    def __init__(self, api_key: str = None, model: str = "models/gemini-3-pro-preview"):
        """
        初始化 Gemini 工具

        Args:
            api_key: Gemini API Key（如果不提供，将从环境变量读取）
            model: 模型名称（默认 gemini-3.0-pro）
        """
        # 优先使用传入的 api_key，否则从环境变量读取
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("未找到 GEMINI_API_KEY，请在代码中设置或使用环境变量")

        # 配置 API
        genai.configure(api_key=api_key)

        # 尝试列出可用模型，找到最佳匹配
        self.model_name = self._find_best_model(model)

        # 创建生成器
        self.model = genai.GenerativeModel(self.model_name)

        print(f"[Gemini] [OK] Initialized - Model: {self.model_name}")

    def _find_best_model(self, preferred: str) -> str:
        """
        查找最佳可用的模型

        Args:
            preferred: 首选模型名称

        Returns:
            实际可用的模型名称
        """
        # 根据实际可用的模型列表（2026年1月）
        candidates = [
            preferred,  # 用户指定的
            "models/gemini-3-pro-preview",  # Gemini 3 Pro Preview
            "models/gemini-2.5-pro",  # Gemini 2.5 Pro（稳定版）
            "models/gemini-2.0-flash-exp",  # Gemini 2.0 Flash Experimental
            "models/gemini-pro-latest",  # 保底选项
        ]

        # 尝试使用首选模型
        return candidates[0]

    def ask(self, prompt: str, context: str = "") -> str:
        """
        向 Gemini 提问

        Args:
            prompt: 问题
            context: 额外的上下文

        Returns:
            Gemini 的回答
        """
        full_prompt = prompt
        if context:
            full_prompt = f"上下文：{context}\n\n问题：{prompt}"

        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"错误：{str(e)}"

    def deep_think(self, task: str) -> str:
        """
        使用深度思考模式

        Args:
            task: 需要深度思考的任务

        Returns:
            思考结果
        """
        prompt = f"""你是一位顶尖的专家，请对以下任务进行深度思考和推理：

任务：{task}

要求：
1. 进行多角度分析
2. 考虑各种可能性
3. 提供深度的见解
4. 给出具体的建议

请输出你的分析和结论。"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"错误：{str(e)}"

    def evaluate_ai_score(self, text: str) -> int:
        """
        评估文本的 AI 浓度

        Args:
            text: 待评估的文本

        Returns:
            AI 评分 (0-100)
        """
        # 截取前 2000 字
        sample = text[:2000] if len(text) > 2000 else text

        prompt = f"""请评估以下文本的 AI 浓度（0-100分）：

文本：
{sample}

评估标准：
- 0-30分：像人写的
- 30-60分：有些 AI 痕迹
- 60-100分：明显是 AI 写的

只需输出一个数字（0-100），不要解释。"""

        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip()

            # 提取数字
            import re
            match = re.search(r'\d+', result)
            if match:
                score = int(match.group())
                return max(0, min(100, score))

            return 50  # 默认值
        except Exception as e:
            print(f"[Gemini] 评估失败: {e}")
            return 50

    def humanize(self, text: str, current_score: int = None) -> str:
        """
        重写文本使其更像人类

        Args:
            text: 原文
            current_score: 当前 AI 评分（可选）

        Returns:
            重写后的文本
        """
        prompt = f"""请重写以下文本，使其更像真人写的：

{'当前 AI 评分：' + str(current_score) if current_score else ''}

要求：
1. 增加口语化表达
2. 打乱句式结构
3. 加入个人观点和情感
4. 使用地道的中文
5. 避免"综上所述"、"首先其次"等 AI 用词
6. 长短句交替
7. 适当使用反问、感叹

原文：
{text}

请直接输出重写后的内容："""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"[Gemini] 重写失败: {e}")
            return text

    def generate_article(self, domain: str = "情感,心理") -> dict:
        """
        完整的公众号文章生成流程

        Args:
            domain: 内容领域

        Returns:
            包含文章信息的字典
        """
        print(f"\n{'='*60}")
        print("Gemini 3 Pro 公众号文章生成")
        print(f"{'='*60}\n")

        # 步骤 1：选题
        print("[1/4] 正在深度思考爆款选题...")
        topic_prompt = f"""作为公众号运营专家，请在 {domain} 领域构思一个爆款选题。

要求：
1. 标题吸睛（不超过 30 字）
2. 有争议性或共鸣点
3. 给出简要大纲

格式：
标题：《XXX》
大纲：XXX"""

        topic_result = self.ask(topic_prompt)
        print(f"✓ 选题完成\n")

        # 解析标题
        title = "AI时代的思考"
        if "《" in topic_result and "》" in topic_result:
            start = topic_result.find("《") + 1
            end = topic_result.find("》")
            title = topic_result[start:end]

        # 步骤 2：写作
        print(f"[2/4] 正在撰写文章（约 2000 字）...")
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

        article = self.ask(article_prompt)
        print(f"✓ 文章撰写完成（{len(article)} 字）\n")

        # 步骤 3-5：优化循环
        print(f"[3/4] AI 率优化（最多 5 次）...\n")

        best_article = article
        best_score = 100

        for i in range(1, 6):
            print(f"第 {i} 次迭代：")

            # 评估
            score = self.evaluate_ai_score(article)
            print(f"  AI 评分：{score}%")

            if score < best_score:
                best_score = score
                best_article = article

            if score < 30:
                print(f"  ✓ 达标！AI 率已降至 {score}%\n")
                break

            if i == 5:
                print(f"  已达最大次数，使用最佳版本（{best_score}%）\n")
                article = best_article
                break

            print(f"  → 进行人话化重写...")
            article = self.humanize(article, score)
            print(f"  ✓ 重写完成\n")

        # 步骤 4：保存
        print(f"[4/4] 保存文章...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gemini_article_{timestamp}.md"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"**AI 评分**：{best_score}%\n\n")
            f.write("---\n\n")
            f.write(article)

        print(f"✓ 已保存到：{filename}")

        return {
            "title": title,
            "content": article,
            "ai_score": best_score,
            "filename": filename
        }


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="Gemini 3 Pro 工具 - 可被 CC 调用的超级专家",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  python gemini_tool.py "你的问题"
  python gemini_tool.py --deep-think "复杂任务"
  python gemini_tool.py --article --domain "情感,心理"
        """
    )

    parser.add_argument("prompt", nargs="?", help="问题或任务描述")
    parser.add_argument("--deep-think", action="store_true", help="使用深度思考模式")
    parser.add_argument("--evaluate", action="store_true", help="评估 AI 率")
    parser.add_argument("--humanize", action="store_true", help="人工化重写")
    parser.add_argument("--article", action="store_true", help="生成完整文章")
    parser.add_argument("--domain", default="情感,心理", help="内容领域（用于 --article）")
    parser.add_argument("--model", default="models/gemini-3-pro-preview", help="指定模型（默认：Gemini 3 Pro）")
    parser.add_argument("--api-key", help="API Key（或使用 GEMINI_API_KEY 环境变量）")

    args = parser.parse_args()

    # 初始化工具
    try:
        tool = GeminiTool(api_key=args.api_key, model=args.model)
    except ValueError as e:
        print(f"错误：{e}")
        sys.exit(1)

    # 根据参数执行不同功能
    if args.article:
        # 生成完整文章
        result = tool.generate_article(args.domain)
        print(f"\n最终结果：")
        print(f"  标题：{result['title']}")
        print(f"  AI 评分：{result['ai_score']}%")
        print(f"  文件：{result['filename']}")

    elif args.evaluate:
        # 评估 AI 率
        if not args.prompt:
            print("错误：--evaluate 需要提供文本")
            sys.exit(1)

        # 读取文件或直接使用文本
        if os.path.exists(args.prompt):
            with open(args.prompt, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            text = args.prompt

        score = tool.evaluate_ai_score(text)
        print(f"\nAI 评分：{score}%")

    elif args.humanize:
        # 人工化重写
        if not args.prompt:
            print("错误：--humanize 需要提供文本")
            sys.exit(1)

        if os.path.exists(args.prompt):
            with open(args.prompt, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            text = args.prompt

        result = tool.humanize(text)
        print(f"\n{result}")

    elif args.deep_think:
        # 深度思考
        if not args.prompt:
            print("错误：--deep-think 需要提供任务")
            sys.exit(1)

        result = tool.deep_think(args.prompt)
        print(f"\n{result}")

    else:
        # 普通问答
        if not args.prompt:
            parser.print_help()
            sys.exit(1)

        result = tool.ask(args.prompt)
        print(f"\n{result}")


if __name__ == "__main__":
    main()
