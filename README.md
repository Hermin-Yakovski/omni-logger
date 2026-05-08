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

### LogConfig

Main configuration dataclass that controls which handlers are enabled and their settings.

**Arguments:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `handlers` | `list[str]` | `["console"]` | List of active handler names (`"console"`, `"file"`, `"dingtalk"`) |
| `console` | `ConsoleHandlerConfig` | `ConsoleHandlerConfig()` | Console handler settings |
| `file` | `FileHandlerConfig` | `FileHandlerConfig()` | File handler settings |
| `dingtalk` | `DingtalkHandlerConfig` | `DingtalkHandlerConfig()` | Dingtalk handler settings |

**Default Behavior:**

All handler configs have sensible defaults. You only need to specify what you want to override:

```python
# Uses default handler: ["console"]
set_logger("my_app", LogConfig())

# Uses default console handler settings (level="INFO", default format)
set_logger("my_app", LogConfig(handlers=["console"]))

# Override only the level, keep other defaults
set_logger("my_app", LogConfig(
    handlers=["console"],
    console=ConsoleHandlerConfig(level="DEBUG")
))
```

Handler configs not explicitly provided will use their default values.

### Console Handler

**Arguments:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Minimum log level (`"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`) |
| `fmt` | `str` | `"%(asctime)s - %(name)s - %(levelname)s - %(message)s"` | Log message format string |
| `datefmt` | `str` | `"%Y-%m-%d %H:%M:%S"` | Timestamp format |

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

**Arguments:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Minimum log level |
| `log_dir` | `Path` | `Path("./logs")` | Directory for log files (created if missing) |
| `max_bytes` | `int` | `10485760` (10MB) | Max file size before rotation |
| `backup_count` | `int` | `5` | Number of backup files to keep |
| `fmt` | `str` | `"%(asctime)s - %(name)s - %(levelname)s - %(message)s"` | Log message format |
| `datefmt` | `str` | `"%Y-%m-%d %H:%M:%S"` | Timestamp format |

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

**Arguments:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str` | `"ERROR"` | Minimum log level (typically `"ERROR"` or `"CRITICAL"`) |

**Required Environment Variables:**

| Variable | Description |
|----------|-------------|
| `ALGO_SERVICES_DINGTALK_ACCESS_TOKEN` | Dingtalk webhook access token |
| `ALGO_SERVICES_DINGTALK_SIGNATURE` | Dingtalk webhook signature secret |

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

**Note:** Missing credentials are silently logged to stderr without crashing.

## API Reference

### `set_logger(name: str, config: LogConfig) -> logging.Logger`

Create and configure a logger with the specified configuration.

- **name**: Logger name (use `__name__` for modules)
- **config**: `LogConfig` dataclass from `omni_logger.config`

### `get_logger(name: str) -> logging.Logger`

Get a previously configured logger by name.

- **name**: Logger name

### `config`

Configuration module containing handler dataclasses.

Import handler configs from `omni_logger.config`:

```python
from omni_logger.config import LogConfig, ConsoleHandlerConfig, FileHandlerConfig, DingtalkHandlerConfig
```

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
