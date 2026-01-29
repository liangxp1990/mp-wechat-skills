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
            rf'<p style="color: {color}; line-height: 1.8; margin: {spacing} 0; font-size: 16px;">\1</p>',
            html,
        )

        return html

    def _style_code_blocks(self, html: str) -> str:
        """处理代码块样式"""
        # 内联代码
        html = re.sub(
            r"<code>(.+?)</code>",
            r'<code style="background-color: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace; color: #e74c3c;">\1</code>',
            html,
        )

        # 代码块
        html = re.sub(
            r"<pre>(.+?)</pre>",
            r'<pre style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; overflow-x: auto; font-family: monospace; font-size: 14px; line-height: 1.5;">\1</pre>',
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
