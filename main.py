"""
自动化公众号写稿系统 - 主程序
功能：整合选题、写作、AI检测、优化和发布流程
"""

import os
from dotenv import load_dotenv
from gemini_worker import GeminiAgent
from wechat_uploader import WeChatUploader
from datetime import datetime
import json

# 加载环境变量
load_dotenv()


class AutoArticleSystem:
    """自动化文章生成系统"""

    def __init__(self):
        """初始化系统"""
        print("=" * 60)
        print("自动化公众号写稿系统")
        print("=" * 60)
        print()

        # 从环境变量获取配置
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.wechat_app_id = os.getenv("WECHAT_APP_ID", "")
        self.wechat_app_secret = os.getenv("WECHAT_APP_SECRET", "")

        # 配置参数
        self.max_iterations = 5  # 最大优化次数
        self.target_ai_score = 30  # 目标AI评分
        self.article_length = 2000  # 文章字数
        self.domain = "情感,心理,人际关系"  # 内容领域

        # 初始化组件
        self.gemini = None
        self.wechat = None
        self._init_components()

    def _init_components(self):
        """初始化各个组件"""
        # 初始化 Gemini
        if self.gemini_api_key:
            try:
                self.gemini = GeminiAgent(
                    api_key=self.gemini_api_key,
                    thinking_model="gemini-2.0-flash-thinking-exp",
                    pro_model="gemini-1.5-pro"
                )
            except Exception as e:
                print(f"[System] ✗ Gemini 初始化失败: {e}")
        else:
            print("[System] ⚠ 警告：未配置 GEMINI_API_KEY，将跳过 Gemini 功能")

        # 初始化微信
        if self.wechat_app_id and self.wechat_app_secret:
            try:
                self.wechat = WeChatUploader(
                    app_id=self.wechat_app_id,
                    app_secret=self.wechat_app_secret
                )
            except Exception as e:
                print(f"[System] ✗ 微信初始化失败: {e}")
        else:
            print("[System] ⚠ 警告：未配置微信 AppID/AppSecret，将无法上传草稿")

        print()

    def generate_article(self) -> dict:
        """
        生成文章的主流程

        Returns:
            包含文章信息的字典
        """
        if not self.gemini:
            print("[System] ✗ Gemini 未初始化，无法生成文章")
            return None

        print("=" * 60)
        print("步骤 1/4: 选题研究")
        print("=" * 60)

        # 步骤1：选题
        topic_result = self.gemini.research_topic(domain=self.domain)
        title = topic_result['title']
        outline = topic_result['outline']

        print()
        print("=" * 60)
        print("步骤 2/4: 撰写初稿")
        print("=" * 60)

        # 步骤2：写作
        article = self.gemini.write_article(title, outline, self.article_length)

        print()
        print("=" * 60)
        print("步骤 3/4: 优化循环 (最多5次)")
        print("=" * 60)
        print()

        # 步骤3：优化循环
        best_article = article
        best_score = 100
        history = []

        for i in range(1, self.max_iterations + 1):
            print(f"[第 {i}/{self.max_iterations} 次迭代]")

            # 检测 AI 率
            score = self.gemini.evaluate_ai_score(article)
            history.append({
                "iteration": i,
                "score": score,
                "length": len(article)
            })

            # 记录最佳版本
            if score < best_score:
                best_score = score
                best_article = article

            # 判断是否达标
            if score < self.target_ai_score:
                print(f"-> ✓ 成功！AI 率已降至 {score}% (目标: <{self.target_ai_score}%)")
                print()
                break

            # 如果是最后一次，不再重写
            if i == self.max_iterations:
                print(f"-> 已达最大尝试次数，使用最低分版本 ({best_score}%)")
                article = best_article
                break

            # 继续优化
            print(f"-> 当前 AI 率：{score}%，正在进行第 {i} 次人话化重写...")
            article = self.gemini.humanize_rewrite(article, score)
            print()

        return {
            "title": title,
            "content": article,
            "ai_score": best_score,
            "iterations": len(history),
            "history": history
        }

    def upload_to_wechat(self, title: str, content: str) -> bool:
        """
        上传文章到微信公众号草稿箱

        Args:
            title: 文章标题
            content: 文章内容

        Returns:
            是否成功
        """
        if not self.wechat:
            print("[System] ✗ 微信未初始化，无法上传")
            return False

        print()
        print("=" * 60)
        print("步骤 4/4: 上传草稿")
        print("=" * 60)

        # 将内容转换为 HTML（如果需要）
        html_content = self.wechat.markdown_to_html(content)

        # 上传
        success = self.wechat.upload_draft(
            title=title,
            content=html_content,
            author="AI助手",
            digest=f"{title} - AI自动生成",
            show_cover_pic=1
        )

        return success

    def save_to_file(self, article_data: dict):
        """
        将文章保存到本地文件

        Args:
            article_data: 文章数据
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"article_{timestamp}.md"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# {article_data['title']}\n\n")
                f.write(f"AI评分：{article_data['ai_score']}%\n")
                f.write(f"迭代次数：{article_data['iterations']}\n\n")
                f.write("---\n\n")
                f.write(article_data['content'])

            print(f"[System] ✓ 文章已保存到本地: {filename}")

            # 同时保存 JSON 格式的详细数据
            json_filename = f"article_{timestamp}_data.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)

            print(f"[System] ✓ 详细数据已保存: {json_filename}")

        except Exception as e:
            print(f"[System] ✗ 保存文件失败: {e}")

    def run(self, auto_upload: bool = False):
        """
        运行完整流程

        Args:
            auto_upload: 是否自动上传到微信公众号
        """
        # 生成文章
        article_data = self.generate_article()

        if not article_data:
            print("[System] ✗ 生成文章失败")
            return

        # 保存到本地
        self.save_to_file(article_data)

        # 显示最终结果
        print()
        print("=" * 60)
        print("最终结果")
        print("=" * 60)
        print(f"标题：{article_data['title']}")
        print(f"字数：{len(article_data['content'])} 字")
        print(f"AI评分：{article_data['ai_score']}%")
        print(f"迭代次数：{article_data['iterations']}")
        print()
        print("优化历史：")
        for h in article_data['history']:
            print(f"  第{h['iteration']}次: AI率={h['score']}%, 字数={h['length']}")
        print()

        # 自动上传
        if auto_upload:
            self.upload_to_wechat(article_data['title'], article_data['content'])
        else:
            print("[System] 提示：使用 auto_upload=True 可自动上传到草稿箱")
            print("[System] 提示：或者手动运行：python main.py --upload")


def main():
    """主函数"""
    import sys

    # 检查命令行参数
    auto_upload = "--upload" in sys.argv or "-u" in sys.argv

    # 创建并运行系统
    system = AutoArticleSystem()
    system.run(auto_upload=auto_upload)


if __name__ == "__main__":
    main()
