"""
Handles loading and validation of application configuration.
"""
import json
from pathlib import Path
from typing import Optional

from .settings import AppSettings
from .logger import get_logger

logger = get_logger()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE = BASE_DIR / "config.json"


def load_config(config_path: Path = CONFIG_FILE) -> Optional[AppSettings]:
    """
    Loads configuration from a JSON file and validates it with Pydantic.

    Args:
        config_path: The path to the configuration file.

    Returns:
        An instance of AppSettings if the config is valid, otherwise None.
    """
    if not config_path.exists():
        logger.warning(f"Configuration file not found at {config_path}. Please create it or run the setup wizard.")
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        settings = AppSettings.model_validate(config_data)
        logger.info("Configuration loaded and validated successfully.")
        return settings

    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {config_path}: {e}")
        return None
    except Exception as e:
        # Pydantic's ValidationError will be caught here
        logger.error(f"Configuration validation failed: {e}")
        return None

# Load the configuration globally on startup
Config: Optional[AppSettings] = load_config()
