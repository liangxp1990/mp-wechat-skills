"""日志系统"""

import logging
import sys
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """带颜色的控制台日志格式化器。

    为不同日志级别添加 ANSI 颜色代码,使控制台输出更易读。
    仅在输出到终端时启用颜色,重定向到文件时自动禁用。

    Attributes:
        COLORS: 日志级别到 ANSI 颜色代码的映射
        use_color: 是否启用彩色输出
    """

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
    """设置应用程序的日志系统。

    配置根日志记录器,支持控制台彩色输出和文件日志记录。
    会清除所有已存在的处理器,并设置第三方库的日志级别。

    Args:
        log_level: 日志级别,如 "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
        log_file: 日志文件路径,如果为 None 则不记录到文件
        console_output: 是否输出到控制台,默认为 True

    Returns:
        None
    """
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
