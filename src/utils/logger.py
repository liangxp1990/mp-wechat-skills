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
