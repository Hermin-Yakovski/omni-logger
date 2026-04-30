"""Handler registry and factory functions."""
from typing import Any

from omni_logger.handlers.console import create_console_handler
from omni_logger.handlers.file import create_file_handler
from omni_logger.handlers.dingtalk import DingtalkErrorHandler


HANDLERS: dict[str, Any] = {
    "console": create_console_handler,
    "file": create_file_handler,
    "dingtalk": DingtalkErrorHandler,
}


def get_handler_class(name: str) -> Any:
    """Get handler class or factory function by name.

    Args:
        name: Handler name (console, file, dingtalk)

    Returns:
        Handler class or factory function

    Raises:
        ValueError: If handler name is unknown
    """
    if name not in HANDLERS:
        valid = ", ".join(HANDLERS.keys())
        raise ValueError(f"Unknown handler: {name}. Valid handlers: {valid}")
    return HANDLERS[name]


__all__ = ["HANDLERS", "get_handler_class", "DingtalkErrorHandler"]
