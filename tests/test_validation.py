# tests/test_validation.py
import pytest

from omni_logger.utils.validation import validate_log_level


def test_valid_log_levels():
    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        assert validate_log_level(level) == level


def test_valid_log_level_case_insensitive():
    assert validate_log_level("debug") == "DEBUG"
    assert validate_log_level("Info") == "INFO"


def test_invalid_log_level_raises():
    with pytest.raises(ValueError, match="Invalid log level"):
        validate_log_level("INVALID")


def test_error_message_includes_valid_levels():
    with pytest.raises(ValueError) as exc_info:
        validate_log_level("BAD")
    assert "DEBUG" in str(exc_info.value)
    assert "INFO" in str(exc_info.value)
