# Refactor __init__.py Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move `set_logger()` and `get_logger()` implementations from `__init__.py` to `logger_setup.py`, keeping `__init__.py` as a thin re-export layer.

**Architecture:** Create new `logger_setup.py` module containing the two public API functions. Update `__init__.py` to import and re-export them.

**Tech Stack:** Python 3.11+, Poetry

---

### Task 1: Create logger_setup.py module

**Files:**
- Create: `omni_logger/logger_setup.py`

- [ ] **Step 1: Create logger_setup.py with set_logger implementation**

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add omni_logger/logger_setup.py
git commit -m "refactor: create logger_setup.py with set_logger and get_logger implementations"
```

### Task 2: Update __init__.py to re-export

**Files:**
- Modify: `omni_logger/__init__.py`

- [ ] **Step 1: Replace __init__.py content with thin re-export layer**

```python
# omni_logger/__init__.py
"""omni-logger: Configurable logging with handler registry pattern."""
from omni_logger.logger_setup import get_logger, set_logger
from omni_logger import config

__all__ = ["set_logger", "get_logger", "config"]
```

- [ ] **Step 2: Commit**

```bash
git add omni_logger/__init__.py
git commit -m "refactor: update __init__.py to re-export from logger_setup"
```

### Task 3: Verify existing tests pass

**Files:**
- Test: `tests/`

- [ ] **Step 1: Run all tests**

```bash
poetry run pytest tests/ -v
```

Expected: All 39 tests pass

- [ ] **Step 2: Verify imports still work**

```bash
poetry run python -c "from omni_logger import set_logger, get_logger, config; print('Import successful')"
```

Expected: `Import successful`

- [ ] **Step 3: Run type checking**

```bash
poetry run mypy omni_logger
```

Expected: `Success: no issues found`

- [ ] **Step 4: Run linting**

```bash
poetry run ruff check omni_logger tests
```

Expected: `All checks passed!`

- [ ] **Step 5: Commit verification**

```bash
git commit --allow-empty -m "test: verify refactoring - all tests pass"
```

### Task 4: Update README if needed

**Files:**
- Check: `README.md`

- [ ] **Step 1: Review README for any references to __init__.py structure**

```bash
grep -n "__init__" README.md
```

Expected: No references or only non-structural mentions

- [ ] **Step 2: If README mentions implementation details, update it**

If the README mentions where functions are implemented, update it to reference `logger_setup.py`. Otherwise, no changes needed.

- [ ] **Step 3: Commit if changes were made**

```bash
git add README.md
git commit -m "docs: update README to reflect logger_setup.py structure"
```

If no changes were made, skip this step.
