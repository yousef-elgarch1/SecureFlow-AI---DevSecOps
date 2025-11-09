"""
Utility functions for the application
"""
import os
import yaml
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_env(key: str, default: str = None) -> str:
    """Get environment variable"""
    return os.getenv(key, default)

def ensure_dir(path: str) -> None:
    """Ensure directory exists"""
    os.makedirs(path, exist_ok=True)
