"""
Configuration & Settings Manager for TempNumber
"""

import json
import os
from typing import Dict, Any

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.tempnumber_config.json")
DEFAULT_BASE_URL = "https://sever1.tempxapi.com"
DEFAULT_USER_AGENT = "okhttp/4.9.2"


class TempNumberConfig:
    """Settings and state persistence for TempNumber Client."""

    def __init__(self, filepath: str = DEFAULT_CONFIG_PATH):
        self.filepath = filepath
        self.defaults = {
            "base_url": DEFAULT_BASE_URL,
            "user_agent": DEFAULT_USER_AGENT,
            "default_country": "United States",
            "active_number": "",
            "poll_interval": 3,
            "mock_mode": False
        }
        self.data = self.load()

    def load(self) -> Dict[str, Any]:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    cfg = self.defaults.copy()
                    cfg.update(saved)
                    return cfg
            except Exception:
                pass
        return self.defaults.copy()

    def save(self) -> bool:
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            return True
        except Exception:
            return False

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default if default is not None else self.defaults.get(key))

    def set(self, key: str, value: Any):
        self.data[key] = value

    def reset(self):
        self.data = self.defaults.copy()
        self.save()
