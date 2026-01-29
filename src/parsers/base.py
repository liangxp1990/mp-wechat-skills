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
        """解析文档,返回统一结构"""
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
