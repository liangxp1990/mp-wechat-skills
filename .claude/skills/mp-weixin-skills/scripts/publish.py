#!/usr/bin/env python3
"""
简化的发布脚本 - 接收 AI 生成的 HTML 和封面，上传到微信公众号

这是 AI 生成内容后的上传接口，不依赖 parsers/converters/covers 模块。
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# 添加 scripts 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from config import AppConfig
from wechat.api_client import WechatApiClient, WechatConfig
from exceptions import WechatApiError


def publish_article(
    title: str,
    html_content: str,
    cover_path: str,
    author: str = "",
    digest: str = "",
) -> str:
    """
    发布文章到微信公众号草稿箱

    Args:
        title: 文章标题
        html_content: 文章 HTML 内容（带内联样式）
        cover_path: 封面图片路径
        author: 作者（可选）
        digest: 摘要（可选）

    Returns:
        media_id: 草稿的 media_id
    """
    logger.info(f"[Publish] 开始发布文章 - 标题: {title}")

    # 加载配置
    config = AppConfig.from_env()
    wechat_config = WechatConfig(
        app_id=config.wechat_app_id,
        app_secret=config.wechat_app_secret,
    )

    # 初始化微信 API 客户端
    api_client = WechatApiClient(wechat_config)

    # 上传封面
    logger.info(f"[Publish] 上传封面: {cover_path}")
    cover_result = api_client.upload_media(cover_path, media_type="thumb")
    thumb_media_id = cover_result["media_id"]
    logger.info(f"[Publish] 封面上传成功 - media_id: {thumb_media_id}")

    # 构建文章数据
    article = {
        "title": title,
        "author": author,
        "digest": digest or _extract_digest(html_content),
        "content": html_content,
        "content_source_url": "",
        "thumb_media_id": thumb_media_id,
        "show_cover_pic": 1,
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
    }

    # 上传草稿
    logger.info(f"[Publish] 上传草稿...")
    result = api_client.upload_draft([article])
    media_id = result.get("media_id", "")

    logger.info(f"[Publish] 发布成功 - media_id: {media_id}")
    return media_id


def _extract_digest(html_content: str, max_length: int = 120) -> str:
    """从 HTML 内容中提取摘要"""
    import re

    # 移除 HTML 标签
    text = re.sub(r"<[^>]+>", "", html_content)
    # 移除多余空白
    text = re.sub(r"\s+", " ", text).strip()
    # 截断（注意微信的限制可能是字符数或字节数）
    if len(text) > max_length:
        # 对于中文，需要考虑字节数限制（UTF-8 编码）
        text_bytes = text.encode('utf-8')
        if len(text_bytes) > max_length:
            # 粗略估算：中文字符约 3 字节，所以字符数限制约为 max_length/3
            char_limit = max_length // 3
            text = text[:char_limit] + "..."
    return text


def main():
    """命令行入口"""
    if len(sys.argv) < 4:
        print("用法: python3 scripts/publish.py <标题> <HTML文件> <封面图片路径>")
        print("示例: python3 scripts/publish.py '文章标题' article.html cover.jpg")
        sys.exit(1)

    title = sys.argv[1]
    html_file = sys.argv[2]
    cover_path = sys.argv[3]

    # 读取 HTML 内容
    html_content = Path(html_file).read_text(encoding="utf-8")

    # 发布文章
    try:
        media_id = publish_article(
            title=title,
            html_content=html_content,
            cover_path=cover_path,
        )
        print(f"\n✅ 文章发布成功!")
        print(f"   Media ID: {media_id}")
        print(f"   📝 请在微信公众号后台查看草稿")
    except WechatApiError as e:
        print(f"\n❌ 发布失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
