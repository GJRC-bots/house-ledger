from __future__ import annotations
import os
import json
from typing import Dict, Any

from .base import StorageBase

def _ensure_file(path: str, default_payload: Dict[str, Any]) -> None:
    if not os.path.exists(path):
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
    def __init__(self, *, config_path: str, scores_path: str):
        self._config_path = config_path
        self._scores_path = scores_path

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
