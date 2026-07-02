"""Reusable logging configuration for ImmortalStudio."""

from __future__ import annotations

import logging
from pathlib import Path


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def setup_logging(level: int = logging.INFO) -> None:
    """Configure console logging for the application."""

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if not any(isinstance(handler, logging.StreamHandler) for handler in root_logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        root_logger.addHandler(console_handler)


def add_file_handler(logger: logging.Logger, log_path: Path, level: int = logging.INFO) -> None:
    """Attach a file handler to a logger if that file is not already attached."""

    log_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_log_path = log_path.resolve()

    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            if Path(handler.baseFilename).resolve() == resolved_log_path:
                return

    file_handler = logging.FileHandler(resolved_log_path, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Return a named project logger."""

    setup_logging()
    return logging.getLogger(name)
