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
    fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    datefmt: str = "%Y-%m-%d %H:%M:%S"


@dataclass
class LogConfig:
    """Logger configuration."""
    handlers: list[str] = field(default_factory=lambda: ["console"])
    console: ConsoleHandlerConfig = field(default_factory=ConsoleHandlerConfig)
    file: FileHandlerConfig = field(default_factory=FileHandlerConfig)
    dingtalk: DingtalkHandlerConfig = field(default_factory=DingtalkHandlerConfig)
