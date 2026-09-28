"""Logging configuration for the whole application."""

import logging
import sys

from codepilot.config import settings
from codepilot.config.settings import get_settings

def configure_logging() -> None:
    settings = get_settings()

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S",)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)


    # Noisy third-party loggers stay quieter than our own code, even in DEBUG
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


