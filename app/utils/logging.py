"""
Structured logging configuration.

Sets up JSON-formatted logging for production environments and
human-readable output for local development.
"""

import logging
import sys
from typing import Optional

from app.core.config import get_settings


def setup_logging(level_override: Optional[str] = None) -> None:
    """
    Configure the root logger with structured output.

    Args:
        level_override: Override the log level from settings (useful for tests).
    """
    settings = get_settings()
    level = level_override or settings.LOG_LEVEL

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | %(levelname)-8s | %(name)s | "
            "%(funcName)s:%(lineno)d | %(message)s"
        ),
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    # Clear existing handlers to avoid duplicates on reload
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if settings.DEBUG else logging.WARNING
    )
