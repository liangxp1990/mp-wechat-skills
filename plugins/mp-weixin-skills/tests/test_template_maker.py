"""测试模板封面生成器"""

from pathlib import Path
from covers.template_maker import TemplateCoverGenerator


def test_template_cover_generator_available():
    """测试生成器可用性"""
    generator = TemplateCoverGenerator()

    assert generator.is_available() == True


def test_template_cover_generator_generate():
    """测试封面生成"""
    generator = TemplateCoverGenerator()

    result = generator.generate("测试标题", "测试内容")

    assert result.image_path.exists()
    assert result.source_type == "template"
    assert result.needs_upload == True
    assert result.metadata["title"] == "测试标题"


def test_template_cover_generator_custom_size():
    """测试自定义尺寸"""
    generator = TemplateCoverGenerator()

    result = generator.generate("测试", "内容", width=800, height=400)

    assert result.image_path.exists()

    # 验证图片尺寸
    from PIL import Image
    img = Image.open(result.image_path)
    assert img.width == 800
    assert img.height == 400


def test_template_cover_generator_theme_color():
    """测试自定义主题色"""
    generator = TemplateCoverGenerator(theme_color="#ff0000")

    result = generator.generate("测试", "内容")

    assert result.image_path.exists()
    assert result.metadata.get("theme_color") == "#ff0000"
