# omni_logger/handlers/file.py
"""Rotating file handler factory."""
import logging

from concurrent_log_handler import ConcurrentRotatingFileHandler

from omni_logger.config import FileHandlerConfig
from omni_logger.utils.validation import validate_log_level


def create_file_handler(logger_name: str, config: FileHandlerConfig) -> ConcurrentRotatingFileHandler:
    """Create a rotating file handler.

    Args:
        logger_name: Name of the logger (used for log file name)
        config: File handler configuration

    Returns:
        Configured rotating file handler

    Raises:
        OSError: If log directory cannot be created
    """
    # Create log directory if it doesn't exist
    config.log_dir.mkdir(mode=0o777, parents=True, exist_ok=True)

    handler = ConcurrentRotatingFileHandler(
        filename=str(config.log_dir / f"{logger_name}.log"),
        maxBytes=config.max_bytes,
        backupCount=config.backup_count,
        encoding="utf-8"
    )

    level_name = validate_log_level(config.level)
    handler.setLevel(getattr(logging, level_name))
    handler.setFormatter(logging.Formatter(fmt=config.fmt, datefmt=config.datefmt))
    return handler
