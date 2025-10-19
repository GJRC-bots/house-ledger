from __future__ import annotations
import os
import json
from typing import Dict, Any

from .base import StorageBase

def _ensure_file(path: str, default_payload: Dict[str, Any]) -> None:
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_payload, f, indent=2)
    else:
        # Check if file is empty or contains invalid JSON
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:  # Empty file
                    raise ValueError("Empty file")
                json.loads(content)  # Try to parse
        except (json.JSONDecodeError, ValueError):
            # File is empty or invalid, write default payload
            with open(path, "w", encoding="utf-8") as f:
                json.dump(default_payload, f, indent=2)

def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_json(path: str, payload: Dict[str, Any]) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, path)

class JsonStorage(StorageBase):
    def __init__(self, *, config_path: str, scores_path: str, season_path: str):
        self._config_path = config_path
        self._scores_path = scores_path
        self._season_path = season_path

    def load_config(self, default_payload: Dict[str, Any]) -> Dict[str, Any]:
        _ensure_file(self._config_path, default_payload)
        return _load_json(self._config_path)

    def save_config(self, payload: Dict[str, Any]) -> None:
        _save_json(self._config_path, payload)

    def load_scores(self, default_payload: Dict[str, Any]) -> Dict[str, Any]:
        _ensure_file(self._scores_path, default_payload)
        return _load_json(self._scores_path)

    def save_scores(self, payload: Dict[str, Any]) -> None:
        _save_json(self._scores_path, payload)

    def load_season_data(self, default_payload: Dict[str, Any]) -> Dict[str, Any]:
        _ensure_file(self._season_path, default_payload)
        return _load_json(self._season_path)

    def save_season_data(self, payload: Dict[str, Any]) -> None:
        _save_json(self._season_path, payload)
