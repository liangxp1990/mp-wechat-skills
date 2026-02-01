"""样式管理器"""

import logging
from typing import Dict
import re

logger = logging.getLogger(__name__)


class StyleManager:
    """样式管理器 - 将 CSS 转换为内联样式"""

    def __init__(self, theme: Dict = None):
        self.theme = theme or self._default_theme()

    def _default_theme(self) -> Dict:
        return {
            "primary_color": "#07c160",
            "text_color": "#333333",
            "bg_color": "#ffffff",
            "heading_color": "#000000",
            "border_radius": "4px",
            "spacing": "16px",
        }

    def apply_inline_styles(self, html: str) -> str:
        """将 CSS 转换为内联样式"""
        logger.info("[StyleManager] 开始应用内联样式")

        # 处理标题
        html = self._style_headings(html)

        # 处理段落
        html = self._style_paragraphs(html)

        # 处理代码块
        html = self._style_code_blocks(html)

        # 处理引用
        html = self._style_blockquotes(html)

        # 处理表格
        html = self._style_tables(html)

        # 清理空列表项（修复 emoji 数字被误解析为有序列表的问题）
        html = self._cleanup_empty_list_items(html)

        logger.info("[StyleManager] 样式应用完成")
        return html

    def _style_headings(self, html: str) -> str:
        """处理标题样式"""
        color = self.theme["heading_color"]
        primary = self.theme["primary_color"]

        # h1 - 带主题色渐变背景
        # 创建渐变效果：从主题色淡化版本到白色背景
        html = re.sub(
            r"<h1>(.+?)</h1>",
            rf'<h1 style="font-size: 26px; font-weight: bold; color: #ffffff; margin: 20px 0; padding: 20px 24px; background: linear-gradient(135deg, {primary} 0%, {self._lighten_color(primary, 20)} 100%); border-radius: 8px; text-shadow: 0 2px 4px rgba(0,0,0,0.1); box-shadow: 0 4px 12px rgba(0,0,0,0.08);">\1</h1>',
            html,
        )

        # h2
        html = re.sub(
            r"<h2>(.+?)</h2>",
            rf'<h2 style="font-size: 20px; font-weight: bold; color: {color}; margin: 18px 0; padding-left: 12px; border-left: 4px solid {primary};">\1</h2>',
            html,
        )

        return html

    def _lighten_color(self, hex_color: str, percent: int) -> str:
        """将颜色变亮指定的百分比"""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        # 变亮颜色
        r = min(255, int(r + (255 - r) * percent / 100))
        g = min(255, int(g + (255 - g) * percent / 100))
        b = min(255, int(b + (255 - b) * percent / 100))

        return f"#{r:02x}{g:02x}{b:02x}"

    def _style_paragraphs(self, html: str) -> str:
        """处理段落样式"""
        color = self.theme["text_color"]
        spacing = self.theme["spacing"]

        html = re.sub(
            r"<p>(.+?)</p>",
            rf'<p style="color: {color}; line-height: 1.75; margin: {spacing} 0; font-size: 15px; text-align: justify;">\1</p>',
            html,
        )

        return html

    def _style_code_blocks(self, html: str) -> str:
        """处理代码块样式 - 微信公众号移动端友好设计"""
        # 内联代码 - 更适合手机阅读
        html = re.sub(
            r"<code>(.+?)</code>",
            r'<code style="background-color: #f0f0f0; color: #d63384; padding: 3px 6px; border-radius: 4px; font-family: -apple-system, BlinkMacSystemFont, \"SF Mono\", Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace; font-size: 14px;">\1</code>',
            html,
        )

        # 代码块 - 移动端友好（横向滚动，不强制换行）
        # 先处理 <pre><code> 组合
        html = re.sub(
            r"<pre><code",
            '<pre style="background-color: #2d2d2d; color: #f8f8f2; padding: 15px 12px; border-radius: 8px; overflow-x: auto; max-width: 100%; font-family: -apple-system, BlinkMacSystemFont, \"SF Mono\", Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace; font-size: 13px; line-height: 1.6; margin: 16px 0; white-space: pre; word-break: normal; -webkit-overflow-scrolling: touch;"><code style="background-color: transparent; color: inherit; padding: 0; font-size: 13px;"',
            html,
        )
        html = re.sub(
            r"</code></pre>",
            '</code></pre>',
            html,
        )

        # 单独的 <pre> 标签（没有 code）
        html = re.sub(
            r'<pre(?![^>]*style)',
            '<pre style="background-color: #2d2d2d; color: #f8f8f2; padding: 15px 12px; border-radius: 8px; overflow-x: auto; max-width: 100%; font-family: -apple-system, BlinkMacSystemFont, \"SF Mono\", Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace; font-size: 13px; line-height: 1.6; margin: 16px 0; white-space: pre; word-break: normal; -webkit-overflow-scrolling: touch;"',
            html,
        )

        return html

    def _style_blockquotes(self, html: str) -> str:
        """处理引用样式"""
        primary = self.theme["primary_color"]

        html = re.sub(
            r"<blockquote>(.+?)</blockquote>",
            rf'<blockquote style="border-left: 4px solid {primary}; padding-left: 15px; margin: 16px 0; color: #666; background-color: #f9f9f9; padding: 10px 15px;">\1</blockquote>',
            html,
        )

        return html

    def _style_tables(self, html: str) -> str:
        """处理表格样式"""
        primary = self.theme["primary_color"]
        text_color = self.theme["text_color"]

        # 处理 table 标签
        html = re.sub(
            r"<table>",
            rf'<table style="width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px;">',
            html,
        )

        # 处理 th 标签（表头）
        html = re.sub(
            r"<th>",
            rf'<th style="background-color: {primary}; color: #ffffff; padding: 10px; text-align: left; font-weight: bold; border: 1px solid {self._darken_color(primary, 10)};">',
            html,
        )

        # 处理 td 标签（单元格）
        html = re.sub(
            r"<td>",
            rf'<td style="padding: 10px; border: 1px solid #e0e0e0; color: {text_color};">',
            html,
        )

        return html

    def _darken_color(self, hex_color: str, percent: int) -> str:
        """将颜色变暗指定的百分比"""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        # 变暗颜色
        r = max(0, int(r * (100 - percent) / 100))
        g = max(0, int(g * (100 - percent) / 100))
        b = max(0, int(b * (100 - percent) / 100))

        return f"#{r:02x}{g:02x}{b:02x}"

    def _cleanup_empty_list_items(self, html: str) -> str:
        """清理空列表项（修复 emoji 数字被误解析为有序列表的问题）"""
        # 移除空的 li 标签（可能由 emoji 数字产生）
        html = re.sub(r'<li>\s*</li>', '', html)

        # 移除空的 ol 标签（如果里面没有内容）
        html = re.sub(r'<ol>\s*</ol>', '', html)

        return html
