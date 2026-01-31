"""图片处理器 - 上传图片到微信素材库并替换链接"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)


class ImageProcessor:
    """处理文章中的图片：上传到微信素材库并替换链接"""

    def __init__(self, api_client, temp_dir: Path):
        """
        初始化图片处理器

        Args:
            api_client: 微信 API 客户端实例
            temp_dir: 临时目录
        """
        self.api_client = api_client
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def process_images(self, html_content: str, images: List[Dict], media_type: str = "image") -> str:
        """
        处理 HTML 中的所有图片：上传并替换链接

        Args:
            html_content: HTML 内容
            images: 图片信息列表（从 ImageExtractor 获取）
            media_type: 素材类型 ('image' 或 'thumb')

        Returns:
            替换后的 HTML 内容
        """
        if not images:
            logger.info("[ImageProcessor] 没有需要处理的图片")
            return html_content

        logger.info(f"[ImageProcessor] 开始处理 {len(images)} 张图片")

        success_count = 0
        processed_html = html_content

        # 从后往前替换，避免位置偏移
        for i, image_info in enumerate(reversed(images)):
            try:
                original_path = image_info['path']
                local_path = image_info.get('local_path')

                # 跳过无法访问的本地图片
                if not local_path or not Path(local_path).exists():
                    logger.warning(f"[ImageProcessor] 图片不存在，跳过: {original_path}")
                    continue

                # 上传图片到微信素材库
                logger.info(f"[ImageProcessor] [{i+1}/{len(images)}] 上传图片: {Path(local_path).name}")
                result = self.api_client.upload_media(str(local_path), media_type)

                # 获取微信 CDN URL
                wechat_url = result.get('url', '')
                media_id = result.get('media_id', '')

                if not wechat_url:
                    logger.warning(f"[ImageProcessor] 未获取到 URL，使用 media_id: {media_id}")
                    continue

                logger.info(f"[ImageProcessor] 图片上传成功: {wechat_url}")

                # 替换 HTML 中的图片链接
                processed_html = self._replace_image_url(processed_html, original_path, wechat_url)
                success_count += 1

                # 标记为已上传
                image_info['uploaded'] = True
                image_info['wechat_url'] = wechat_url
                image_info['media_id'] = media_id

            except Exception as e:
                logger.error(f"[ImageProcessor] 处理图片失败: {image_info.get('path', 'unknown')}, 错误: {e}")
                image_info['uploaded'] = False

        logger.info(f"[ImageProcessor] 图片处理完成: {success_count}/{len(images)} 张成功")
        return processed_html

    def _replace_image_url(self, html_content: str, old_url: str, new_url: str) -> str:
        """
        替换 HTML 中的图片 URL

        Args:
            html_content: HTML 内容
            old_url: 原始 URL
            new_url: 新 URL

        Returns:
            替换后的 HTML 内容
        """
        # 替换 <img> 标签中的 src
        pattern = r'(<img[^>]+src=["\'])' + re.escape(old_url) + r'(["\'][^>]*>)'
        html_content = re.sub(pattern, r'\1' + new_url + r'\2', html_content)

        return html_content

    def batch_upload_images(self, image_paths: List[Path], media_type: str = "image") -> Dict[str, str]:
        """
        批量上传图片并返回 URL 映射

        Args:
            image_paths: 图片路径列表
            media_type: 素材类型

        Returns:
            {本地路径: 微信 URL} 映射字典
        """
        url_mapping = {}

        for image_path in image_paths:
            try:
                logger.info(f"[ImageProcessor] 上传: {image_path.name}")
                result = self.api_client.upload_media(str(image_path), media_type)

                wechat_url = result.get('url', '')
                if wechat_url:
                    url_mapping[str(image_path)] = wechat_url
                    logger.info(f"[ImageProcessor] 成功: {wechat_url}")
                else:
                    logger.warning(f"[ImageProcessor] 未获取到 URL: {image_path.name}")

            except Exception as e:
                logger.error(f"[ImageProcessor] 上传失败: {image_path.name}, 错误: {e}")

        return url_mapping

    def extract_and_upload_from_html(self, html_content: str, base_path: Path = None, media_type: str = "image") -> str:
        """
        从 HTML 中提取图片，上传到微信，并替换链接（一站式处理）

        Args:
            html_content: HTML 内容
            base_path: 文档所在目录（用于解析相对路径）
            media_type: 素材类型

        Returns:
            处理后的 HTML 内容
        """
        from utils.image_extractor import ImageExtractor

        # 提取图片
        extractor = ImageExtractor(self.temp_dir)
        images, local_images = extractor.extract_and_prepare_images(html_content, 'html', base_path)

        if not images:
            return html_content

        # 处理图片（上传并替换链接）
        return self.process_images(html_content, images, media_type)


def extract_images_from_html(html_content: str, temp_dir: Path) -> List[Dict]:
    """
    便捷函数：从 HTML 中提取图片信息

    Args:
        html_content: HTML 内容
        temp_dir: 临时目录

    Returns:
        图片信息列表
    """
    from utils.image_extractor import ImageExtractor

    extractor = ImageExtractor(temp_dir)
    images, _ = extractor.extract_and_prepare_images(html_content, 'html')
    return images
