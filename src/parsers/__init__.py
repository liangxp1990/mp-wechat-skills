"""文档解析器模块"""

from src.parsers.base import ParserFactory, BaseParser, ParsedContent
from src.parsers.markdown import MarkdownParser
from src.parsers.word import WordParser
from src.parsers.pdf import PDFParser

# 注册解析器
ParserFactory.register(".md", MarkdownParser())
ParserFactory.register(".docx", WordParser())
ParserFactory.register(".doc", WordParser())
ParserFactory.register(".pdf", PDFParser())

__all__ = ["BaseParser", "ParsedContent", "ParserFactory"]
