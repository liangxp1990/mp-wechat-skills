"""测试 Markdown 解析器"""

from pathlib import Path
from src.parsers.markdown import MarkdownParser
from src.parsers.base import ParsedContent


def test_markdown_parser_supports():
    """测试文件类型判断"""
    parser = MarkdownParser()

    assert parser.supports(Path("test.md")) == True
    assert parser.supports(Path("test.txt")) == False


def test_markdown_parser_parse():
    """测试解析功能"""
    parser = MarkdownParser()
    result = parser.parse(Path("examples/sample.md"))

    assert isinstance(result, ParsedContent)
    assert result.title == "示例文章"
    assert "<h1" in result.content
    assert result.metadata["source_file"] == "examples/sample.md"
