# Refactor __init__.py Design

**Date:** 2026-05-07
**Status:** Approved

## Overview

Refactor `omni_logger/__init__.py` to move function implementations to a separate `logger_setup.py` module. The `__init__.py` file should only expose the public API (`set_logger`, `get_logger`, `config`) without containing implementation code.

## Motivation

The current `__init__.py` contains ~70 lines of implementation code for `set_logger()` and `get_logger()` functions. This makes it difficult to:
- Quickly see what the public API exposes
- Maintain the package boundary
- Keep `__init__.py` focused on its purpose: re-exports

## Design

### File Structure

```
omni_logger/
├── __init__.py          # Thin re-export layer (~5 lines)
├── logger_setup.py      # Implementation of set_logger/get_logger
├── config.py            # (unchanged)
└── handlers/            # (unchanged)
```

### Module Responsibilities

**`logger_setup.py`:**
- Contains `set_logger()` implementation
- Contains `get_logger()` implementation
- Internal imports (like `get_handler_class`) stay within this module

**`__init__.py`:**
- Re-exports public API functions from `logger_setup.py`
- Re-exports `config` module
- Defines `__all__` list
- No implementation code

### Implementation Details

**`logger_setup.py` content:**
```python
"""Logger setup functions."""
import logging

from omni_logger import config


def set_logger(name: str, config: config.LogConfig) -> logging.Logger:
    """Create and configure a logger with the specified configuration."""
    from omni_logger.handlers import get_handler_class

    # ... implementation moved from __init__.py


def get_logger(name: str) -> logging.Logger:
    """Get a logger by name."""
    return logging.getLogger(name)
```

**`__init__.py` content:**
```python
"""omni-logger: Configurable logging with handler registry pattern."""
from omni_logger.logger_setup import get_logger, set_logger
from omni_logger import config

__all__ = ["set_logger", "get_logger", "config"]
```

## Testing

- Existing test imports remain unchanged: `from omni_logger import set_logger, get_logger`
- All 39 existing tests pass without modification
- Public API behavior is identical

## Migration

No migration needed - this is an internal refactoring with no breaking changes to the public API.
