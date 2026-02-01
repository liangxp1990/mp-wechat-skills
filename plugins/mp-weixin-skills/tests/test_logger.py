"""测试日志系统"""

import logging
import tempfile
from pathlib import Path
from utils.logger import setup_logging


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


def test_third_party_log_levels():
    """测试第三方库日志级别设置"""
    setup_logging()
    assert logging.getLogger("requests").level == logging.WARNING
    assert logging.getLogger("urllib3").level == logging.WARNING
    assert logging.getLogger("PIL").level == logging.WARNING

