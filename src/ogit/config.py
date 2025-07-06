"""Configuration management for ogit."""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .constants import CONFIG_FILENAME, DEFAULT_EDITOR, OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for ogit."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory to store config file, defaults to home directory
        """
        self.config_dir = Path(config_dir) if config_dir else Path.home()
        self.config_path = self.config_dir / CONFIG_FILENAME
        self._config = self._load_config()
        logger.debug(f"Config initialized: {self.config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                logger.debug(f"Loaded config from {self.config_path}")
                return config
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load config from {self.config_path}: {e}")
        
        # Return default config
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "default_model": None,
            "editor": os.environ.get("EDITOR", DEFAULT_EDITOR),
            "api_timeout": OLLAMA_TIMEOUT,
            "auto_add": True,
            "auto_push": False,
            "show_progress": True,
            "conventional_commits": True,
            "protected_branches": ["main", "master", "develop"],
            "max_commit_length": 72
        }
    
    def save(self) -> bool:
        """Save configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.debug(f"Saved config to {self.config_path}")
            return True
        except IOError as e:
            logger.error(f"Failed to save config to {self.config_path}: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value
        logger.debug(f"Set config {key} = {value}")
    
    # Convenience properties
    @property
    def default_model(self) -> Optional[str]:
        """Get default model."""
        return self.get("default_model")
    
    @default_model.setter
    def default_model(self, value: str) -> None:
        """Set default model."""
        self.set("default_model", value)
    
    @property
    def editor(self) -> str:
        """Get editor command."""
        return self.get("editor", DEFAULT_EDITOR)
    
    @property
    def api_timeout(self) -> int:
        """Get API timeout."""
        return self.get("api_timeout", OLLAMA_TIMEOUT)
    
    @property
    def auto_add(self) -> bool:
        """Get auto-add setting."""
        return self.get("auto_add", True)
    
    @property
    def auto_push(self) -> bool:
        """Get auto-push setting."""
        return self.get("auto_push", False)
    
    @property
    def show_progress(self) -> bool:
        """Get show progress setting."""
        return self.get("show_progress", True)
    
    @property
    def conventional_commits(self) -> bool:
        """Get conventional commits setting."""
        return self.get("conventional_commits", True)
    
    @property
    def protected_branches(self) -> list:
        """Get protected branches list."""
        return self.get("protected_branches", ["main", "master", "develop"])
    
    @property
    def max_commit_length(self) -> int:
        """Get maximum commit message length."""
        return self.get("max_commit_length", 72)


# Global config instance
_config = None


def get_config() -> Config:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def save_default_model(model: str) -> bool:
    """Save default model to config."""
    config = get_config()
    config.default_model = model
    return config.save()


def load_default_model() -> Optional[str]:
    """Load default model from config."""
    return get_config().default_model