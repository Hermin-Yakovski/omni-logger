# tests/test_file_handler.py
import logging
from pathlib import Path
import tempfile

import pytest

from omni_logger.config import FileHandlerConfig
from omni_logger.handlers.file import create_file_handler


def test_create_file_handler_default_config(tmp_path):
    config = FileHandlerConfig(log_dir=tmp_path)
    handler = create_file_handler("test_logger", config)
    from concurrent_log_handler import ConcurrentRotatingFileHandler
    assert isinstance(handler, ConcurrentRotatingFileHandler)
    assert handler.level == logging.INFO


def test_create_file_handler_creates_log_dir(tmp_path):
    log_dir = tmp_path / "nested" / "logs"
    config = FileHandlerConfig(log_dir=log_dir)
    handler = create_file_handler("test_logger", config)
    assert log_dir.exists()


def test_create_file_handler_custom_rotation():
    config = FileHandlerConfig(max_bytes=50_000_000, backup_count=10)
    handler = create_file_handler("test_logger", config)
    assert handler.maxBytes == 50_000_000
    assert handler.backupCount == 10


def test_create_file_handler_custom_format(tmp_path):
    config = FileHandlerConfig(
        log_dir=tmp_path,
        fmt="%(levelname)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    handler = create_file_handler("test_logger", config)
    formatter = handler.formatter
    assert formatter._fmt == "%(levelname)s: %(message)s"
    assert formatter.datefmt == "%H:%M:%S"


def test_create_file_handler_log_file_naming(tmp_path):
    config = FileHandlerConfig(log_dir=tmp_path)
    handler = create_file_handler("my_app", config)
    assert handler.baseFilename == str(tmp_path / "my_app.log")
