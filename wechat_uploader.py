"""
微信公众号发布脚本
功能：将文章上传到公众号草稿箱
"""

from wechatpy import WeChatClient
from wechatpy.exceptions import WeChatClientException
import requests
import json
import time


class WeChatUploader:
    """微信公众号文章上传器"""

    def __init__(self, app_id: str, app_secret: str):
        """
        初始化微信客户端

        Args:
            app_id: 微信公众号 AppID
            app_secret: 微信公众号 AppSecret
        """
        self.app_id = app_id
        self.app_secret = app_secret

        try:
            self.client = WeChatClient(app_id, app_secret)
            print("[WeChat] 微信客户端初始化成功")
        except Exception as e:
            print(f"[WeChat] ✗ 初始化失败: {e}")
            self.client = None

    def get_access_token(self) -> str:
        """获取 Access Token"""
        if not self.client:
            return None

        try:
            # WeChatClient 会自动管理 access_token
            return self.client.access_token
        except Exception as e:
            print(f"[WeChat] ✗ 获取 Access Token 失败: {e}")
            return None

    def upload_thumb(self, image_path: str = None, use_default: bool = True) -> str:
        """
        上传封面图，获取 media_id

        Args:
            image_path: 本地图片路径（如果为None则使用默认）
            use_default: 是否使用默认封面

        Returns:
            media_id: 素材的 media_id
        """
        if not self.client:
            return None

        # 如果有指定图片，上传该图片
        if image_path:
            try:
                with open(image_path, 'rb') as f:
                    result = self.client.material.add('thumb', f)
                    media_id = result['media_id']
                    print(f"[WeChat] ✓ 封面图上传成功: {media_id}")
                    return media_id
            except Exception as e:
                print(f"[WeChat] ✗ 上传封面图失败: {e}")
                return None

        # 使用默认封面（需要在配置中设置）
        if use_default:
            # 返回一个默认的 media_id
            # 用户需要在公众号后台手动上传一张图片，然后获取其 media_id
            default_media_id = "YOUR_DEFAULT_THUMB_MEDIA_ID"
            if default_media_id.startswith("YOUR_"):
                print("[WeChat] ⚠ 警告：未配置默认封面 media_id")
                print("[WeChat] 请在公众号后台上传封面图，并将 media_id 填入代码中")
                return None
            return default_media_id

        return None

    def upload_draft(self, title: str, content: str, thumb_media_id: str = None,
                     author: str = "", digest: str = "", show_cover_pic: int = 1) -> bool:
        """
        上传文章到草稿箱

        Args:
            title: 文章标题
            content: 文章内容（HTML格式）
            thumb_media_id: 封面图 media_id
            author: 作者
            digest: 摘要
            show_cover_pic: 是否显示封面图（0=不显示，1=显示）

        Returns:
            是否成功
        """
        if not self.client:
            print("[WeChat] ✗ 客户端未初始化")
            return False

        print(f"[WeChat] 正在上传草稿...")
        print(f"[WeChat] 标题：{title}")

        # 如果没有提供封面图，尝试上传
        if not thumb_media_id:
            thumb_media_id = self.upload_thumb(use_default=True)
            if not thumb_media_id:
                print("[WeChat] ⚠ 警告：无法上传封面图，将不显示封面")
                show_cover_pic = 0

        # 构建文章数据
        articles = {
            "articles": [
                {
                    "title": title,
                    "author": author,
                    "digest": digest,
                    "content": content,
                    "content_source_url": "",
                    "thumb_media_id": thumb_media_id,
                    "show_cover_pic": show_cover_pic,
                    "need_open_comment": 1,  # 打开评论
                    "only_fans_can_comment": 0  # 所有人可评论
                }
            ]
        }

        try:
            # 调用草稿箱接口
            result = self.client.draft.add(articles)

            if 'media_id' in result:
                print(f"[WeChat] ✓ 草稿已保存成功！")
                print(f"[WeChat] Media ID: {result['media_id']}")
                print(f"[WeChat] 请登录公众号后台查看草稿箱")
                return True
            else:
                print(f"[WeChat] ✗ 上传失败: {result}")
                return False

        except WeChatClientException as e:
            print(f"[WeChat] ✗ API错误: {e}")
            print(f"[WeChat] 错误码：{e.errcode}")
            print(f"[WeChat] 错误信息：{e.errmsg}")

            # 常见错误提示
            if e.errcode == 40001:
                print("[WeChat] 提示：AppID 或 AppSecret 可能不正确")
            elif e.errcode == 40164:
                print("[WeChat] 提示：IP地址不在白名单中，请在公众号后台配置")
            elif e.errcode == 45009:
                print("[WeChat] 提示：接口调用超过限制")

            return False

        except Exception as e:
            print(f"[WeChat] ✗ 未知错误: {e}")
            return False

    def markdown_to_html(self, markdown_text: str) -> str:
        """
        将 Markdown 转换为 HTML（公众号需要HTML格式）

        Args:
            markdown_text: Markdown 格式文本

        Returns:
            HTML 格式文本
        """
        try:
            import markdown
            html = markdown.markdown(markdown_text)
            return html
        except ImportError:
            print("[WeChat] ⚠ 警告：未安装 markdown 库，将直接使用原文")
            print("[WeChat] 安装命令: pip install markdown")
            return markdown_text
        except Exception as e:
            print(f"[WeChat] ✗ Markdown转换失败: {e}")
            return markdown_text


# 测试代码
if __name__ == "__main__":
    # 这里需要填入你的微信公众号信息
    APP_ID = "YOUR_WECHAT_APP_ID"
    APP_SECRET = "YOUR_WECHAT_APP_SECRET"

    if APP_ID == "YOUR_WECHAT_APP_ID":
        print("请先在代码中填入你的微信公众号 AppID 和 AppSecret")
        print("\n获取方式：")
        print("1. 登录微信公众平台：https://mp.weixin.qq.com")
        print("2. 进入「开发」->「基本配置」")
        print("3. 查看并复制 AppID 和 AppSecret")
    else:
        uploader = WeChatUploader(APP_ID, APP_SECRET)

        # 测试上传
        test_title = "测试文章标题"
        test_content = "<p>这是测试文章内容。</p>"

        success = uploader.upload_draft(
            title=test_title,
            content=test_content,
            author="AI助手",
            digest="这是一篇测试文章"
        )

        if success:
            print("\n测试成功！")
        else:
            print("\n测试失败，请检查配置")
