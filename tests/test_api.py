# tests/test_api.py
import logging

import pytest

from omni_logger import set_logger, LogConfig


def test_set_logger_creates_logger_with_console_handler(tmp_path):
    config = LogConfig()
    logger = set_logger("test_app", config)

    assert logger.name == "test_app"
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)


def test_set_logger_clears_existing_handlers():
    config = LogConfig()
    logger = set_logger("test_app", config)

    # Call again with different config
    config2 = LogConfig(handlers=[])
    logger2 = set_logger("test_app", config2)

    assert logger is logger2  # Same logger instance
    assert len(logger2.handlers) == 0  # Handlers cleared


def test_set_logger_with_file_handler(tmp_path):
    config = LogConfig(handlers=["file"], file=type("obj", (object,), {"log_dir": tmp_path, "level": "INFO", "fmt": "", "datefmt": "", "max_bytes": 1000, "backup_count": 3})())
    logger = set_logger("test_app", config)

    assert len(logger.handlers) == 1
    from concurrent_log_handler import ConcurrentRotatingFileHandler
    assert isinstance(logger.handlers[0], ConcurrentRotatingFileHandler)


def test_set_logger_invalid_handler_name():
    config = LogConfig(handlers=["invalid"])
    with pytest.raises(ValueError, match="Unknown handler"):
        set_logger("test_app", config)


def test_set_logger_creates_log_directory(tmp_path):
    log_dir = tmp_path / "logs"
    config = LogConfig(handlers=["file"], file=type("obj", (object,), {"log_dir": log_dir, "level": "INFO", "fmt": "", "datefmt": "", "max_bytes": 1000, "backup_count": 3})())
    set_logger("test_app", config)

    assert log_dir.exists()


def test_set_logger_applies_formatter():
    config = LogConfig()
    logger = set_logger("test_app", config)

    handler = logger.handlers[0]
    assert handler.formatter is not None
    assert "%(asctime)s" in handler.formatter._fmt
