"""本地模板封面生成器"""

import logging
from pathlib import Path
from typing import Dict
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
from src.covers.base import BaseCoverGenerator, CoverResult

logger = logging.getLogger(__name__)


class TemplateCoverGenerator(BaseCoverGenerator):
    """使用本地模板生成封面"""

    # 微信封面尺寸: 2.35:1
    DEFAULT_WIDTH = 1080
    DEFAULT_HEIGHT = 460

    def __init__(self, theme_color: str = "#07c160"):
        self.theme_color = theme_color
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

        # 绘制渐变背景
        self._draw_gradient(draw, width, height)

        # 绘制标题
        self._draw_title(draw, title, width, height)

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
            metadata={"template": "gradient", "title": title, "theme_color": self.theme_color},
            needs_upload=True,
        )

    def _draw_gradient(self, draw, width: int, height: int):
        """绘制渐变背景"""
        # 简单渐变效果
        for y in range(height):
            ratio = y / height
            # 从浅色到深色
            r = int(240 - ratio * 30)
            g = int(250 - ratio * 30)
            b = int(255 - ratio * 30)
            draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))

    def _draw_title(self, draw, title: str, width: int, height: int):
        """绘制标题文字"""
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 60)
        except:
            try:
                # 尝试使用其他常见字体
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
            except:
                # 回退到默认字体
                font = ImageFont.load_default()

        # 计算文字位置（居中）
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # 绘制阴影
        draw.text((x + 2, y + 2), title, font=font, fill=(200, 200, 200))

        # 绘制主文字
        draw.text((x, y), title, font=font, fill=(51, 51, 51))
