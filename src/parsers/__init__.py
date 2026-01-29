"""文档解析器模块"""

from src.parsers.base import ParserFactory, BaseParser, ParsedContent
from src.parsers.markdown import MarkdownParser

# 注册解析器
ParserFactory.register(".md", MarkdownParser())

__all__ = ["BaseParser", "ParsedContent", "ParserFactory"]
