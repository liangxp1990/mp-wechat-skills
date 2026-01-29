"""HTML 构建器"""

import logging
from src.parsers.base import ParsedContent
from src.converters.style_manager import StyleManager

logger = logging.getLogger(__name__)


class WechatHTMLBuilder:
    """微信公众号 HTML 构建器"""

    def __init__(self, template_name: str = "default"):
        self.template_name = template_name
        self.style_manager = StyleManager()
        logger.info(f"[HTMLBuilder] 初始化构建器 - 模板: {template_name}")

    def build(self, parsed: ParsedContent) -> str:
        """构建微信公众号 HTML 内容"""
        logger.info("[HTMLBuilder] 开始构建 HTML")

        # 应用内联样式
        html = self.style_manager.apply_inline_styles(parsed.content)

        # 包装在容器中
        wrapped_html = self._wrap_content(html)

        logger.info("[HTMLBuilder] HTML 构建完成")
        return wrapped_html

    def _wrap_content(self, content: str) -> str:
        """包装内容"""
        return f'<section style="max-width: 677px; margin: 0 auto; padding: 20px;">{content}</section>'
