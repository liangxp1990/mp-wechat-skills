"""测试 HTML 构建器"""

from src.parsers.base import ParsedContent
from src.converters.html_builder import WechatHTMLBuilder
from src.converters.style_manager import StyleManager
from pathlib import Path


def test_style_manager():
    """测试样式管理器"""
    manager = StyleManager()

    html = "<h1>标题</h1><p>段落</p>"
    result = manager.apply_inline_styles(html)

    assert "font-size: 24px" in result
    assert "line-height: 1.8" in result


def test_html_builder():
    """测试 HTML 构建器"""
    builder = WechatHTMLBuilder()

    parsed = ParsedContent(
        title="测试标题",
        content="<h1>标题</h1><p>内容</p>",
        images=[],
        metadata={},
    )

    result = builder.build(parsed)

    assert "<section" in result
    assert "标题" in result
    assert "内容" in result


def test_style_manager_headings():
    """测试标题样式"""
    manager = StyleManager()

    html = "<h1>一级标题</h1><h2>二级标题</h2>"
    result = manager.apply_inline_styles(html)

    assert "font-size: 24px" in result
    assert "font-size: 20px" in result
    assert "font-weight: bold" in result


def test_style_manager_code_blocks():
    """测试代码块样式"""
    manager = StyleManager()

    html = "<code>内联代码</code><pre>代码块</pre>"
    result = manager.apply_inline_styles(html)

    assert "background-color: #f5f5f5" in result
    assert "font-family: monospace" in result


def test_style_manager_blockquotes():
    """测试引用样式"""
    manager = StyleManager()

    html = "<blockquote>引用内容</blockquote>"
    result = manager.apply_inline_styles(html)

    assert "border-left: 4px solid" in result
    assert "padding-left: 15px" in result


def test_html_builder_with_complex_content():
    """测试复杂内容的 HTML 构建"""
    builder = WechatHTMLBuilder()

    parsed = ParsedContent(
        title="复杂文章",
        content="<h1>标题</h1><p>段落1</p><p>段落2</p><blockquote>引用</blockquote>",
        images=[],
        metadata={},
    )

    result = builder.build(parsed)

    assert "<section" in result
    assert "max-width: 677px" in result
    assert "标题" in result
    assert "段落1" in result
    assert "段落2" in result
    assert "引用" in result
