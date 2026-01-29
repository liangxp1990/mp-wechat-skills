"""本地模板封面生成器"""

import logging
import os
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
from src.covers.base import BaseCoverGenerator, CoverResult

logger = logging.getLogger(__name__)


class TemplateCoverGenerator(BaseCoverGenerator):
    """使用本地模板生成封面"""

    # 微信封面尺寸: 2.35:1
    DEFAULT_WIDTH = 1080
    DEFAULT_HEIGHT = 460

    # 字体路径列表（按优先级排序）
    FONT_PATHS = [
        "/System/Library/Fonts/STHeiti Medium.ttc",  # 华文黑体中号
        "/System/Library/Fonts/STHeiti Light.ttc",   # 华文黑体细号
        "/System/Library/Fonts/Songti.ttc",          # 宋体
        "/System/Library/Fonts/PingFang.ttc",        # 苹方（如果存在）
        "/System/Library/Fonts/Supplemental/NotoSansCJK-Regular.ttc",  # Noto Sans CJK（如果存在）
    ]

    def __init__(self, theme_color: str = "#07c160"):
        self.theme_color = theme_color
        # 将十六进制颜色转换为 RGB
        self.theme_rgb = self._hex_to_rgb(theme_color)
        logger.info(f"[TemplateCover] 初始化 - 主题色: {theme_color}")

    def is_available(self) -> bool:
        """本地模板始终可用"""
        return True

    def generate(
        self, title: str, content: str, **kwargs
    ) -> CoverResult:
        """生成封面"""
        logger.info(f"[TemplateCover] 开始生成封面 - 标题: {title}")

        # 创建图片
        width = kwargs.get("width", self.DEFAULT_WIDTH)
        height = kwargs.get("height", self.DEFAULT_HEIGHT)

        img = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(img)

        # 绘制现代化设计背景
        self._draw_modern_background(draw, width, height)

        # 绘制装饰元素
        self._draw_decorations(draw, width, height)

        # 绘制标题（支持中文）
        self._draw_title(draw, title, width, height)

        # 绘制副标题（如果有）
        subtitle = kwargs.get("subtitle", "")
        if subtitle:
            self._draw_subtitle(draw, subtitle, width, height)

        # 保存图片
        output_dir = Path("./temp")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cover_{timestamp}.jpg"
        file_path = output_dir / filename

        img.save(file_path, "JPEG", quality=95)
        logger.info(f"[TemplateCover] 封面已保存: {file_path}")

        return CoverResult(
            image_path=file_path,
            source_type="template",
            metadata={"template": "modern", "title": title, "theme_color": self.theme_color},
            needs_upload=True,
        )

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """将十六进制颜色转换为 RGB 元组"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """获取支持中文的字体"""
        # 尝试使用系统字体
        for font_path in self.FONT_PATHS:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except Exception as e:
                    logger.debug(f"[TemplateCover] 无法加载字体 {font_path}: {e}")
                    continue

        # 如果所有字体都失败，使用默认字体
        logger.warning("[TemplateCover] 无法加载中文字体，使用默认字体")
        return ImageFont.load_default()

    def _draw_modern_background(self, draw, width: int, height: int):
        """绘制现代化背景"""
        # 创建渐变背景
        for y in range(height):
            ratio = y / height
            # 使用主题色创建柔和的渐变
            r = int(255 - ratio * (255 - self.theme_rgb[0]) * 0.3)
            g = int(255 - ratio * (255 - self.theme_rgb[1]) * 0.3)
            b = int(255 - ratio * (255 - self.theme_rgb[2]) * 0.3)
            draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))

        # 在右侧添加主题色装饰条
        bar_width = 8
        for x in range(width - bar_width, width):
            ratio = (x - (width - bar_width)) / bar_width
            r = int(self.theme_rgb[0] * (1 - ratio * 0.3))
            g = int(self.theme_rgb[1] * (1 - ratio * 0.3))
            b = int(self.theme_rgb[2] * (1 - ratio * 0.3))
            draw.rectangle([(x, 0), (x + 1, height)], fill=(r, g, b))

        # 在左上角添加几何图形装饰
        self._draw_geometric_shape(draw, 40, 40, 80, self.theme_rgb)

    def _draw_geometric_shape(self, draw, x: int, y: int, size: int, color: Tuple[int, int, int]):
        """绘制几何图形装饰"""
        # 绘制半圆形
        for i in range(size):
            for j in range(size):
                if (i - size//2)**2 + (j - size//2)**2 <= (size//2)**2:
                    # 创建半透明效果
                    alpha = int(100 * (1 - (i + j) / (size * 1.5)))
                    if alpha > 0:
                        r, g, b = color
                        # 简单的半透明模拟
                        draw.point((x + i, y + j), fill=(min(255, r + 50), min(255, g + 50), min(255, b + 50)))

    def _draw_decorations(self, draw, width: int, height: int):
        """绘制装饰元素"""
        # 底部装饰线
        line_y = height - 60
        draw.rectangle([(40, line_y), (width - 120, line_y + 3)], fill=self.theme_rgb)

        # 添加小圆点装饰
        dot_y = line_y - 20
        for i in range(5):
            x = 60 + i * 30
            draw.ellipse([(x, dot_y), (x + 8, dot_y + 8)], fill=self.theme_rgb)

    def _draw_title(self, draw, title: str, width: int, height: int):
        """绘制标题文字（支持中文）"""
        # 获取中文字体
        font = self._get_font(56, bold=True)

        # 如果标题太长，进行截断
        max_chars = 20
        if len(title) > max_chars:
            title = title[:max_chars-2] + "..."
            logger.info(f"[TemplateCover] 标题过长，已截断: {title}")

        # 计算文字位置（居中偏上）
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (width - text_width) // 2
        y = height // 2 - text_height // 2 - 20

        # 绘制阴影（增加立体感）
        shadow_offset = 3
        draw.text(
            (x + shadow_offset, y + shadow_offset),
            title,
            font=font,
            fill=(180, 180, 180)
        )

        # 绘制主文字
        draw.text((x, y), title, font=font, fill=(33, 33, 33))

    def _draw_subtitle(self, draw, subtitle: str, width: int, height: int):
        """绘制副标题"""
        # 使用较小的字体
        font = self._get_font(32)

        # 计算文字位置
        bbox = draw.textbbox((0, 0), subtitle, font=font)
        text_width = bbox[2] - bbox[0]

        x = (width - text_width) // 2
        y = height // 2 + 40

        # 绘制副标题
        draw.text((x, y), subtitle, font=font, fill=(102, 102, 102))
