"""Configuration loader for AURA project."""
import os
import yaml
from pathlib import Path
from typing import Any, Dict

class ConfigLoader:
    """Loads and manages configuration from YAML file."""
    
    def __init__(self, config_path: str = "settings/config.yaml"):
        """
        Initialize the configuration loader.
        
        Args:
            config_path: Path to the configuration YAML file
        """
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please copy 'config.example.yaml' to 'config.yaml' and fill in your values."
            )
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f) or {}
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path: Path to the config value (e.g., 'api_keys.google_genai')
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_api_key(self, service: str) -> str:
        """
        Get an API key for a specific service.
        
        Args:
            service: Name of the service (e.g., 'google_genai')
            
        Returns:
            API key
            
        Raises:
            ValueError: If API key is not found or is placeholder
        """
        api_key = self.get(f'api_keys.{service}')
        
        if not api_key:
            raise ValueError(f"API key for '{service}' not found in configuration")
        
        if "YOUR_" in api_key.upper() or "HERE" in api_key.upper():
            raise ValueError(
                f"API key for '{service}' appears to be a placeholder. "
                f"Please update your config.yaml with actual credentials."
            )
        
        return api_key
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get the full configuration dictionary."""
        return self._config


# Create a global instance
config = ConfigLoader()
