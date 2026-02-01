"""Markdown 解析器"""

import logging
from pathlib import Path
from typing import List
import re

from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode

from parsers.base import BaseParser, ParsedContent

logger = logging.getLogger(__name__)


class MarkdownParser(BaseParser):
    """Markdown 解析器"""

    def __init__(self):
        # 使用 js-default preset 以支持 GFM (GitHub Flavored Markdown) 包括表格
        self.md = MarkdownIt("js-default")

    def supports(self, file_path: Path) -> bool:
        """判断是否支持该文件类型"""
        return file_path.suffix.lower() == ".md"

    def parse(self, file_path: Path) -> ParsedContent:
        """解析 Markdown 文档"""
        logger.info(f"[MarkdownParser] 开始解析: {file_path}")

        if not file_path.exists():
            from exceptions import FileReadError
            raise FileReadError(str(file_path), "文件不存在")

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            from exceptions import FileReadError
            raise FileReadError(str(file_path), str(e))

        # 提取标题（第一个 # 标题）
        title = self._extract_title(content)

        # 转换为 HTML
        html_content = self.md.render(content)

        # 提取图片路径
        images = self._extract_images(file_path, content)

        # 元数据
        metadata = {
            "source_file": str(file_path),
            "author": "",
            "date": "",
        }

        logger.info(f"[MarkdownParser] 解析完成 - 标题: {title}, 图片数: {len(images)}")

        return ParsedContent(
            title=title,
            content=html_content,
            images=images,
            metadata=metadata,
        )

    def _extract_title(self, content: str) -> str:
        """提取标题"""
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        # 如果没有找到标题，使用文件名
        return "未命名文章"

    def _extract_images(self, file_path: Path, content: str) -> List[Path]:
        """提取图片路径"""
        images = []

        # 匹配 ![alt](path) 格式
        pattern = r"!\[.*?\]\((.+?)\)"
        matches = re.findall(pattern, content)

        for match in matches:
            # 处理相对路径
            img_path = Path(match)
            if not img_path.is_absolute():
                img_path = file_path.parent / img_path

            images.append(img_path)

        return images
