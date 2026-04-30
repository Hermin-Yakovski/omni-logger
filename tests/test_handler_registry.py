# tests/test_handler_registry.py
import pytest

from omni_logger.handlers import HANDLERS, get_handler_class


def test_handlers_registry_has_all_handlers():
    assert "console" in HANDLERS
    assert "file" in HANDLERS
    assert "dingtalk" in HANDLERS


def test_get_handler_class_valid():
    from logging import Handler
    # dingtalk is a class, console and file are factory functions
    handler_class = get_handler_class("dingtalk")
    assert issubclass(handler_class, Handler)


def test_get_handler_class_invalid():
    with pytest.raises(ValueError, match="Unknown handler"):
        get_handler_class("invalid")


def test_error_message_includes_valid_handlers():
    with pytest.raises(ValueError) as exc_info:
        get_handler_class("bad_handler")
    error_msg = str(exc_info.value)
    assert "console" in error_msg
    assert "file" in error_msg
    assert "dingtalk" in error_msg
