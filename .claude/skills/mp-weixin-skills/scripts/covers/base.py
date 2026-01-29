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
