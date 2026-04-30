# tests/test_console_handler.py
import logging

from omni_logger.config import ConsoleHandlerConfig
from omni_logger.handlers.console import create_console_handler


def test_create_console_handler_default_config():
    handler = create_console_handler(ConsoleHandlerConfig())
    assert isinstance(handler, logging.StreamHandler)
    assert handler.level == logging.INFO
    assert handler.formatter is not None


def test_create_console_handler_custom_level():
    config = ConsoleHandlerConfig(level="DEBUG")
    handler = create_console_handler(config)
    assert handler.level == logging.DEBUG


def test_create_console_handler_custom_format():
    config = ConsoleHandlerConfig(
        fmt="%(levelname)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    handler = create_console_handler(config)
    formatter = handler.formatter
    assert formatter._fmt == "%(levelname)s: %(message)s"
    assert formatter.datefmt == "%H:%M:%S"
