from __future__ import annotations
from typing import Dict, Any, List

from storage.base import StorageBase

DEFAULT_CONFIG: Dict[str, Any] = {
    "guild_id": "",
    "mod_role_id": "",
    "house_roles": {
        "house_veridian": "",
        "feathered_host": ""
    },
    "channels": {
        "scoreboard": "",
        "review_queue": "",
        "log": ""
    },
    "weighting": {
        "enabled": False,
        "rounding": "round"
    },
    "display": {
        "channel_id": "",
        "message_id": ""
    }
}

class ConfigManager:
    def __init__(self, storage: StorageBase):
        self._storage = storage
        self._config = self._storage.load_config(default_payload=DEFAULT_CONFIG)

    @property
    def data(self) -> Dict[str, Any]:
        return self._config

    def save(self) -> None:
        self._storage.save_config(self._config)

    def set_weighting(self, enabled: bool, rounding: str) -> None:
        w = self._config.setdefault("weighting", {})
        w["enabled"] = bool(enabled)
        w["rounding"] = rounding
        self.save()

    def get_house_role_ids(self) -> Dict[str, List[str]]:
        roles = self._config.get("house_roles", {})
        result = {}
        for house, role_data in roles.items():
            if isinstance(role_data, list):
                result[house] = role_data
            elif isinstance(role_data, str) and role_data.strip():
                result[house] = [role_data.strip()]
            else:
                result[house] = []
        return result

    def get_mod_role_id(self) -> str:
        return str(self._config.get("mod_role_id") or "").strip()

    def get_display_channel_id(self) -> str:
        return str(self._config.get("display", {}).get("channel_id") or "").strip()

    def get_display_message_id(self) -> str:
        return str(self._config.get("display", {}).get("message_id") or "").strip()

    def get_log_channel_id(self) -> str:
        return str(self._config.get("channels", {}).get("log") or "").strip()

    def set_display_settings(self, channel_id: str, message_id: str) -> None:
        d = self._config.setdefault("display", {})
        d["channel_id"] = channel_id
        d["message_id"] = message_id
        self.save()
