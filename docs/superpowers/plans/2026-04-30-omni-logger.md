# omni-logger Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python logging package that provides consistent logger configuration across a project with handler registry pattern and three built-in handlers (console, rotating file, Dingtalk).

**Architecture:** Handler registry pattern where handlers are selected by name from a central dict. Each handler has its own dedicated configuration dataclass. The public API (`set_logger()`, `get_logger()`) configures loggers that are retrieved via Python's standard `logging.getLogger()`.

**Tech Stack:** Python 3.11+, dataclasses, standard library `logging` module, `concurrent-log-handler` for file rotation, `requests` for Dingtalk webhooks, `pytest` for testing, `ruff` for linting, `mypy` for type checking.

---

## File Structure

```
omni_logger/
├── __init__.py           # Public API: set_logger(), get_logger()
├── py.typed              # Type checking marker file
├── config.py             # LogConfig and handler config dataclasses
├── handlers/
│   ├── __init__.py       # Handler registry (HANDLERS dict)
│   ├── console.py        # ConsoleHandler factory
│   ├── file.py           # RotatingFileHandler factory
│   └── dingtalk.py       # DingtalkErrorHandler class
└── utils/
    ├── __init__.py
    └── validation.py     # Log level validation

tests/
├── __init__.py
├── conftest.py           # Fixtures (temp log dir, mocked env vars)
├── test_config.py        # Config dataclass tests
├── test_handlers.py      # Handler factory tests
├── test_dingtalk.py      # Dingtalk handler tests
└── test_api.py           # set_logger() and get_logger() tests

pyproject.toml            # Poetry project config and dependencies
README.md                 # Updated with usage examples
```

---

## Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `omni_logger/py.typed`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create pyproject.toml with Poetry**

```bash
cat > pyproject.toml << 'EOF'
[tool.poetry]
name = "omni-logger"
version = "0.1.0"
description = "Customizable logger with handler registry pattern"
authors = ["yehemin <yehemin@example.com>"]
readme = "README.md"
packages = [{include = "omni_logger"}]
include = ["omni_logger/py.typed"]

[tool.poetry.dependencies]
python = "^3.11"
concurrent-log-handler = "^0.9.0"
requests = "^2.31.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
pytest-mock = "^3.11.0"
ruff = "^0.8"
mypy = "^1.10"
pytest-cov = "^7.1.0"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF
```

- [ ] **Step 2: Create package directory structure**

```bash
mkdir -p omni_logger/handlers omni_logger/utils tests
```

- [ ] **Step 3: Create py.typed marker file**

```bash
touch omni_logger/py.typed
```

- [ ] **Step 4: Create test directory init file**

```bash
mkdir -p tests && touch tests/__init__.py
```

- [ ] **Step 5: Create empty __init__ files for subpackages**

```bash
touch omni_logger/handlers/__init__.py omni_logger/utils/__init__.py
```

- [ ] **Step 6: Install dependencies with Poetry**

```bash
poetry install
```

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml omni_logger/py.typed tests/__init__.py omni_logger/handlers/__init__.py omni_logger/utils/__init__.py
git commit -m "chore: set up Poetry project structure and dependencies"
```

---

## Task 2: Config Dataclasses

**Files:**
- Create: `omni_logger/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write failing tests for config dataclasses**

```python
# tests/test_config.py
import logging
from pathlib import Path

import pytest

from omni_logger.config import (
    LogConfig,
    ConsoleHandlerConfig,
    FileHandlerConfig,
    DingtalkHandlerConfig,
)


def test_console_handler_config_defaults():
    config = ConsoleHandlerConfig()
    assert config.level == "INFO"
    assert config.fmt == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    assert config.datefmt == "%Y-%m-%d %H:%M:%S"


def test_console_handler_config_custom():
    config = ConsoleHandlerConfig(level="DEBUG", fmt="%(message)s")
    assert config.level == "DEBUG"
    assert config.fmt == "%(message)s"


def test_file_handler_config_defaults():
    config = FileHandlerConfig()
    assert config.level == "INFO"
    assert config.log_dir == Path("./logs")
    assert config.max_bytes == 10 * 1024 * 1024
    assert config.backup_count == 5


def test_file_handler_config_custom():
    config = FileHandlerConfig(
        log_dir=Path("/var/log"),
        max_bytes=50_000_000,
        backup_count=10
    )
    assert config.log_dir == Path("/var/log")
    assert config.max_bytes == 50_000_000
    assert config.backup_count == 10


def test_dingtalk_handler_config_defaults():
    config = DingtalkHandlerConfig()
    assert config.level == "ERROR"
    assert config.min_level == logging.ERROR


def test_log_config_defaults():
    config = LogConfig()
    assert config.handlers == ["console"]
    assert isinstance(config.console, ConsoleHandlerConfig)
    assert isinstance(config.file, FileHandlerConfig)
    assert isinstance(config.dingtalk, DingtalkHandlerConfig)


def test_log_config_custom():
    config = LogConfig(
        handlers=["console", "file"],
        console=ConsoleHandlerConfig(level="DEBUG")
    )
    assert config.handlers == ["console", "file"]
    assert config.console.level == "DEBUG"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_config.py -v
```

Expected: `ImportError: cannot import name 'LogConfig'`

- [ ] **Step 3: Implement config dataclasses**

```python
# omni_logger/config.py
"""Configuration dataclasses for omni-logger."""
import logging
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ConsoleHandlerConfig:
    """Console handler configuration."""
    level: str = "INFO"
    fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    datefmt: str = "%Y-%m-%d %H:%M:%S"


@dataclass
class FileHandlerConfig:
    """Rotating file handler configuration."""
    level: str = "INFO"
    log_dir: Path = Path("./logs")
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    datefmt: str = "%Y-%m-%d %H:%M:%S"


@dataclass
class DingtalkHandlerConfig:
    """Dingtalk error handler configuration."""
    level: str = "ERROR"
    min_level: int = logging.ERROR


@dataclass
class LogConfig:
    """Logger configuration."""
    handlers: list[str] = field(default_factory=lambda: ["console"])
    console: ConsoleHandlerConfig = field(default_factory=ConsoleHandlerConfig)
    file: FileHandlerConfig = field(default_factory=FileHandlerConfig)
    dingtalk: DingtalkHandlerConfig = field(default_factory=DingtalkHandlerConfig)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_config.py -v
```

Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add omni_logger/config.py tests/test_config.py
git commit -m "feat: add config dataclasses with defaults"
```

---

## Task 3: Log Level Validation Utility

**Files:**
- Create: `omni_logger/utils/validation.py`
- Create: `omni_logger/utils/__init__.py`
- Test: `tests/test_validation.py`

- [ ] **Step 1: Write failing tests for log level validation**

```python
# tests/test_validation.py
import pytest

from omni_logger.utils.validation import validate_log_level, VALID_LEVELS


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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_validation.py -v
```

Expected: `ImportError`

- [ ] **Step 3: Implement validation utility**

```python
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
```

```python
# omni_logger/utils/__init__.py
"""Utilities for omni-logger."""

from omni_logger.utils.validation import validate_log_level, VALID_LEVELS

__all__ = ["validate_log_level", "VALID_LEVELS"]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_validation.py -v
```

Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add omni_logger/utils/ tests/test_validation.py
git commit -m "feat: add log level validation utility"
```

---

## Task 4: Handler Registry

**Files:**
- Create: `omni_logger/handlers/__init__.py`
- Test: `tests/test_handler_registry.py`

- [ ] **Step 1: Write failing tests for handler registry**

```python
# tests/test_handler_registry.py
import pytest

from omni_logger.handlers import HANDLERS, get_handler_class


def test_handlers_registry_has_all_handlers():
    assert "console" in HANDLERS
    assert "file" in HANDLERS
    assert "dingtalk" in HANDLERS


def test_get_handler_class_valid():
    from logging import Handler
    handler_class = get_handler_class("console")
    assert issubclass(handler_class, Handler)


def test_get_handler_class_invalid():
    with pytest.raises(ValueError, match="Unknown handler"):
        get_handler_class("invalid")


def test_error_message_includes_valid_handlers():
    with pytest.raises(ValueError) as exc_info:
        get_handler_class("bad_handler")
    error_msg = str(exc_info.value)
    assert "console" in error_msg
    assert "file" in error_msg
    assert "dingtalk" in error_msg
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_handler_registry.py -v
```

Expected: `ImportError`

- [ ] **Step 3: Implement handler registry (placeholder for now)**

```python
# omni_logger/handlers/__init__.py
"""Handler registry and factory functions."""
import logging

from omni_logger.handlers.console import create_console_handler
from omni_logger.handlers.file import create_file_handler
from omni_logger.handlers.dingtalk import DingtalkErrorHandler


HANDLERS: dict[str, logging.Handler] = {
    "console": create_console_handler,
    "file": create_file_handler,
    "dingtalk": DingtalkErrorHandler,
}


def get_handler_class(name: str) -> logging.Handler:
    """Get handler class by name.

    Args:
        name: Handler name (console, file, dingtalk)

    Returns:
        Handler class or callable

    Raises:
        ValueError: If handler name is unknown
    """
    if name not in HANDLERS:
        valid = ", ".join(HANDLERS.keys())
        raise ValueError(f"Unknown handler: {name}. Valid handlers: {valid}")
    return HANDLERS[name]


__all__ = ["HANDLERS", "get_handler_class", "DingtalkErrorHandler"]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_handler_registry.py -v
```

Expected: All tests pass (registry exists, handlers will be added in next tasks)

- [ ] **Step 5: Commit**

```bash
git add omni_logger/handlers/__init__.py tests/test_handler_registry.py
git commit -m "feat: add handler registry"
```

---

## Task 5: Console Handler Factory

**Files:**
- Create: `omni_logger/handlers/console.py`
- Test: `tests/test_console_handler.py`

- [ ] **Step 1: Write failing tests for console handler**

```python
# tests/test_console_handler.py
import logging

from omni_logger.config import ConsoleHandlerConfig
from omni_logger.handlers.console import create_console_handler


def test_create_console_handler_default_config():
    handler = create_console_handler(ConsoleHandlerConfig())
    assert isinstance(handler, logging.StreamHandler)
    assert handler.level == logging.INFO
    assert handler.formatter is not None


def test_create_console_handler_custom_level():
    config = ConsoleHandlerConfig(level="DEBUG")
    handler = create_console_handler(config)
    assert handler.level == logging.DEBUG


def test_create_console_handler_custom_format():
    config = ConsoleHandlerConfig(
        fmt="%(levelname)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    handler = create_console_handler(config)
    formatter = handler.formatter
    assert formatter._fmt == "%(levelname)s: %(message)s"
    assert formatter.datefmt == "%H:%M:%S"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_console_handler.py -v
```

Expected: `ImportError`

- [ ] **Step 3: Implement console handler factory**

```python
# omni_logger/handlers/console.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_console_handler.py -v
```

Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add omni_logger/handlers/console.py tests/test_console_handler.py
git commit -m "feat: add console handler factory"
```

---

## Task 6: File Handler Factory

**Files:**
- Create: `omni_logger/handlers/file.py`
- Test: `tests/test_file_handler.py`

- [ ] **Step 1: Write failing tests for file handler**

```python
# tests/test_file_handler.py
import logging
from pathlib import Path
import tempfile

import pytest

from omni_logger.config import FileHandlerConfig
from omni_logger.handlers.file import create_file_handler


def test_create_file_handler_default_config(tmp_path):
    config = FileHandlerConfig(log_dir=tmp_path)
    handler = create_file_handler("test_logger", config)
    from concurrent_log_handler import ConcurrentRotatingFileHandler
    assert isinstance(handler, ConcurrentRotatingFileHandler)
    assert handler.level == logging.INFO


def test_create_file_handler_creates_log_dir(tmp_path):
    log_dir = tmp_path / "nested" / "logs"
    config = FileHandlerConfig(log_dir=log_dir)
    handler = create_file_handler("test_logger", config)
    assert log_dir.exists()


def test_create_file_handler_custom_rotation():
    config = FileHandlerConfig(max_bytes=50_000_000, backup_count=10)
    handler = create_file_handler("test_logger", config)
    assert handler.maxBytes == 50_000_000
    assert handler.backupCount == 10


def test_create_file_handler_custom_format(tmp_path):
    config = FileHandlerConfig(
        log_dir=tmp_path,
        fmt="%(levelname)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    handler = create_file_handler("test_logger", config)
    formatter = handler.formatter
    assert formatter._fmt == "%(levelname)s: %(message)s"
    assert formatter.datefmt == "%H:%M:%S"


def test_create_file_handler_log_file_naming(tmp_path):
    config = FileHandlerConfig(log_dir=tmp_path)
    handler = create_file_handler("my_app", config)
    assert handler.baseFilename == str(tmp_path / "my_app.log")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_file_handler.py -v
```

Expected: `ImportError`

- [ ] **Step 3: Implement file handler factory**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_file_handler.py -v
```

Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add omni_logger/handlers/file.py tests/test_file_handler.py
git commit -m "feat: add rotating file handler factory"
```

---

## Task 7: Dingtalk Error Handler

**Files:**
- Create: `omni_logger/handlers/dingtalk.py`
- Test: `tests/test_dingtalk_handler.py`

- [ ] **Step 1: Write failing tests for Dingtalk handler**

```python
# tests/test_dingtalk_handler.py
import logging
import os
from unittest.mock import MagicMock, patch

import pytest

from omni_logger.handlers.dingtalk import DingtalkErrorHandler


def test_dingtalk_handler_filters_below_error():
    handler = DingtalkErrorHandler()
    assert handler.level >= logging.ERROR


def test_dingtalk_handler_emits_error_records(mock_requests_post):
    handler = DingtalkErrorHandler()
    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname="test.py",
        lineno=1,
        msg="Test error",
        args=(),
        exc_info=None
    )
    handler.emit(record)
    mock_requests_post.assert_called_once()


def test_dingtalk_handler_ignores_info_records(mock_requests_post):
    handler = DingtalkErrorHandler()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test info",
        args=(),
        exc_info=None
    )
    handler.emit(record)
    mock_requests_post.assert_not_called()


def test_dingtalk_handler_missing_env_vars_logs_warning(capfd):
    # Clear env vars
    os.environ.pop("ALGO_SERVICES_DINGTALK_ACCESS_TOKEN", None)
    os.environ.pop("ALGO_SERVICES_DINGTALK_SIGNATURE", None)

    handler = DingtalkErrorHandler()
    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname="test.py",
        lineno=1,
        msg="Test error",
        args=(),
        exc_info=None
    )
    handler.emit(record)

    captured = capfd.readouterr()
    assert "DingtalkErrorHandler" in captured.err


def test_dingtalk_handler_send_failure_prints_to_stderr(capfd, mock_requests_post):
    os.environ["ALGO_SERVICES_DINGTALK_ACCESS_TOKEN"] = "test_token"
    os.environ["ALGO_SERVICES_DINGTALK_SIGNATURE"] = "test_secret"

    mock_requests_post.side_effect = Exception("Network error")

    handler = DingtalkErrorHandler()
    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname="test.py",
        lineno=1,
        msg="Test error",
        args=(),
        exc_info=None
    )
    handler.emit(record)

    captured = capfd.readouterr()
    assert "Failed" in captured.err
```

- [ ] **Step 2: Add conftest fixtures for Dingtalk tests**

```python
# tests/conftest.py
import logging
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def tmp_log_dir(tmp_path):
    """Temporary log directory for testing."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir(exist_ok=True)
    return log_dir


@pytest.fixture
def mock_dingtalk_env():
    """Set up Dingtalk environment variables for testing."""
    original_token = os.environ.get("ALGO_SERVICES_DINGTALK_ACCESS_TOKEN")
    original_signature = os.environ.get("ALGO_SERVICES_DINGTALK_SIGNATURE")

    os.environ["ALGO_SERVICES_DINGTALK_ACCESS_TOKEN"] = "test_token"
    os.environ["ALGO_SERVICES_DINGTALK_SIGNATURE"] = "test_secret"

    yield

    if original_token is not None:
        os.environ["ALGO_SERVICES_DINGTALK_ACCESS_TOKEN"] = original_token
    else:
        os.environ.pop("ALGO_SERVICES_DINGTALK_ACCESS_TOKEN", None)

    if original_signature is not None:
        os.environ["ALGO_SERVICES_DINGTALK_SIGNATURE"] = original_signature
    else:
        os.environ.pop("ALGO_SERVICES_DINGTALK_SIGNATURE", None)


@pytest.fixture
def mock_requests_post(monkeypatch):
    """Mock requests.post for Dingtalk tests."""
    mock = MagicMock()
    monkeypatch.setattr("requests.post", mock)
    return mock
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
pytest tests/test_dingtalk_handler.py -v
```

Expected: `ImportError`

- [ ] **Step 4: Implement Dingtalk error handler**

```python
# omni_logger/handlers/dingtalk.py
"""Dingtalk error handler for logging notifications."""
import base64
import hashlib
import hmac
import json
import logging
import os
import time
from urllib.parse import quote_plus

import requests


class DingtalkErrorHandler(logging.Handler):
    """Send ERROR and above log records to Dingtalk webhook."""

    _access_token: str
    _signature: str
    _url_body: str

    def __init__(self):
        super().__init__()
        self._access_token = os.getenv("ALGO_SERVICES_DINGTALK_ACCESS_TOKEN", "")
        self._signature = os.getenv("ALGO_SERVICES_DINGTALK_SIGNATURE", "")
        self._url_body = "https://oapi.dingtalk.com/robot/send"

        # Set level to ERROR by default
        self.setLevel(logging.ERROR)

    def _generate_url_with_timestamp(self) -> str:
        """Generate signed URL with timestamp."""
        timestamp = str(round(time.time() * 1000))
        hmac_code = hmac.new(
            self._signature.encode("utf-8"),
            f"{timestamp}\n{self._signature}".encode("utf-8"),
            digestmod=hashlib.sha256
        ).digest()
        sign = quote_plus(base64.b64encode(hmac_code).decode("utf-8"))
        return self._url_body + f"?access_token={self._access_token}&timestamp={timestamp}&sign={sign}"

    def emit(self, record: logging.LogRecord):
        """Emit a log record if level is ERROR or above.

        Missing credentials or send failures are logged to stderr but don't crash.
        """
        if record.levelno < logging.ERROR:
            return

        if not self._access_token or not self._signature:
            print("DingtalkErrorHandler: Missing ALGO_SERVICES_DINGTALK_ACCESS_TOKEN or ALGO_SERVICES_DINGTALK_SIGNATURE env vars", file=__import__("sys").stderr)
            return

        self.format(record)
        self.send(record)

    def send(self, record: logging.LogRecord):
        """Send log record to Dingtalk.

        Send failures are printed to stderr but don't propagate.
        """
        data = {
            "msgtype": "text",
            "text": {
                "content": {
                    "asctime": record.asctime,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "filename": record.filename,
                    "lineno": record.lineno,
                }
            },
            "at": {
                "atMobiles": [],
                "isAtAll": False
            }
        }

        try:
            requests.post(
                url=self._generate_url_with_timestamp(),
                headers={"Content-Type": "application/json"},
                data=json.dumps(data, ensure_ascii=False)
            )
        except Exception as e:
            print(f"DingtalkErrorHandler.send() Failed: {e}", file=__import__("sys").stderr)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_dingtalk_handler.py -v
```

Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add omni_logger/handlers/dingtalk.py tests/test_dingtalk_handler.py tests/conftest.py
git commit -m "feat: add Dingtalk error handler"
```

---

## Task 8: Public API - set_logger() Function

**Files:**
- Create: `omni_logger/__init__.py`
- Test: `tests/test_api.py`

- [ ] **Step 1: Write failing tests for set_logger()**

```python
# tests/test_api.py
import logging
from pathlib import Path
import tempfile

import pytest

from omni_logger import set_logger, get_logger, LogConfig


def test_set_logger_creates_logger_with_console_handler(tmp_path):
    config = LogConfig()
    logger = set_logger("test_app", config)

    assert logger.name == "test_app"
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)


def test_set_logger_clears_existing_handlers():
    config = LogConfig()
    logger = set_logger("test_app", config)

    # Call again with different config
    config2 = LogConfig(handlers=[])
    logger2 = set_logger("test_app", config2)

    assert logger is logger2  # Same logger instance
    assert len(logger2.handlers) == 0  # Handlers cleared


def test_set_logger_with_file_handler(tmp_path):
    config = LogConfig(handlers=["file"], file=type("obj", (object,), {"log_dir": tmp_path, "level": "INFO", "fmt": "", "datefmt": "", "max_bytes": 1000, "backup_count": 3})())
    logger = set_logger("test_app", config)

    assert len(logger.handlers) == 1
    from concurrent_log_handler import ConcurrentRotatingFileHandler
    assert isinstance(logger.handlers[0], ConcurrentRotatingFileHandler)


def test_set_logger_invalid_handler_name():
    config = LogConfig(handlers=["invalid"])
    with pytest.raises(ValueError, match="Unknown handler"):
        set_logger("test_app", config)


def test_set_logger_creates_log_directory(tmp_path):
    log_dir = tmp_path / "logs"
    config = LogConfig(handlers=["file"], file=type("obj", (object,), {"log_dir": log_dir, "level": "INFO", "fmt": "", "datefmt": "", "max_bytes": 1000, "backup_count": 3})())
    set_logger("test_app", config)

    assert log_dir.exists()


def test_set_logger_applies_formatter():
    config = LogConfig()
    logger = set_logger("test_app", config)

    handler = logger.handlers[0]
    assert handler.formatter is not None
    assert "%(asctime)s" in handler.formatter._fmt
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_api.py -v
```

Expected: `ImportError`

- [ ] **Step 3: Implement set_logger() function**

```python
# omni_logger/__init__.py
"""omni-logger: Configurable logging with handler registry pattern."""
import logging

from omni_logger.config import LogConfig
from omni_logger.handlers import get_handler_class


def set_logger(name: str, config: LogConfig) -> logging.Logger:
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


__all__ = ["set_logger", "get_logger", "LogConfig"]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_api.py -v
```

Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add omni_logger/__init__.py tests/test_api.py
git commit -m "feat: add set_logger() and get_logger() public API"
```

---

## Task 9: Integration Tests

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: Write integration tests**

```python
# tests/test_integration.py
import logging
from pathlib import Path
import tempfile

import pytest

from omni_logger import set_logger, get_logger, LogConfig, FileHandlerConfig


def test_get_logger_returns_same_as_logging_getLogger():
    """Verify get_logger() is symmetric with logging.getLogger()."""
    config = LogConfig()
    set_logger("test_app", config)

    logger1 = get_logger("test_app")
    logger2 = logging.getLogger("test_app")

    assert logger1 is logger2


def test_full_logging_flow_console_and_file(tmp_path, caplog):
    """Test end-to-end logging with console and file handlers."""
    config = LogConfig(
        handlers=["console", "file"],
        file=FileHandlerConfig(log_dir=tmp_path)
    )
    logger = set_logger("integration_test", config)

    with caplog.at_level(logging.INFO):
        logger.info("Test message")

    # Verify console captured the log
    assert any("Test message" in record.message for record in caplog.records)

    # Verify file captured the log
    log_file = tmp_path / "integration_test.log"
    assert log_file.exists()
    content = log_file.read_text()
    assert "Test message" in content


def test_logger_reconfiguration():
    """Test that calling set_logger() again replaces configuration."""
    config1 = LogConfig(handlers=["console"])
    logger1 = set_logger("reconfig_test", config1)
    assert len(logger1.handlers) == 1

    config2 = LogConfig(handlers=["console", "file"])
    logger2 = set_logger("reconfig_test", config2)
    assert logger1 is logger2  # Same instance
    assert len(logger2.handlers) == 2  # Reconfigured


def test_dingtalk_handler_integration(mock_requests_post, mock_dingtalk_env):
    """Test Dingtalk handler sends ERROR level logs."""
    config = LogConfig(handlers=["dingtalk"])
    logger = set_logger("dingtalk_test", config)

    logger.error("Critical error occurred")

    # Verify Dingtalk was called
    mock_requests_post.assert_called_once()


def test_dingtalk_handler_skips_info_logs(mock_requests_post, mock_dingtalk_env):
    """Test Dingtalk handler ignores INFO level logs."""
    config = LogConfig(handlers=["dingtalk"])
    logger = set_logger("dingtalk_test", config)

    logger.info("This should not trigger Dingtalk")

    # Verify Dingtalk was NOT called
    mock_requests_post.assert_not_called()
```

- [ ] **Step 2: Run integration tests**

```bash
pytest tests/test_integration.py -v
```

Expected: All tests pass

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration tests"
```

---

## Task 10: Update README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README with usage examples**

```markdown
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
from omni_logger import set_logger, LogConfig

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
from omni_logger import set_logger, LogConfig, ConsoleHandlerConfig

set_logger("my_app", LogConfig(
    console=ConsoleHandlerConfig(
        level="DEBUG",
        fmt="%(levelname)s: %(message)s"
    )
))
```

### File Handler with Rotation

```python
from omni_logger import set_logger, LogConfig, FileHandlerConfig

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
from omni_logger import set_logger, LogConfig

# Set environment variables
os.environ["ALGO_SERVICES_DINGTALK_ACCESS_TOKEN"] = "your_token"
os.environ["ALGO_SERVICES_DINGTALK_SIGNATURE"] = "your_signature"

set_logger("my_app", LogConfig(
    handlers=["console", "dingtalk"]
))

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
```

- [ ] **Step 2: Verify README renders correctly**

```bash
cat README.md
```

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: update README with usage examples"
```

---

## Task 11: Final Verification

**Files:**
- Test: All tests

- [ ] **Step 1: Run all tests**

```bash
pytest tests/ -v
```

Expected: All tests pass

- [ ] **Step 2: Run tests with coverage**

```bash
pytest --cov=omni_logger --cov-report=term-missing
```

Expected: High coverage (90%+)

- [ ] **Step 3: Run ruff linting**

```bash
poetry run ruff check omni_logger tests
```

Expected: No linting errors

- [ ] **Step 4: Run mypy type checking**

```bash
poetry run mypy omni_logger
```

Expected: No type errors

- [ ] **Step 5: Verify package structure**

- [ ] **Step 6: Verify package structure**

```bash
python -c "from omni_logger import set_logger, get_logger, LogConfig; print('Import successful')"
```

Expected: `Import successful`

- [ ] **Step 7: Verify example usage works**

```bash
python -c "
from omni_logger import set_logger, get_logger, LogConfig
from pathlib import Path
import tempfile

tmp_dir = Path(tempfile.mkdtemp())
set_logger('test', LogConfig(handlers=['console'], file=type('FC', (), {'log_dir': tmp_dir, 'level': 'INFO', 'fmt': '', 'datefmt': '', 'max_bytes': 1000, 'backup_count': 3})()))
logger = get_logger('test')
logger.info('Test message works!')
print('Example successful!')
"
```

Expected: No errors, "Test message works!" and "Example successful!" printed

- [ ] **Step 8: Final commit (if any fixes needed)**

```bash
git status
git add ...
git commit -m "..."
```

---

## Completion Checklist

- [ ] All tasks completed
- [ ] All tests passing
- [ ] README updated
- [ ] No placeholders in code
- [ ] Package can be imported and used
- [ ] Example usage verified

**Plan Status:** Ready for implementation
