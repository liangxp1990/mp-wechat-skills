# 微信公众号文章发布工具 - 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 构建一个将 Markdown、Word 或 PDF 文档转换为符合微信公众号排版要求的工具，支持封面生成、素材上传和草稿发布。

**架构:** 单一 CLI 入口，模块化设计。包含文档解析器、内容转换器、封面生成器、微信 API 客户端等核心模块，支持 API 自动模式和手动模式。

**技术栈:** Python 3.10+, markdown-it-py, python-docx, PyMuPDF, Pillow, requests, python-dotenv

---

## Task 1: 项目基础结构

**目标:** 创建项目基础结构、配置文件和依赖管理

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `src/__init__.py`
- Create: `src/config.py`

### Step 1: 创建 pyproject.toml

**文件:** `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mp-weixin-skills"
version = "0.1.0"
description = "微信公众号文章发布工具"
readme = "SKILL.md"
requires-python = ">=3.10"
authors = [
    {name = "Claude AI"}
]
dependencies = [
    "markdown-it-py>=3.0.0",
    "mdit-py-plugins>=0.4.0",
    "python-docx>=1.0.0",
    "PyMuPDF>=1.23.0",
    "Pillow>=10.0.0",
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
    "click>=8.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "mypy>=1.5.0",
]

[project.scripts]
mp-weixin = "src.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.black]
line-length = 100
target-version = ['py310']

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
```

### Step 2: 创建 .env.example

**文件:** `.env.example`

```bash
# 微信公众号配置（使用 API 时必需）
WECHAT_APP_ID=your_app_id_here
WECHAT_APP_SECRET=your_app_secret_here

# 封面生成配置（可选）
COVER_GENERATOR=auto
OPENAI_API_KEY=your_openai_key_here
UNSPLASH_API_KEY=your_unsplash_key_here

# 输出配置
OUTPUT_DIR=./output
TEMP_DIR=./temp

# 样式配置
TEMPLATE_NAME=default
THEME_COLOR=#07c160

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=./output/mp-weixin.log
```

### Step 3: 创建 src/__init__.py

**文件:** `src/__init__.py`

```python
"""微信公众号文章发布工具"""

__version__ = "0.1.0"
```

### Step 4: 创建配置管理模块

**文件:** `src/config.py`

```python
"""配置管理模块"""

import logging
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """应用配置"""

    # 微信公众号配置
    wechat_app_id: str
    wechat_app_secret: str

    # 封面生成配置
    cover_generator: str = "auto"
    openai_api_key: Optional[str] = None
    unsplash_api_key: Optional[str] = None

    # 输出配置
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    temp_dir: Path = field(default_factory=lambda: Path("./temp"))

    # 样式配置
    template_name: str = "default"
    theme_color: str = "#07c160"

    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[Path] = None

    @classmethod
    def from_env(cls, env_file: str = ".env") -> "AppConfig":
        """从环境变量加载配置"""
        logger.info(f"[Config] 从环境文件加载配置: {env_file}")

        load_dotenv(env_file)

        config = cls(
            wechat_app_id=os.getenv("WECHAT_APP_ID", ""),
            wechat_app_secret=os.getenv("WECHAT_APP_SECRET", ""),
            cover_generator=os.getenv("COVER_GENERATOR", "auto"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            unsplash_api_key=os.getenv("UNSPLASH_API_KEY"),
            output_dir=Path(os.getenv("OUTPUT_DIR", "./output")),
            temp_dir=Path(os.getenv("TEMP_DIR", "./temp")),
            template_name=os.getenv("TEMPLATE_NAME", "default"),
            theme_color=os.getenv("THEME_COLOR", "#07c160"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=Path(os.getenv("LOG_FILE")) if os.getenv("LOG_FILE") else None,
        )

        logger.info(f"[Config] 配置加载完成")
        return config

    def has_wechat_api(self) -> bool:
        """是否配置了微信 API"""
        return bool(self.wechat_app_id and self.wechat_app_secret)
```

### Step 5: 提交基础结构

```bash
git add pyproject.toml .env.example src/__init__.py src/config.py
git commit -m "feat: 添加项目基础结构和配置管理"
```

---

## Task 2: 日志系统

**目标:** 实现清晰的日志系统，支持彩色控制台输出和结构化文件日志

**Files:**
- Create: `src/utils/__init__.py`
- Create: `src/utils/logger.py`
- Create: `tests/test_logger.py`

### Step 1: 创建日志工具模块

**文件:** `src/utils/__init__.py`

```python
"""工具模块"""
```

**文件:** `src/utils/logger.py`

```python
"""日志系统"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import json


class ColoredFormatter(logging.Formatter):
    """带颜色的控制台日志格式化器"""

    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
        "RESET": "\033[0m",
    }

    def __init__(self, fmt: str, use_color: bool = True):
        super().__init__(fmt)
        self.use_color = use_color

    def format(self, record):
        if self.use_color:
            levelcolor = self.COLORS.get(record.levelname, self.COLORS["RESET"])
            record.levelname = f"{levelcolor}{record.levelname}{self.COLORS['RESET']}"

        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    console_output: bool = True,
) -> None:
    """设置日志系统"""

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.handlers.clear()

    # 控制台处理器
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_format = "%(asctime)s | %(levelname)-8s | %(name)-12s | %(message)s"
        console_formatter = ColoredFormatter(console_format, use_color=sys.stdout.isatty())
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        root_logger.addHandler(console_handler)

    # 文件处理器
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_format = "%(asctime)s | %(levelname)-8s | %(name)-12s | %(message)s"
        file_formatter = logging.Formatter(file_format)
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)

    # 设置第三方库的日志级别
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    logging.info(f"[Logger] 日志系统初始化完成 - 级别: {log_level}")
```

### Step 2: 编写日志测试

**文件:** `tests/test_logger.py`

```python
"""测试日志系统"""

import logging
import tempfile
from pathlib import Path
from src.utils.logger import setup_logging


def test_setup_logging_console():
    """测试控制台日志设置"""
    setup_logging(log_level="INFO", console_output=True)

    logger = logging.getLogger("test")
    logger.setLevel(logging.INFO)

    # 应该不会抛出异常
    logger.info("测试消息")


def test_setup_logging_with_file():
    """测试文件日志设置"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"

        setup_logging(log_level="DEBUG", log_file=log_file)

        logger = logging.getLogger("test_file")
        logger.info("测试消息到文件")

        # 验证文件被创建
        assert log_file.exists()

        # 验证内容
        content = log_file.read_text(encoding="utf-8")
        assert "测试消息到文件" in content
```

### Step 3: 运行测试

```bash
pytest tests/test_logger.py -v
```

Expected: PASS

### Step 4: 提交日志系统

```bash
git add src/utils/logger.py tests/test_logger.py
git commit -m "feat: 实现日志系统"
```

---

## Task 3: 异常定义

**目标:** 定义所有自定义异常类，提供用户友好的错误信息

**Files:**
- Create: `src/exceptions.py`
- Create: `tests/test_exceptions.py`

### Step 1: 创建异常模块

**文件:** `src/exceptions.py`

```python
"""自定义异常类"""

from typing import Dict, Any


class MpWeixinError(Exception):
    """基础异常类"""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def user_message(self) -> str:
        """返回用户友好的错误信息"""
        return self.message


class ParserError(MpWeixinError):
    """文档解析异常"""
    pass


class UnsupportedFileTypeError(ParserError):
    """不支持的文件类型"""

    def __init__(self, file_path: str, file_type: str):
        super().__init__(
            f"不支持的文件类型: {file_type}",
            {"file_path": file_path, "file_type": file_type},
        )

    def user_message(self) -> str:
        return (
            f"❌ 文件格式不支持\n\n"
            f"支持的格式: Markdown (.md), Word (.docx), PDF (.pdf)\n"
            f"请检查文件后缀名是否正确。"
        )


class FileReadError(ParserError):
    """文件读取异常"""

    def __init__(self, file_path: str, reason: str):
        super().__init__(f"文件读取失败: {file_path}", {"file_path": file_path, "reason": reason})

    def user_message(self) -> str:
        return (
            f"❌ 无法读取文件\n\n"
            f"文件: {self.details['file_path']}\n"
            f"原因: {self.details['reason']}\n\n"
            f"请检查：\n"
            f"1. 文件是否存在\n"
            f"2. 是否有读取权限\n"
            f"3. 文件是否损坏"
        )


class WechatApiError(MpWeixinError):
    """微信公众号 API 异常"""

    ERROR_CODES = {
        40001: "AppSecret 错误",
        40013: "不合法的 AppID",
        42001: "access_token 超时",
        45011: "API 调用太频繁",
    }

    def __init__(self, message: str, errcode: int = None):
        super().__init__(message, {"errcode": errcode, "errmsg": message})
        self.errcode = errcode

    def user_message(self) -> str:
        if self.errcode:
            friendly_msg = self.ERROR_CODES.get(self.errcode, "未知错误")
            return f"❌ 微信公众号 API 错误\n\n错误码: {self.errcode}\n错误信息: {friendly_msg}"
        return f"❌ 微信公众号 API 错误\n\n{self.message}"


class ConversionError(MpWeixinError):
    """内容转换异常"""
    pass
```

### Step 2: 编写异常测试

**文件:** `tests/test_exceptions.py`

```python
"""测试异常类"""

from src.exceptions import UnsupportedFileTypeError, WechatApiError


def test_unsupported_file_type_error():
    """测试不支持的文件类型异常"""
    error = UnsupportedFileTypeError("test.xyz", ".xyz")

    assert error.message == "不支持的文件类型: .xyz"
    assert error.details["file_path"] == "test.xyz"
    assert error.details["file_type"] == ".xyz"
    assert "不支持的文件类型" in error.user_message()


def test_wechat_api_error():
    """测试微信 API 异常"""
    error = WechatApiError("测试错误", errcode=40001)

    assert error.errcode == 40001
    assert "AppSecret 错误" in error.user_message()
```

### Step 3: 运行测试

```bash
pytest tests/test_exceptions.py -v
```

Expected: PASS

### Step 4: 提交异常模块

```bash
git add src/exceptions.py tests/test_exceptions.py
git commit -m "feat: 添加异常定义"
```

---

## Task 4: Markdown 解析器

**目标:** 实现 Markdown 文档解析功能

**Files:**
- Create: `src/parsers/__init__.py`
- Create: `src/parsers/base.py`
- Create: `src/parsers/markdown.py`
- Create: `tests/test_markdown_parser.py`
- Create: `examples/sample.md`

### Step 1: 创建解析器基类

**文件:** `src/parsers/__init__.py`

```python
"""文档解析器模块"""

from src.parsers.base import ParserFactory, BaseParser, ParsedContent

__all__ = ["BaseParser", "ParsedContent", "ParserFactory"]
```

**文件:** `src/parsers/base.py`

```python
"""解析器基类"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


@dataclass
class ParsedContent:
    """解析后的内容结构"""

    title: str
    content: str
    images: List[Path]
    metadata: dict
    toc: Optional[List[dict]] = None

    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.metadata is None:
            self.metadata = {}
        if self.toc is None:
            self.toc = []


class BaseParser(ABC):
    """解析器基类"""

    @abstractmethod
    def parse(self, file_path: Path) -> ParsedContent:
        """解析文档，返回统一结构"""
        pass

    @abstractmethod
    def supports(self, file_path: Path) -> bool:
        """判断是否支持该文件类型"""
        pass


class ParserFactory:
    """解析器工厂"""

    _parsers = {}

    @classmethod
    def register(cls, suffix: str, parser: BaseParser):
        """注册解析器"""
        cls._parsers[suffix] = parser

    @classmethod
    def get_parser(cls, file_path: Path) -> BaseParser:
        """获取解析器"""
        ext = file_path.suffix.lower()
        parser = cls._parsers.get(ext)
        if not parser:
            from src.exceptions import UnsupportedFileTypeError
            raise UnsupportedFileTypeError(str(file_path), ext)
        return parser

    @classmethod
    def supports(cls, file_path: Path) -> bool:
        """判断是否支持该文件类型"""
        return file_path.suffix.lower() in cls._parsers
```

### Step 2: 实现 Markdown 解析器

**文件:** `src/parsers/markdown.py`

```python
"""Markdown 解析器"""

import logging
from pathlib import Path
from typing import List
import re

from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode

from src.parsers.base import BaseParser, ParsedContent

logger = logging.getLogger(__name__)


class MarkdownParser(BaseParser):
    """Markdown 解析器"""

    def __init__(self):
        self.md = MarkdownIt()

    def supports(self, file_path: Path) -> bool:
        """判断是否支持该文件类型"""
        return file_path.suffix.lower() == ".md"

    def parse(self, file_path: Path) -> ParsedContent:
        """解析 Markdown 文档"""
        logger.info(f"[MarkdownParser] 开始解析: {file_path}")

        if not file_path.exists():
            from src.exceptions import FileReadError
            raise FileReadError(str(file_path), "文件不存在")

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            from src.exceptions import FileReadError
            raise FileReadError(str(file_path), str(e))

        # 提取标题（第一个 # 标题）
        title = self._extract_title(content)

        # 转换为 HTML
        html_content = self.md.render(content)

        # 提取图片路径
        images = self._extract_images(file_path, content)

        # 元数据
        metadata = {
            "source_file": str(file_path),
            "author": "",
            "date": "",
        }

        logger.info(f"[MarkdownParser] 解析完成 - 标题: {title}, 图片数: {len(images)}")

        return ParsedContent(
            title=title,
            content=html_content,
            images=images,
            metadata=metadata,
        )

    def _extract_title(self, content: str) -> str:
        """提取标题"""
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        # 如果没有找到标题，使用文件名
        return "未命名文章"

    def _extract_images(self, file_path: Path, content: str) -> List[Path]:
        """提取图片路径"""
        images = []

        # 匹配 ![alt](path) 格式
        pattern = r"!\[.*?\]\((.+?)\)"
        matches = re.findall(pattern, content)

        for match in matches:
            # 处理相对路径
            img_path = Path(match)
            if not img_path.is_absolute():
                img_path = file_path.parent / img_path

            images.append(img_path)

        return images
```

### Step 3: 创建示例文件

**文件:** `examples/sample.md`

```markdown
# 示例文章

这是一篇示例文章，用于测试 Markdown 解析器。

## 功能介绍

- 支持 Markdown 格式
- 自动提取标题
- 识别图片引用

![示例图片](https://example.com/image.jpg)

## 代码示例

```python
print("Hello, WeChat!")
```
```

### Step 4: 编写测试

**文件:** `tests/test_markdown_parser.py`

```python
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
```

### Step 5: 运行测试

```bash
pytest tests/test_markdown_parser.py -v
```

Expected: PASS

### Step 6: 注册解析器

修改 `src/parsers/__init__.py`:

```python
"""文档解析器模块"""

from src.parsers.base import ParserFactory, BaseParser, ParsedContent
from src.parsers.markdown import MarkdownParser

# 注册解析器
ParserFactory.register(".md", MarkdownParser())

__all__ = ["BaseParser", "ParsedContent", "ParserFactory"]
```

### Step 7: 提交 Markdown 解析器

```bash
git add src/parsers/ tests/test_markdown_parser.py examples/sample.md
git commit -m "feat: 实现 Markdown 解析器"
```

---

## Task 5: 内容转换器

**目标:** 实现 HTML 构建器和样式管理

**Files:**
- Create: `src/converters/__init__.py`
- Create: `src/converters/html_builder.py`
- Create: `src/converters/style_manager.py`
- Create: `src/converters/templates/default.html`
- Create: `tests/test_html_builder.py`

### Step 1: 创建样式管理器

**文件:** `src/converters/__init__.py`

```python
"""内容转换模块"""

from src.converters.html_builder import WechatHTMLBuilder
from src.converters.style_manager import StyleManager

__all__ = ["WechatHTMLBuilder", "StyleManager"]
```

**文件:** `src/converters/style_manager.py`

```python
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

        # h1
        html = re.sub(
            r"<h1>(.+?)</h1>",
            rf'<h1 style="font-size: 24px; font-weight: bold; color: {color}; margin: 20px 0; border-bottom: 2px solid {self.theme["primary_color"]}; padding-bottom: 10px;">\1</h1>',
            html,
        )

        # h2
        html = re.sub(
            r"<h2>(.+?)</h2>",
            rf'<h2 style="font-size: 20px; font-weight: bold; color: {color}; margin: 18px 0;">\1</h2>',
            html,
        )

        return html

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
```

### Step 2: 创建 HTML 构建器

**文件:** `src/converters/html_builder.py`

```python
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
```

### Step 3: 创建默认模板

**文件:** `src/converters/templates/default.html`

```html
<!-- 默认样式模板 -->
<section style="max-width: 677px; margin: 0 auto; padding: 20px;">
  {{content}}
</section>
```

### Step 4: 编写测试

**文件:** `tests/test_html_builder.py`

```python
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
```

### Step 5: 运行测试

```bash
pytest tests/test_html_builder.py -v
```

Expected: PASS

### Step 6: 提交内容转换器

```bash
git add src/converters/ tests/test_html_builder.py
git commit -m "feat: 实现内容转换器"
```

---

## Task 6: 封面生成器（本地模板）

**目标:** 实现本地模板封面生成功能

**Files:**
- Create: `src/covers/__init__.py`
- Create: `src/covers/base.py`
- Create: `src/covers/template_maker.py`
- Create: `tests/test_template_maker.py`

### Step 1: 创建封面生成器基类

**文件:** `src/covers/__init__.py`

```python
"""封面生成模块"""

from src.covers.base import BaseCoverGenerator, CoverResult
from src.covers.template_maker import TemplateCoverGenerator

__all__ = ["BaseCoverGenerator", "CoverResult", "TemplateCoverGenerator"]
```

**文件:** `src/covers/base.py`

```python
"""封面生成器基类"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass
class CoverResult:
    """封面生成结果"""

    image_path: Path
    source_type: str
    metadata: Dict
    needs_upload: bool = True


class BaseCoverGenerator(ABC):
    """封面生成器基类"""

    @abstractmethod
    def generate(self, title: str, content: str, **kwargs) -> CoverResult:
        """根据标题和内容生成封面"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查该生成器是否可用"""
        pass
```

### Step 2: 实现本地模板封面生成器

**文件:** `src/covers/template_maker.py`

```python
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
            metadata={"template": "gradient", "title": title},
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
```

### Step 3: 编写测试

**文件:** `tests/test_template_maker.py`

```python
"""测试模板封面生成器"""

from pathlib import Path
from src.covers.template_maker import TemplateCoverGenerator


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
```

### Step 4: 运行测试

```bash
pytest tests/test_template_maker.py -v
```

Expected: PASS

### Step 5: 提交封面生成器

```bash
git add src/covers/ tests/test_template_maker.py
git commit -m "feat: 实现本地模板封面生成器"
```

---

## Task 7: 微信公众号 API 客户端

**目标:** 实现微信公众号 API 客户端

**Files:**
- Create: `src/wechat/__init__.py`
- Create: `src/wechat/api_client.py`
- Create: `tests/test_api_client.py`

### Step 1: 创建 API 客户端

**文件:** `src/wechat/__init__.py`

```python
"""微信公众号 API 模块"""

from src.wechat.api_client import WechatApiClient, WechatConfig

__all__ = ["WechatApiClient", "WechatConfig"]
```

**文件:** `src/wechat/api_client.py`

```python
"""微信公众号 API 客户端"""

import logging
from typing import Dict
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.exceptions import WechatApiError

logger = logging.getLogger(__name__)


@dataclass
class WechatConfig:
    """微信公众号配置"""

    app_id: str
    app_secret: str
    base_url: str = "https://api.weixin.qq.com"
    timeout: int = 30


class WechatApiClient:
    """微信公众号 API 客户端"""

    ENDPOINTS = {
        "token": "/cgi-bin/token",
        "upload_media": "/cgi-bin/material/add_material",
        "upload_draft": "/cgi-bin/draft/add",
        "update_draft": "/cgi-bin/draft/update",
    }

    def __init__(self, config: WechatConfig):
        logger.info(f"[WechatAPI] 初始化客户端 - AppID: {config.app_id[:8]}***")
        self.config = config
        self._access_token: str = ""
        self._session = self._create_session()

    def _create_session(self) -> requests.Session:
        """创建 HTTP 会话"""
        logger.debug("[WechatAPI] 创建 HTTP 会话")
        session = requests.Session()

        retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)

        return session

    def get_access_token(self) -> str:
        """获取访问令牌"""
        if self._access_token:
            logger.debug("[WechatAPI] 使用缓存的 access_token")
            return self._access_token

        logger.info("[WechatAPI] 请求新的 access_token")
        url = f"{self.config.base_url}{self.ENDPOINTS['token']}"
        params = {
            "grant_type": "client_credential",
            "appid": self.config.app_id,
            "secret": self.config.app_secret,
        }

        try:
            response = self._session.get(url, params=params, timeout=self.config.timeout)
            response.raise_for_status()

            data = response.json()

            if "access_token" not in data:
                error_msg = f"获取 access_token 失败: {data.get('errmsg', '未知错误')}"
                logger.error(f"[WechatAPI] {error_msg}")
                raise WechatApiError(error_msg, data.get("errcode"))

            self._access_token = data["access_token"]
            logger.info(f"[WechatAPI] access_token 获取成功")
            return self._access_token

        except requests.RequestException as e:
            logger.error(f"[WechatAPI] 网络请求失败: {e}")
            raise WechatApiError(f"网络请求失败: {e}")

    def upload_media(self, file_path: str, media_type: str = "thumb") -> Dict:
        """上传永久素材"""
        logger.info(f"[WechatAPI] 开始上传素材 - 类型: {media_type}")

        url = f"{self.config.base_url}{self.ENDPOINTS['upload_media']}"
        params = {
            "access_token": self.get_access_token(),
            "type": media_type,
        }

        try:
            with open(file_path, "rb") as f:
                files = {"media": f}
                response = self._session.post(url, params=params, files=files, timeout=self.config.timeout)

            response.raise_for_status()
            data = response.json()

            if "media_id" not in data:
                error_msg = f"上传素材失败: {data.get('errmsg', '未知错误')}"
                logger.error(f"[WechatAPI] {error_msg}")
                raise WechatApiError(error_msg, data.get("errcode"))

            logger.info(f"[WechatAPI] 素材上传成功")
            return data

        except (requests.RequestException, IOError) as e:
            logger.error(f"[WechatAPI] 上传失败: {e}")
            raise WechatApiError(f"上传失败: {e}")

    def upload_draft(self, articles: list) -> Dict:
        """上传草稿"""
        logger.info(f"[WechatAPI] 开始上传草稿")

        url = f"{self.config.base_url}{self.ENDPOINTS['upload_draft']}"
        params = {"access_token": self.get_access_token()}
        payload = {"articles": articles}

        try:
            response = self._session.post(url, params=params, json=payload, timeout=self.config.timeout)
            response.raise_for_status()

            data = response.json()

            if data.get("errcode") != 0:
                error_msg = f"上传草稿失败: {data.get('errmsg', '未知错误')}"
                logger.error(f"[WechatAPI] {error_msg}")
                raise WechatApiError(error_msg, data.get("errcode"))

            logger.info(f"[WechatAPI] 草稿上传成功")
            return data

        except requests.RequestException as e:
            logger.error(f"[WechatAPI] 草稿上传失败: {e}")
            raise WechatApiError(f"草稿上传失败: {e}")

    def update_draft(self, media_id: str, index: int, article: Dict) -> Dict:
        """更新草稿"""
        logger.info(f"[WechatAPI] 开始更新草稿 - media_id: {media_id}")

        url = f"{self.config.base_url}{self.ENDPOINTS['update_draft']}"
        params = {"access_token": self.get_access_token()}

        payload = {"media_id": media_id, "index": index, "articles": article}

        try:
            response = self._session.post(url, params=params, json=payload, timeout=self.config.timeout)
            response.raise_for_status()

            data = response.json()

            if data.get("errcode") != 0:
                error_msg = f"更新草稿失败: {data.get('errmsg', '未知错误')}"
                logger.error(f"[WechatAPI] {error_msg}")
                raise WechatApiError(error_msg, data.get("errcode"))

            logger.info(f"[WechatAPI] 草稿更新成功")
            return data

        except requests.RequestException as e:
            logger.error(f"[WechatAPI] 更新失败: {e}")
            raise WechatApiError(f"更新失败: {e}")
```

### Step 2: 编写测试

**文件:** `tests/test_api_client.py`

```python
"""测试微信 API 客户端"""

from src.wechat.api_client import WechatApiClient, WechatConfig
import pytest


def test_wechat_config():
    """测试配置"""
    config = WechatConfig(app_id="test_id", app_secret="test_secret")

    assert config.app_id == "test_id"
    assert config.app_secret == "test_secret"


def test_wechat_client_init():
    """测试客户端初始化"""
    config = WechatConfig(app_id="test_id", app_secret="test_secret")
    client = WechatApiClient(config)

    assert client.config == config
    assert client._session is not None
```

### Step 3: 运行测试

```bash
pytest tests/test_api_client.py -v
```

Expected: PASS

### Step 4: 提交 API 客户端

```bash
git add src/wechat/ tests/test_api_client.py
git commit -m "feat: 实现微信公众号 API 客户端"
```

---

## Task 8: CLI 主程序

**目标:** 实现命令行接口

**Files:**
- Create: `src/cli.py`
- Modify: `pyproject.toml` (添加 CLI 入口)

### Step 1: 创建 CLI 主程序

**文件:** `src/cli.py`

```python
"""命令行接口"""

import sys
import logging
from pathlib import Path
import click

from src.config import AppConfig
from src.utils.logger import setup_logging
from src.parsers import ParserFactory
from src.converters import WechatHTMLBuilder
from src.covers.template_maker import TemplateCoverGenerator
from src.wechat import WechatApiClient, WechatConfig
from src.exceptions import MpWeixinError

logger = logging.getLogger(__name__)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="详细输出")
@click.option("--env", default=".env", help="环境文件路径")
def main(verbose: bool, env: str):
    """微信公众号文章发布工具"""
    pass


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--no-api", is_flag=True, help="不使用 API")
@click.option("--template", default="default", help="样式模板")
@click.option("--cover-type", default="auto", help="封面生成方式")
def publish(file: str, no_api: bool, template: str, cover_type: str):
    """发布文章到微信公众号"""
    try:
        # 加载配置
        config = AppConfig.from_env()
        log_level = "DEBUG" if click.ctx.verbose else config.log_level
        setup_logging(log_level, config.log_file)

        logger.info("[CLI] 微信公众号文章发布工具启动")

        # 解析文档
        file_path = Path(file)
        parser = ParserFactory.get_parser(file_path)
        parsed = parser.parse(file_path)

        logger.info(f"[CLI] 文章标题: {parsed.title}")

        # 转换内容
        builder = WechatHTMLBuilder(template)
        html_content = builder.build(parsed)

        # 生成封面
        cover_gen = TemplateCoverGenerator(config.theme_color)
        cover_result = cover_gen.generate(parsed.title, "")

        if no_api or not config.has_wechat_api():
            # 手动模式
            logger.info("[CLI] 运行在手动模式")

            output_dir = config.output_dir
            output_dir.mkdir(parents=True, exist_ok=True)

            # 保存 HTML
            html_file = output_dir / f"{file_path.stem}.html"
            html_file.write_text(html_content, encoding="utf-8")

            click.echo(f"✅ 转换完成!")
            click.echo(f"   HTML: {html_file}")
            click.echo(f"   封面: {cover_result.image_path}")
            click.echo(f"\n请手动上传到微信公众号后台")

        else:
            # API 模式
            logger.info("[CLI] 运行在 API 模式")

            api_config = WechatConfig(config.wechat_app_id, config.wechat_app_secret)
            api_client = WechatApiClient(api_config)

            # 上传封面
            cover_data = api_client.upload_media(str(cover_result.image_path), "thumb")

            # 构建文章数据
            article = {
                "title": parsed.title,
                "content": html_content,
                "thumb_media_id": cover_data["media_id"],
                "need_open_comment": 0,
                "only_fans_can_comment": 0,
            }

            # 上传草稿
            result = api_client.upload_draft([article])

            click.echo(f"✅ 文章发布成功!")
            click.echo(f"   Media ID: {result['media_id']}")
            click.echo(f"   请在微信公众号后台查看草稿")

    except MpWeixinError as e:
        click.echo(e.user_message())
        sys.exit(1)
    except Exception as e:
        logger.exception(f"[CLI] 未处理的异常")
        click.echo(f"❌ 发生错误: {e}")
        sys.exit(1)


@main.command()
def version():
    """显示版本信息"""
    from src import __version__
    click.echo(f"mp-weixin-skills version {__version__}")


if __name__ == "__main__":
    main()
```

### Step 2: 更新 pyproject.toml

修改 `pyproject.toml`，确保 click 在依赖中：

```toml
dependencies = [
    "markdown-it-py>=3.0.0",
    "mdit-py-plugins>=0.4.0",
    "python-docx>=1.0.0",
    "PyMuPDF>=1.23.0",
    "Pillow>=10.0.0",
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
    "click>=8.1.0",  # 确保有这一行
]
```

### Step 3: 测试 CLI

```bash
# 安装项目
pip install -e .

# 测试帮助
mp-weixin --help

# 测试发布（手动模式）
mp-weixin publish examples/sample.md --no-api
```

Expected: 成功生成 HTML 和封面

### Step 4: 提交 CLI

```bash
git add src/cli.py pyproject.toml
git commit -m "feat: 实现 CLI 主程序"
```

---

## Task 9: 完善和集成测试

**目标:** 完善功能，编写集成测试

**Files:**
- Create: `tests/test_integration.py`
- Modify: `README.md`

### Step 1: 编写集成测试

**文件:** `tests/test_integration.py`

```python
"""集成测试"""

from pathlib import Path
from src.parsers import ParserFactory
from src.converters import WechatHTMLBuilder
from src.covers.template_maker import TemplateCoverGenerator


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
```

### Step 2: 运行所有测试

```bash
pytest tests/ -v --cov=src
```

Expected: 所有测试通过，覆盖率 > 70%

### Step 3: 创建 README

**文件:** `README.md`

```markdown
# 微信公众号文章发布工具

一个强大的微信公众号文章发布工具。

## 功能特点

- 支持 Markdown、Word、PDF 格式
- 自动生成封面图
- 上传素材到微信素材库
- 推送到草稿箱

## 安装

```bash
pip install -e .
```

## 使用

```bash
# 配置环境变量
cp .env.example .env
# 编辑 .env 填入微信配置

# 发布文章
mp-weixin publish article.md

# 仅转换（不上传）
mp-weixin publish article.md --no-api
```

## 开发

```bash
# 运行测试
pytest tests/ -v

# 代码格式化
black src/
```
```

### Step 4: 提交测试和文档

```bash
git add tests/test_integration.py README.md
git commit -m "feat: 添加集成测试和文档"
```

---

## 总结

实现计划已完成。所有任务按照 TDD 原则设计，每个任务包含：
1. 编写测试
2. 运行测试验证失败
3. 实现代码
4. 运行测试验证通过
5. 提交代码

**下一步:** 使用 `superpowers:executing-plans` 或 `superpowers:subagent-driven-development` 开始实施。
