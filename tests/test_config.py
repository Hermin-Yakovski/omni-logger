# tests/test_config.py
import logging
from pathlib import Path

import pytest

from omni_logger.config import (
    LogConfig,
    ConsoleHandlerConfig,
    FileHandlerConfig,
    DingtalkHandlerConfig,
)


def test_console_handler_config_defaults():
    config = ConsoleHandlerConfig()
    assert config.level == "INFO"
    assert config.fmt == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    assert config.datefmt == "%Y-%m-%d %H:%M:%S"


def test_console_handler_config_custom():
    config = ConsoleHandlerConfig(level="DEBUG", fmt="%(message)s")
    assert config.level == "DEBUG"
    assert config.fmt == "%(message)s"


def test_file_handler_config_defaults():
    config = FileHandlerConfig()
    assert config.level == "INFO"
    assert config.log_dir == Path("./logs")
    assert config.max_bytes == 10 * 1024 * 1024
    assert config.backup_count == 5


def test_file_handler_config_custom():
    config = FileHandlerConfig(
        log_dir=Path("/var/log"),
        max_bytes=50_000_000,
        backup_count=10
    )
    assert config.log_dir == Path("/var/log")
    assert config.max_bytes == 50_000_000
    assert config.backup_count == 10


def test_dingtalk_handler_config_defaults():
    config = DingtalkHandlerConfig()
    assert config.level == "ERROR"
    assert config.min_level == logging.ERROR


def test_log_config_defaults():
    config = LogConfig()
    assert config.handlers == ["console"]
    assert isinstance(config.console, ConsoleHandlerConfig)
    assert isinstance(config.file, FileHandlerConfig)
    assert isinstance(config.dingtalk, DingtalkHandlerConfig)


def test_log_config_custom():
    config = LogConfig(
        handlers=["console", "file"],
        console=ConsoleHandlerConfig(level="DEBUG")
    )
    assert config.handlers == ["console", "file"]
    assert config.console.level == "DEBUG"
