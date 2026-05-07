# omni-logger

A Python logging package that provides consistent logger configuration across your project using a handler registry pattern.

## Features

- **Handler Registry Pattern** — Select handlers by name: `console`, `file`, `dingtalk`
- **Type-Safe Configuration** — Dataclass-based config with sensible defaults
- **Symmetric API** — `set_logger()` to configure, `get_logger()` to retrieve
- **Standard Library Compatible** — Works with Python's built-in `logging` module

## Installation

```bash
pip install omni-logger
```

## Quick Start

```python
# main.py - Application entry point
from omni_logger import set_logger
from omni_logger.config import LogConfig

# Configure logger with console and file handlers
set_logger("my_app", LogConfig(
    handlers=["console", "file"]
))

# my_module.py - Application module
from omni_logger import get_logger

logger = get_logger("my_app")
logger.info("Application started")
logger.error("Something went wrong")
```

## Configuration

### Console Handler

```python
from omni_logger import set_logger
from omni_logger.config import LogConfig, ConsoleHandlerConfig

set_logger("my_app", LogConfig(
    console=ConsoleHandlerConfig(
        level="DEBUG",
        fmt="%(levelname)s: %(message)s"
    )
))
```

### File Handler with Rotation

```python
from pathlib import Path
from omni_logger import set_logger
from omni_logger.config import LogConfig, FileHandlerConfig

set_logger("my_app", LogConfig(
    handlers=["console", "file"],
    file=FileHandlerConfig(
        log_dir=Path("./logs"),
        max_bytes=50_000_000,  # 50MB
        backup_count=10
    )
))
```

### Dingtalk Error Notifications

```python
import os
from omni_logger import set_logger, get_logger
from omni_logger.config import LogConfig

# Set environment variables
os.environ["ALGO_SERVICES_DINGTALK_ACCESS_TOKEN"] = "your_token"
os.environ["ALGO_SERVICES_DINGTALK_SIGNATURE"] = "your_signature"

set_logger("my_app", LogConfig(
    handlers=["console", "dingtalk"]
))

# Get the logger instance
logger = get_logger("my_app")

# ERROR and above will be sent to Dingtalk
logger.error("Critical failure!")
```

## API Reference

### `set_logger(name: str, config: LogConfig) -> logging.Logger`

Create and configure a logger with the specified configuration.

- **name**: Logger name (use `__name__` for modules)
- **config**: `LogConfig` dataclass with handler configuration

### `get_logger(name: str) -> logging.Logger`

Get a previously configured logger by name.

- **name**: Logger name

### `LogConfig`

Main configuration dataclass.

- **handlers**: List of handler names (`["console"]`, `["console", "file"]`, etc.)
- **console**: `ConsoleHandlerConfig` — Console output settings
- **file**: `FileHandlerConfig` — Rotating file settings
- **dingtalk**: `DingtalkHandlerConfig` — Dingtalk notification settings

## Development

```bash
# Install with Poetry
poetry install

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=omni_logger

# Run linting
poetry run ruff check omni_logger tests

# Run type checking
poetry run mypy omni_logger
```

## License

MIT License
