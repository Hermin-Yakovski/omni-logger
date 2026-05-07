# omni_logger/logger_setup.py
"""Logger setup functions."""
import logging

from omni_logger import config


def set_logger(name: str, config: config.LogConfig) -> logging.Logger:
    """Create and configure a logger with the specified configuration.

    Args:
        name: Logger name
        config: Log configuration object

    Returns:
        Configured logger instance

    Raises:
        ValueError: If handler name in config.handlers is unknown
        OSError: If log directory cannot be created
    """
    from omni_logger.handlers import get_handler_class

    logger = logging.getLogger(name)
    logger.handlers.clear()  # Clear existing handlers

    # Set logger level based on first handler (or default to INFO)
    if config.handlers:
        first_handler_name = config.handlers[0]
        if first_handler_name == "console":
            logger.setLevel(getattr(logging, config.console.level))
        elif first_handler_name == "file":
            logger.setLevel(getattr(logging, config.file.level))
        elif first_handler_name == "dingtalk":
            logger.setLevel(getattr(logging, config.dingtalk.level))
    else:
        logger.setLevel(logging.INFO)

    # Add configured handlers
    for handler_name in config.handlers:
        handler_class = get_handler_class(handler_name)

        if handler_name == "console":
            handler = handler_class(config.console)
        elif handler_name == "file":
            handler = handler_class(name, config.file)
        elif handler_name == "dingtalk":
            handler = handler_class()
        else:
            # This shouldn't happen as get_handler_class validates
            continue

        logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger by name.

    This is a convenience wrapper around logging.getLogger().
    The logger must have been previously configured via set_logger().

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
