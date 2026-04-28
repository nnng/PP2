"""Settings loader and defaults for Snake game."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

DEFAULT_SETTINGS: Dict[str, Any] = {
    "window_width": 800,
    "window_height": 800,
    "grid_cols": 20,
    "grid_rows": 20,
    "snake_color": [46, 204, 113],
    "food_color": [231, 76, 60],
    "background_color": [20, 20, 20],
    "show_grid": True,
    "sound": False,
    "base_fps": 8,
    "level_up_food": 5,
    "db_host": "localhost",
    "db_port": 5432,
    "db_name": "snake_db",
    "db_user": "snake_user",
    "db_password": "your_password",
    "db_sslmode": "prefer",
}


class SettingsManager:
    """Reads and writes settings.json with safe fallbacks."""

    def __init__(self, settings_path: str | Path = "settings.json") -> None:
        self.settings_path = Path(settings_path)

    def load(self) -> Dict[str, Any]:
        if not self.settings_path.exists():
            return dict(DEFAULT_SETTINGS)

        try:
            data = json.loads(self.settings_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return dict(DEFAULT_SETTINGS)
        except (OSError, json.JSONDecodeError):
            return dict(DEFAULT_SETTINGS)

        merged = dict(DEFAULT_SETTINGS)
        merged.update(data)
        return merged

    def save(self, settings: Dict[str, Any]) -> None:
        payload = dict(DEFAULT_SETTINGS)
        payload.update(settings)
        self.settings_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
