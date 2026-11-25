import sys
import logging

from core.settings import settings


def setup_logging(level: int | None = None) -> logging.Logger:
    """
    Configure the ``agent`` logger with a stderr handler (idempotent).

    Args:
        level (int | None): Log level; defaults to DEBUG when ``settings.debug``
            is set, otherwise INFO.

    Returns:
        logging.Logger: The configured ``agent`` logger.
    """
    logger = logging.getLogger("agent")

    if logger.handlers:
        return logger

    if level is None:
        level = logging.DEBUG if settings().debug else logging.INFO

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ),
    )

    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False

    return logger
