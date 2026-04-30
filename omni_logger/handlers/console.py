"""Console handler factory."""
import logging
import sys

from omni_logger.config import ConsoleHandlerConfig
from omni_logger.utils.validation import validate_log_level


def create_console_handler(config: ConsoleHandlerConfig) -> logging.StreamHandler:
    """Create a console handler.

    Args:
        config: Console handler configuration

    Returns:
        Configured console handler
    """
    handler = logging.StreamHandler(sys.stdout)
    level_name = validate_log_level(config.level)
    handler.setLevel(getattr(logging, level_name))
    handler.setFormatter(logging.Formatter(fmt=config.fmt, datefmt=config.datefmt))
    return handler
