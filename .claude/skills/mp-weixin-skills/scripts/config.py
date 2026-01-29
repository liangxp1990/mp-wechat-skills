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
