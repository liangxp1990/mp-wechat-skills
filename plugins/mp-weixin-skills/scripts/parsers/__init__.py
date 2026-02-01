"""文档解析器模块"""

from parsers.base import ParserFactory, BaseParser, ParsedContent
from parsers.markdown import MarkdownParser
from parsers.word import WordParser
from parsers.pdf import PDFParser

# 注册解析器
ParserFactory.register(".md", MarkdownParser())
ParserFactory.register(".docx", WordParser())
ParserFactory.register(".doc", WordParser())
ParserFactory.register(".pdf", PDFParser())

__all__ = ["BaseParser", "ParsedContent", "ParserFactory"]
