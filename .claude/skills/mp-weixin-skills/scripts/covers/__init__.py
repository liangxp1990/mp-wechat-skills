"""封面生成模块"""

from covers.base import BaseCoverGenerator, CoverResult
from covers.template_maker import TemplateCoverGenerator
from covers.image_search_maker import ImageSearchCoverGenerator
from covers.browser_search_maker import BrowserSearchCoverGenerator

__all__ = ["BaseCoverGenerator", "CoverResult", "TemplateCoverGenerator", "ImageSearchCoverGenerator", "BrowserSearchCoverGenerator"]
