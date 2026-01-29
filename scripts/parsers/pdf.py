"""PDF 文档解析器"""

import logging
from pathlib import Path
from typing import List

import fitz  # PyMuPDF
from parsers.base import BaseParser, ParsedContent

logger = logging.getLogger(__name__)


class PDFParser(BaseParser):
    """PDF 文档解析器"""

    def parse(self, file_path: Path) -> ParsedContent:
        """解析 PDF 文档"""
        logger.info(f"[PDFParser] 开始解析: {file_path}")

        try:
            doc = fitz.open(file_path)

            # 提取标题（使用第一页的第一行，或元数据）
            title = self._extract_title(doc)

            # 提取所有页面内容
            content_parts = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                if text.strip():
                    # 将页面文本转换为 Markdown 格式
                    content_parts.append(self._convert_page(text, page_num))

            content = "\n\n".join(content_parts)

            # 提取图片
            images = self._extract_images(doc, file_path)

            # 提取元数据
            metadata = self._extract_metadata(doc)

            doc.close()

            result = ParsedContent(
                title=title,
                content=content,
                images=images,
                metadata=metadata,
            )

            logger.info(
                f"[PDFParser] 解析完成 - 标题: {title}, 页数: {len(doc)}, 图片数: {len(images)}"
            )
            return result

        except Exception as e:
            logger.error(f"[PDFParser] 解析失败: {e}")
            from exceptions import FileReadError
            raise FileReadError(str(file_path), str(e))

    def _extract_title(self, doc) -> str:
        """提取标题"""
        # 尝试从元数据获取标题
        metadata = doc.metadata
        if metadata and "title" in metadata and metadata["title"]:
            return metadata["title"]

        # 否则使用第一页的第一行
        first_page = doc[0]
        text = first_page.get_text("text")
        lines = text.strip().split("\n")
        if lines and lines[0].strip():
            title = lines[0].strip()
            # 限制标题长度
            if len(title) > 50:
                return title[:50] + "..."
            return title

        return "未命名文档"

    def _convert_page(self, text: str, page_num: int) -> str:
        """将页面文本转换为 Markdown 格式"""
        lines = text.strip().split("\n")
        converted_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 尝试识别标题（通常是较大且居中的文本）
            # PDF 文本提取较难准确识别结构，这里做简单处理
            if len(line) < 50 and line == line.upper() and not line.endswith("."):
                # 可能是标题
                converted_lines.append(f"## {line}")
            else:
                converted_lines.append(line)

        return "\n".join(converted_lines)

    def _extract_images(self, doc, file_path: Path) -> List[Path]:
        """提取图片引用（PDF 解析器暂不支持图片提取）"""
        # PDF 图片提取较复杂，暂不支持
        return []

    def _extract_metadata(self, doc) -> dict:
        """提取元数据"""
        metadata = doc.metadata
        return {
            "author": metadata.get("author", ""),
            "title": metadata.get("title", ""),
            "subject": metadata.get("subject", ""),
            "keywords": metadata.get("keywords", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
        }

    def supports(self, file_path: Path) -> bool:
        """判断是否支持该文件类型"""
        return file_path.suffix.lower() == ".pdf"
