"""图片提取器 - 从文档中提取图片引用"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from urllib.parse import urlparse
import requests

logger = logging.getLogger(__name__)


class ImageExtractor:
    """从 Markdown 或 HTML 中提取图片引用"""

    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def extract_from_markdown(self, content: str, base_path: Path) -> List[Dict]:
        """
        从 Markdown 中提取图片引用

        Args:
            content: Markdown 内容
            base_path: Markdown 文件所在目录，用于解析相对路径

        Returns:
            图片信息列表: [{'path': '原始路径', 'type': 'local|http|https', 'index': 位置}]
        """
        images = []

        # 匹配 Markdown 图片语法 ![alt](path)
        pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        matches = re.finditer(pattern, content)

        for i, match in enumerate(matches):
            alt_text = match.group(1)
            image_path = match.group(2).strip()

            # 解析图片路径类型
            if image_path.startswith(('http://', 'https://')):
                image_type = 'remote'
            elif image_path.startswith('/'):
                image_type = 'absolute'
            else:
                image_type = 'relative'

            images.append({
                'path': image_path,
                'alt': alt_text,
                'type': image_type,
                'base_path': base_path,
                'index': i
            })
            logger.debug(f"[ImageExtractor] 找到图片: {image_path} (类型: {image_type})")

        logger.info(f"[ImageExtractor] 从 Markdown 中提取到 {len(images)} 张图片")
        return images

    def extract_from_html(self, content: str) -> List[Dict]:
        """
        从 HTML 中提取图片引用

        Args:
            content: HTML 内容

        Returns:
            图片信息列表
        """
        images = []

        # 匹配 HTML img 标签
        pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        matches = re.finditer(pattern, content)

        for i, match in enumerate(matches):
            image_path = match.group(1)

            if image_path.startswith(('http://', 'https://')):
                image_type = 'remote'
            elif image_path.startswith('/'):
                image_type = 'absolute'
            else:
                image_type = 'relative'

            images.append({
                'path': image_path,
                'type': image_type,
                'index': i
            })
            logger.debug(f"[ImageExtractor] 从 HTML 找到图片: {image_path}")

        logger.info(f"[ImageExtractor] 从 HTML 中提取到 {len(images)} 张图片")
        return images

    def resolve_local_path(self, image_info: Dict) -> Path:
        """
        解析本地图片路径

        Args:
            image_info: 图片信息字典

        Returns:
            解析后的完整路径
        """
        image_path = image_info['path']

        if image_info['type'] == 'absolute':
            # 绝对路径
            return Path(image_path)
        elif image_info['type'] == 'relative':
            # 相对路径，相对于 base_path
            base_path = image_info.get('base_path', Path('.'))
            return base_path / image_path
        else:
            # 远程图片，不处理
            return None

    def download_remote_image(self, url: str, filename: str) -> Path:
        """
        下载远程图片到临时目录

        Args:
            url: 图片 URL
            filename: 保存的文件名

        Returns:
            本地文件路径
        """
        local_path = self.temp_dir / filename

        try:
            logger.info(f"[ImageExtractor] 下载远程图片: {url}")
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()

            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"[ImageExtractor] 图片已保存: {local_path}")
            return local_path

        except Exception as e:
            logger.error(f"[ImageExtractor] 下载图片失败: {url}, 错误: {e}")
            raise

    def extract_and_prepare_images(self, content: str, content_type: str = 'markdown', base_path: Path = None) -> Tuple[List[Dict], List[Path]]:
        """
        提取并准备所有图片（下载远程图片到本地）

        Args:
            content: 文档内容
            content_type: 内容类型 ('markdown' 或 'html')
            base_path: 文档所在目录

        Returns:
            (图片信息列表, 本地图片路径列表)
        """
        base_path = base_path or Path('.')

        # 提取图片引用
        if content_type == 'markdown':
            images = self.extract_from_markdown(content, base_path)
        else:
            images = self.extract_from_html(content)

        local_images = []

        for image_info in images:
            if image_info['type'] == 'remote':
                # 下载远程图片
                filename = self._generate_filename(image_info['path'])
                local_path = self.download_remote_image(image_info['path'], filename)
                image_info['local_path'] = local_path
                local_images.append(local_path)
            else:
                # 本地图片，直接使用
                local_path = self.resolve_local_path(image_info)
                if local_path and local_path.exists():
                    image_info['local_path'] = local_path
                    local_images.append(local_path)

        return images, local_images

    def _generate_filename(self, url: str) -> str:
        """从 URL 生成文件名"""
        parsed = urlparse(url)
        path = parsed.path

        # 提取文件名
        filename = Path(path).name

        # 如果没有扩展名，添加 .jpg
        if not Path(filename).suffix:
            filename = f"{filename}.jpg"

        # 确保文件名唯一
        counter = 0
        base_name = Path(filename).stem
        ext = Path(filename).suffix

        while (self.temp_dir / filename).exists():
            counter += 1
            filename = f"{base_name}_{counter}{ext}"

        return filename
