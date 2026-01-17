"""
封面图生成模块
支持多种方式生成文章封面图
"""

import os
import requests
from datetime import datetime
import re


class CoverGenerator:
    """封面图生成器"""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.use_placeholder = os.getenv("USE_PLACEHOLDER_COVER", "false").lower() == "true"

    def generate_cover(self, title, article_content, style="elegant", output_dir="."):
        """
        生成封面图

        Args:
            title: 文章标题
            article_content: 文章内容（用于分析主题）
            style: 封面风格 (elegant, tech, warm, bold, minimal, playful, nature, retro)
            output_dir: 输出目录

        Returns:
            dict: {
                "success": bool,
                "image_path": str,
                "method": str,
                "error": str (if failed)
            }
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"cover_{timestamp}.png"
        image_path = os.path.join(output_dir, image_filename)

        # 方式1: 尝试使用 OpenAI DALL-E
        if self.openai_api_key:
            result = self._generate_with_dalle(title, article_content, style, image_path)
            if result["success"]:
                return result

        # 方式2: 使用占位符
        if self.use_placeholder:
            result = self._generate_placeholder(title, style, image_path)
            if result["success"]:
                return result

        # 方式3: 跳过封面图
        return {
            "success": False,
            "image_path": None,
            "method": "none",
            "error": "No image generation method configured"
        }

    def _generate_with_dalle(self, title, article_content, style, image_path):
        """使用 OpenAI DALL-E 生成封面"""
        try:
            # 分析文章内容，提取关键词
            keywords = self._extract_keywords(article_content)

            # 根据风格构建提示词
            style_prompts = {
                "elegant": "elegant, sophisticated, minimalist, soft gradient colors, clean composition",
                "tech": "modern, futuristic, geometric shapes, circuit patterns, glowing effects, tech style",
                "warm": "friendly, warm colors, rounded shapes, sunshine, inviting atmosphere",
                "bold": "high contrast, vibrant colors, dramatic, eye-catching, bold typography",
                "minimal": "ultra-clean, zen-like, black and white with one accent color, lots of whitespace",
                "playful": "fun, pastel colors, doodles, cute elements, whimsical style",
                "nature": "organic, earthy tones, plant motifs, natural textures, calming",
                "retro": "vintage, muted colors, nostalgic, classic illustration style"
            }

            style_prompt = style_prompts.get(style, style_prompts["elegant"])

            # 构建完整提示词
            prompt = f"""Create a cover image for an article titled "{title}".
Style: {style_prompt}
Keywords: {', '.join(keywords[:5])}
Format: Horizontal wide image (2.35:1 ratio), perfect for article cover.
Design: Clean, professional, suitable for Chinese social media."""

            # 调用 DALL-E API
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "dall-e-3",
                    "prompt": prompt,
                    "n": 1,
                    "size": "1024x1792",  # 横向比例
                    "response_format": "url"
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                image_url = data["data"][0]["url"]

                # 下载图片
                img_response = requests.get(image_url, timeout=30)
                if img_response.status_code == 200:
                    with open(image_path, 'wb') as f:
                        f.write(img_response.content)

                    return {
                        "success": True,
                        "image_path": image_path,
                        "method": "dalle",
                        "error": None
                    }

            return {
                "success": False,
                "image_path": None,
                "method": "dalle",
                "error": f"API error: {response.status_code}"
            }

        except Exception as e:
            return {
                "success": False,
                "image_path": None,
                "method": "dalle",
                "error": str(e)
            }

    def _generate_placeholder(self, title, style, image_path):
        """生成占位符封面（使用文本和渐变色）"""
        try:
            from PIL import Image, ImageDraw, ImageFont

            # 创建横向图片 (2.35:1)
            width, height = 1080, 460
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)

            # 根据风格选择颜色
            colors = {
                "elegant": {'bg': '#F5F0E6', 'accent': '#5B8A8A', 'text': '#2D3748'},
                "tech": {'bg': '#1A202C', 'accent': '#00D4FF', 'text': '#FFFFFF'},
                "warm": {'bg': '#FFFAF0', 'accent': '#ED8936', 'text': '#2D3748'},
                "bold": {'bg': '#000000', 'accent': '#F6E05E', 'text': '#FFFFFF'},
                "minimal": {'bg': '#FFFFFF', 'accent': '#000000', 'text': '#000000'},
                "playful": {'bg': '#FFFBEB', 'accent': '#9F7AEA', 'text': '#2D3748'},
                "nature": {'bg': '#F5E6D3', 'accent': '#276749', 'text': '#2D3748'},
                "retro": {'bg': '#F5E6D3', 'accent': '#C05621', 'text': '#2D3748'}
            }

            color_scheme = colors.get(style, colors["elegant"])

            # 绘制背景
            draw.rectangle([(0, 0), (width, height)], fill=color_scheme['bg'])

            # 绘制装饰元素（简单的几何形状）
            accent_color = color_scheme['accent']
            draw.rectangle([(50, 50), (200, 410)], fill=accent_color)  # 左侧装饰条
            draw.ellipse([(width-250, 50), (width-50, 200)], fill=accent_color)  # 右上圆形

            # 绘制标题
            try:
                # 尝试使用中文字体
                font_large = ImageFont.truetype("msyh.ttc", 48)  # 微软雅黑
                font_small = ImageFont.truetype("msyh.ttc", 24)
            except:
                # 如果找不到中文字体，使用默认字体
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()

            # 截断标题（最多15个字符）
            display_title = title[:15] + "..." if len(title) > 15 else title

            # 绘制标题文字
            text_color = color_scheme['text']
            draw.text((250, 180), display_title, fill=text_color, font=font_large)

            # 绘制副标题
            subtitle = f"{datetime.now().strftime('%Y年%m月%d日')}"
            draw.text((250, 240), subtitle, fill=text_color, font=font_small)

            # 保存图片
            img.save(image_path, 'PNG')

            return {
                "success": True,
                "image_path": image_path,
                "method": "placeholder",
                "error": None
            }

        except ImportError:
            return {
                "success": False,
                "image_path": None,
                "method": "placeholder",
                "error": "PIL not installed. Run: pip install Pillow"
            }
        except Exception as e:
            return {
                "success": False,
                "image_path": None,
                "method": "placeholder",
                "error": str(e)
            }

    def _extract_keywords(self, content, max_keywords=10):
        """从文章内容中提取关键词"""
        # 简单的关键词提取（基于常见词频）
        common_words = {'的', '了', '是', '在', '我', '你', '他', '她', '它', '我们', '他们', '这', '那', '有', '没有', '会', '能', '可以', '但是', '因为', '所以', '如果', '虽然', '然后', '还是', '或者', '和', '与', '及'}

        # 分词（简单按空格和标点）
        words = re.findall(r'[\u4e00-\u9fa5]{2,4}', content)

        # 统计词频
        word_count = {}
        for word in words:
            if word not in common_words and len(word) >= 2:
                word_count[word] = word_count.get(word, 0) + 1

        # 排序并返回前N个
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [word[0] for word in sorted_words[:max_keywords]]


# 便捷函数
def generate_cover_for_article(title, content, style="elegant", output_dir="."):
    """为文章生成封面图的便捷函数"""
    generator = CoverGenerator()
    return generator.generate_cover(title, content, style, output_dir)


if __name__ == "__main__":
    # 测试
    test_title = "成年人的顶级自律是学会主动掉队"
    test_content = """这是一篇关于个人成长的心理学文章，讲述在社交媒体时代，
    学会主动掉队、不回消息是一种内心平静的信号，是成年人最顶级的自律。"""

    result = generate_cover_for_article(test_title, test_content, style="elegant", output_dir=".")
    print(f"生成结果: {result}")
