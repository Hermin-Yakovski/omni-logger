# omni-logger Design

**Date:** 2026-04-30
**Status:** Approved

## Overview

A Python logging package that provides consistent logger configuration across a project. Loggers are configured via a `set_logger()` function that accepts a `LogConfig` dataclass. Modules retrieve pre-configured loggers using Python's standard `logging.getLogger()` or the symmetric `get_logger()` wrapper.

The package includes three built-in handlers:
- **Console** — Stdout output with configurable formatting
- **File** — Rotating file logs with configurable size/count thresholds
- **Dingtalk** — Error-level notifications sent to Dingtalk (credentials via env vars)

Handlers are selected by name from a registry, with each handler having its own dedicated configuration dataclass.

## Architecture

```
omni_logger/
├── __init__.py           # Public API: set_logger(), get_logger()
├── config.py             # LogConfig and handler config dataclasses
├── handlers/
│   ├── __init__.py       # Handler registry (HANDLERS dict)
│   ├── console.py        # ConsoleHandler
│   ├── file.py           # RotatingFileHandler
│   └── dingtalk.py       # DingtalkErrorHandler
└── utils/
    └── __init__.py       # Shared utilities (if needed)
```

### Public API

```python
from omni_logger import set_logger, get_logger, LogConfig

# Configure logger
set_logger("my_module", LogConfig(...))

# Retrieve logger (symmetric API)
logger = get_logger("my_module")

# Or use standard library (equivalent)
import logging
logger = logging.getLogger("my_module")
```

### Data Flow

1. Application calls `set_logger(name, LogConfig(...))`
2. `set_logger()` gets or creates logger via `logging.getLogger(name)`
3. Clears existing handlers via `logger.handlers.clear()`, sets logger level
4. For each handler name in `config.handlers`:
   - Lookup handler class from `HANDLERS` registry
   - Get corresponding config (e.g., `config.console`)
   - Instantiate handler with config
   - Set formatter and add to logger
5. Modules call `get_logger(name)` or `logging.getLogger(name)` to retrieve

**Note:** Calling `set_logger()` multiple times for the same logger name replaces the previous configuration (all existing handlers are cleared).

### Handler Registry

```python
HANDLERS: dict[str, type[logging.Handler]] = {
    "console": ConsoleHandler,
    "file": RotatingFileHandler,
    "dingtalk": DingtalkErrorHandler,
}
```

## Components

### LogConfig

Main configuration dataclass.

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class LogConfig:
    """Logger configuration."""
    handlers: list[str] = field(default_factory=lambda: ["console"])
    console: ConsoleHandlerConfig = field(default_factory=ConsoleHandlerConfig)
    file: FileHandlerConfig = field(default_factory=FileHandlerConfig)
    dingtalk: DingtalkHandlerConfig = field(default_factory=DingtalkHandlerConfig)
```

### ConsoleHandlerConfig

Console output configuration.

```python
@dataclass
class ConsoleHandlerConfig:
    """Console handler configuration."""
    level: str = "INFO"
    fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    datefmt: str = "%Y-%m-%d %H:%M:%S"
```

### FileHandlerConfig

Rotating file configuration.

```python
@dataclass
class FileHandlerConfig:
    """Rotating file handler configuration."""
    level: str = "INFO"
    log_dir: Path = Path("./logs")
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    datefmt: str = "%Y-%m-%d %H:%M:%S"
```

### DingtalkHandlerConfig

Dingtalk notification configuration. Credentials are read from environment variables.

```python
import logging

@dataclass
class DingtalkHandlerConfig:
    """Dingtalk error handler configuration."""
    level: str = "ERROR"
    min_level: int = logging.ERROR  # Only send ERROR and above
```

**Environment Variables:**
- `ALGO_SERVICES_DINGTALK_ACCESS_TOKEN` — Dingtalk webhook access token
- `ALGO_SERVICES_DINGTALK_SIGNATURE` — Dingtalk webhook signature

## Error Handling

### Configuration Errors
- Invalid handler name → `ValueError` with list of valid handlers
- Invalid log level string → `ValueError` with valid levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File handler: unable to create log directory → `OSError` propagated to caller

### Handler-Specific Errors
- Dingtalk handler: missing env vars → log warning via `sys.stderr`, handler silently fails (doesn't crash logger)
- Dingtalk handler: send failure → catch exception, print to stderr, don't propagate

### Design Principle
Logger configuration failures should be visible but not crash the application. Handlers that fail to initialize should log warnings and be skipped.

## Testing

### Unit Tests
- `set_logger()` creates logger with correct level and handlers
- Handler registry returns correct handler classes
- Each handler configures formatter correctly
- Invalid handler names raise `ValueError`
- Invalid log levels raise `ValueError`
- File handler creates log directory if missing

### Integration Tests
- `get_logger(name)` returns same logger as `logging.getLogger(name)`
- Log output writes to correct files
- Dingtalk handler sends to correct URL (mocked requests)

### Test Fixtures
- Temporary log directory (fixture cleanup)
- Mocked env vars for Dingtalk credentials
- Mocked `requests.post` for Dingtalk tests

## Usage Example

```python
# main.py - Application entry point
from omni_logger import set_logger, LogConfig, FileHandlerConfig

set_logger("my_app", LogConfig(
    handlers=["console", "file", "dingtalk"],
    file=FileHandlerConfig(max_bytes=50_000_000)  # 50MB rotation
))

# my_module.py - Application module
from omni_logger import get_logger

logger = get_logger("my_app")
logger.info("Application started")
logger.error("Something went wrong")  # Triggers Dingtalk notification
```
