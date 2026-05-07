# omni_logger/__init__.py
"""omni-logger: Configurable logging with handler registry pattern."""
from omni_logger.logger_setup import get_logger, set_logger
from omni_logger import config

__all__ = ["set_logger", "get_logger", "config"]
