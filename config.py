#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Management Module
Manages application configuration, including API settings, interface settings, etc.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Configuration Manager class"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize configuration manager
        
        Args:
            config_file: Configuration file name
        """
        self.config_file = Path.home() / ".git_ai_commit" / config_file
        self.config_file.parent.mkdir(exist_ok=True)
        self._config = self._load_default_config()
        self.load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        default_prompt = """You are a professional software engineer.
Carefully review the provided context and code changes that are about to be committed to the Git repository.
Generate a commit message for these changes.
The commit message must use imperative mood (e.g. "fix" not "fixed").
The commit message format should be as follows:
Use the following prefixes:
- **fix**
- **feat**
- **build**
- **chore**
- **ci**
- **docs**
- **style**
- **refactor**
- **perf**
- **test**
Just reply with the commit message itself, do not include quotes, comments, or additional explanations!
Examples:
`fix null pointer exception during user login`
`feat add user registration endpoint`
`refactor optimize order processing logic`"""

        return {
            "api": {
                "url": "https://api.kenhong.com/v1",
                "api_key": "",
                "model": "glm-4-flash",
                "prompt": default_prompt
            },
            "ui": {
                "window_width": 400,
                "window_height": 550,
                "last_repo_path": ""
            },
            "git": {
                "max_diff_lines": 200,
                "auto_stage": False
            }
        }
    
    def load_config(self) -> None:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge configuration, keep default values
                    self._merge_config(self._config, loaded_config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Failed to load configuration file, using default configuration: {e}")
    
    def save_config(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Failed to save configuration file: {e}")
    
    def _merge_config(self, default: Dict, loaded: Dict) -> None:
        """Recursively merge configuration"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(default[key], dict) and isinstance(value, dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
    
    def get(self, key_path: str, default=None) -> Any:
        """
        Get configuration value
        
        Args:
            key_path: Configuration key path, e.g. 'api.url'
            default: Default value
            
        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Set configuration value
        
        Args:
            key_path: Configuration key path, e.g. 'api.url'
            value: Configuration value
        """
        keys = key_path.split('.')
        config = self._config
        
        # Navigate to last level
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set value
        config[keys[-1]] = value
    
    def get_api_config(self) -> Dict[str, str]:
        """Get API configuration"""
        return {
            "url": self.get("api.url", ""),
            "api_key": self.get("api.api_key", ""),
            "model": self.get("api.model", "glm-4-flash"),
            "prompt": self.get("api.prompt", "")
        }
    
    def set_api_config(self, url: str, api_key: str, model: str, prompt: str = None) -> None:
        """Set API configuration"""
        self.set("api.url", url)
        self.set("api.api_key", api_key)
        self.set("api.model", model)
        if prompt is not None:
            self.set("api.prompt", prompt)
        self.save_config()
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI configuration"""
        return {
            "window_width": self.get("ui.window_width", 800),
            "window_height": self.get("ui.window_height", 600),
            "last_repo_path": self.get("ui.last_repo_path", "")
        }
    
    def set_ui_config(self, **kwargs) -> None:
        """Set UI configuration"""
        for key, value in kwargs.items():
            self.set(f"ui.{key}", value)
        self.save_config()
    
    def get_git_config(self) -> Dict[str, Any]:
        """Get Git configuration"""
        return {
            "max_diff_lines": self.get("git.max_diff_lines", 200),
            "auto_stage": self.get("git.auto_stage", False)
        }


# Global configuration manager instance
config_manager = ConfigManager()


if __name__ == "__main__":
    # Test configuration manager
    print("Testing configuration manager...")
    
    # Test default configuration
    print(f"Default API URL: {config_manager.get('api.url')}")
    print(f"Default window size: {config_manager.get('ui.window_width')}x{config_manager.get('ui.window_height')}")
    
    # Test setting and getting
    config_manager.set("api.api_key", "test-key")
    print(f"API Key after setting: {config_manager.get('api.api_key')}")
    
    # Test API configuration
    api_config = config_manager.get_api_config()
    print(f"API configuration: {api_config}")
    
    print("Configuration manager test completed")
