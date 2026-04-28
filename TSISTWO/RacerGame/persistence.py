from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SETTINGS_FILE = Path("settings.json")
LEADERBOARD_FILE = Path("leaderboard.json")

DEFAULT_SETTINGS: dict[str, Any] = {
    "sound": True,
    "car_color": "red",
    "difficulty": "normal",
    "target_distance": 5000,
    "difficulty_profiles": {
        "easy": {
            "enemy_speed_base": 180,
            "enemy_spawn_interval": 1.2,
            "obstacle_spawn_interval": 2.0,
            "coin_spawn_interval": 0.9,
            "powerup_spawn_interval": 7.5,
        },
        "normal": {
            "enemy_speed_base": 220,
            "enemy_spawn_interval": 1.0,
            "obstacle_spawn_interval": 1.7,
            "coin_spawn_interval": 0.8,
            "powerup_spawn_interval": 6.5,
        },
        "hard": {
            "enemy_speed_base": 260,
            "enemy_spawn_interval": 0.85,
            "obstacle_spawn_interval": 1.4,
            "coin_spawn_interval": 0.75,
            "powerup_spawn_interval": 6.0,
        },
    },
}


def _deep_merge(defaults: dict[str, Any], loaded: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = dict(defaults)
    for key, default_value in defaults.items():
        if key not in loaded:
            continue
        loaded_value = loaded[key]
        if isinstance(default_value, dict) and isinstance(loaded_value, dict):
            merged[key] = _deep_merge(default_value, loaded_value)
        else:
            merged[key] = loaded_value
    return merged


def load_settings(file_path: Path = SETTINGS_FILE) -> dict[str, Any]:
    if not file_path.exists():
        save_settings(DEFAULT_SETTINGS, file_path)
        return dict(DEFAULT_SETTINGS)

    try:
        with file_path.open("r", encoding="utf-8") as source:
            payload = json.load(source)
        if not isinstance(payload, dict):
            raise ValueError("settings.json root should be object")
        merged = _deep_merge(DEFAULT_SETTINGS, payload)
        return merged
    except (json.JSONDecodeError, OSError, ValueError):
        save_settings(DEFAULT_SETTINGS, file_path)
        return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict[str, Any], file_path: Path = SETTINGS_FILE) -> None:
    with file_path.open("w", encoding="utf-8") as target:
        json.dump(settings, target, indent=2)


def _normalize_name(raw_name: Any) -> str:
    cleaned = str(raw_name).strip()
    return (cleaned or "Player")[:20]


def _result_key(row: dict[str, Any]) -> tuple[int, int]:
    return int(row.get("score", 0)), int(row.get("distance", 0))


def _deduplicate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best_by_name: dict[str, dict[str, Any]] = {}
    for row in rows:
        normalized = {
            "name": _normalize_name(row.get("name", "Player")),
            "score": int(row.get("score", 0)),
            "distance": int(row.get("distance", 0)),
        }
        current = best_by_name.get(normalized["name"])
        if current is None or _result_key(normalized) > _result_key(current):
            best_by_name[normalized["name"]] = normalized

    unique_rows = list(best_by_name.values())
    unique_rows.sort(key=_result_key, reverse=True)
    return unique_rows[:10]


# End of persistence helpers


def load_leaderboard(file_path: Path = LEADERBOARD_FILE) -> list[dict[str, Any]]:
    if not file_path.exists():
        save_leaderboard([], file_path)
        return []

    try:
        with file_path.open("r", encoding="utf-8") as source:
            payload = json.load(source)
        if not isinstance(payload, list):
            raise ValueError("leaderboard should be list")
        sanitized: list[dict[str, Any]] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            name = _normalize_name(item.get("name", "Player"))
            score = int(item.get("score", 0))
            distance = int(item.get("distance", 0))
            sanitized.append({"name": name, "score": score, "distance": distance})
        unique_rows = _deduplicate_rows(sanitized)
        if unique_rows != sanitized[:10]:
            save_leaderboard(unique_rows, file_path)
        return unique_rows
    except (json.JSONDecodeError, OSError, ValueError):
        save_leaderboard([], file_path)
        return []


def save_leaderboard(rows: list[dict[str, Any]], file_path: Path = LEADERBOARD_FILE) -> None:
    top_ten = _deduplicate_rows(rows)
    with file_path.open("w", encoding="utf-8") as target:
        json.dump(top_ten, target, indent=2)


def add_leaderboard_entry(name: str, score: int, distance: int, file_path: Path = LEADERBOARD_FILE) -> list[dict[str, Any]]:
    rows = load_leaderboard(file_path)
    normalized_name = _normalize_name(name)
    new_entry = {"name": normalized_name, "score": int(score), "distance": int(distance)}

    replaced = False
    for idx, row in enumerate(rows):
        if row.get("name") != normalized_name:
            continue
        if _result_key(new_entry) > _result_key(row):
            rows[idx] = new_entry
        replaced = True
        break

    if not replaced:
        rows.append(new_entry)

    save_leaderboard(rows, file_path)
    return load_leaderboard(file_path)
