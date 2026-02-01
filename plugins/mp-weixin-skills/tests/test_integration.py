"""集成测试"""

from pathlib import Path
from parsers import ParserFactory
from converters import WechatHTMLBuilder
from covers.template_maker import TemplateCoverGenerator


def test_full_conversion_flow():
    """测试完整的转换流程"""
    # 解析
    parser = ParserFactory.get_parser(Path("examples/sample.md"))
    parsed = parser.parse(Path("examples/sample.md"))

    assert parsed.title == "示例文章"

    # 转换
    builder = WechatHTMLBuilder()
    html = builder.build(parsed)

    assert "<section" in html
    assert "示例文章" in html

    # 生成封面
    cover_gen = TemplateCoverGenerator()
    cover = cover_gen.generate(parsed.title, "")

    assert cover.image_path.exists()
    assert cover.source_type == "template"


def test_markdown_to_html_integration():
    """测试 Markdown 到 HTML 的完整转换"""
    # 解析 Markdown
    parser = ParserFactory.get_parser(Path("examples/sample.md"))
    parsed = parser.parse(Path("examples/sample.md"))

    # 验证解析结果
    assert parsed.title == "示例文章"
    assert "<h1" in parsed.content
    assert "<h2" in parsed.content
    assert "<p" in parsed.content
    assert parsed.metadata["source_file"] == "examples/sample.md"

    # 转换为微信公众号 HTML
    builder = WechatHTMLBuilder()
    html = builder.build(parsed)

    # 验证 HTML 结构
    assert "<section" in html
    assert "max-width: 677px" in html
    assert "示例文章" in html
    assert "功能介绍" in html
    assert "代码示例" in html

    # 验证样式应用
    assert "font-size: 24px" in html  # h1 样式
    assert "line-height: 1.8" in html  # 段落样式


def test_cover_generation_integration():
    """测试封面生成的完整流程"""
    # 创建封面生成器
    cover_gen = TemplateCoverGenerator()

    # 生成封面
    result = cover_gen.generate("集成测试标题", "测试内容")

    # 验证生成结果
    assert result.image_path.exists()
    assert result.source_type == "template"
    assert result.needs_upload is True
    assert result.metadata["title"] == "集成测试标题"

    # 验证文件可读
    assert result.image_path.stat().st_size > 0


def test_parser_factory_integration():
    """测试解析器工厂的集成"""
    # 测试支持的文件类型
    md_path = Path("examples/sample.md")
    assert ParserFactory.supports(md_path) is True

    txt_path = Path("test.txt")
    assert ParserFactory.supports(txt_path) is False

    # 测试获取解析器
    parser = ParserFactory.get_parser(md_path)
    assert parser is not None
    assert hasattr(parser, 'parse')
    assert hasattr(parser, 'supports')


def test_style_manager_with_builder():
    """测试样式管理器与构建器的集成"""
    from parsers.base import ParsedContent
    from converters.style_manager import StyleManager

    # 创建测试内容
    parsed = ParsedContent(
        title="样式测试",
        content="<h1>主标题</h1><h2>副标题</h2><p>段落内容</p><blockquote>引用内容</blockquote>",
        images=[],
        metadata={},
    )

    # 使用构建器转换
    builder = WechatHTMLBuilder()
    html = builder.build(parsed)

    # 验证各种样式都被正确应用
    assert "font-size: 24px" in html  # h1
    assert "font-size: 20px" in html  # h2
    assert "line-height: 1.8" in html  # p
    assert "border-left: 4px solid" in html  # blockquote
    assert "max-width: 677px" in html  # container


def test_error_handling_integration():
    """测试错误处理的集成"""
    from exceptions import UnsupportedFileTypeError

    # 测试不支持的文件类型
    try:
        parser = ParserFactory.get_parser(Path("test.xyz"))
        assert False, "应该抛出 UnsupportedFileTypeError"
    except UnsupportedFileTypeError as e:
        assert ".xyz" in e.message
        assert "文件格式不支持" in e.user_message()


def test_complex_document_integration():
    """测试复杂文档的完整处理流程"""
    # 解析文档
    parser = ParserFactory.get_parser(Path("examples/sample.md"))
    parsed = parser.parse(Path("examples/sample.md"))

    # 转换内容
    builder = WechatHTMLBuilder()
    html = builder.build(parsed)

    # 生成封面
    cover_gen = TemplateCoverGenerator()
    cover = cover_gen.generate(parsed.title, parsed.content)

    # 验证整个流程
    assert parsed.title == "示例文章"
    assert len(html) > 0
    assert cover.image_path.exists()

    # 验证 HTML 包含预期内容
    assert "功能介绍" in html
    assert "代码示例" in html
