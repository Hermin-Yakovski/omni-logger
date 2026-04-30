# omni_logger/utils/validation.py
"""Log level validation utility."""

VALID_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def validate_log_level(level: str) -> str:
    """Validate and normalize log level string.

    Args:
        level: Log level string (case-insensitive)

    Returns:
        Uppercase normalized log level

    Raises:
        ValueError: If level is not a valid log level
    """
    level_upper = level.upper()
    if level_upper not in VALID_LEVELS:
        valid = ", ".join(VALID_LEVELS)
        raise ValueError(f"Invalid log level: {level}. Valid levels: {valid}")
    return level_upper
