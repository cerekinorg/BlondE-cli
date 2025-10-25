# In utils.py (create if not exists)
import logging
import os
import json
from pathlib import Path

# Configuration file path
CONFIG_FILE = Path.home() / ".blonde" / "config.json"
CONFIG_FILE.parent.mkdir(exist_ok=True)

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


def save_api_key(key_name: str, key_value: str):
    """Save API key to local config file.
    
    Args:
        key_name: Name of the API key (e.g., 'OPENAI_API_KEY')
        key_value: The API key value
    """
    config = {}
    if CONFIG_FILE.exists():
        config = json.loads(CONFIG_FILE.read_text())
    config[key_name] = key_value
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def load_api_key(key_name: str) -> str:
    """Load API key from local config file.
    
    Args:
        key_name: Name of the API key to load
        
    Returns:
        API key value or empty string if not found
    """
    if CONFIG_FILE.exists():
        config = json.loads(CONFIG_FILE.read_text())
        return config.get(key_name, "")
    return ""




