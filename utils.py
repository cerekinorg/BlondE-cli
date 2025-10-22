# In utils.py (create if not exists)
import logging
import os
from pathlib import Path

def setup_logging(debug: bool = False):
    """Sets up logging to file and console.
    Args:
        debug: If True, log debug messages to console and file.
    """
    log_dir = Path.home() / ".blonde"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "debug.log"

    logger = logging.getLogger("blonde")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # File handler (always log DEBUG)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)

    # Console handler (INFO unless debug)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)

    # Avoid duplicate handlers
    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger




