"""Logging configuration utilities for the API Gateway service."""

import logging
import sys


def setup_logging(debug: bool = False) -> None:
    """Configure structured console logging for the application.

    Args:
        debug: If True, set logging level to DEBUG, otherwise INFO.
    """
    log_level = logging.DEBUG if debug else logging.INFO

    # Custom log formatter
    log_format = (
        "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
    )

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,  # Overwrites existing config
    )

    # Reduce verbosity of third party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
