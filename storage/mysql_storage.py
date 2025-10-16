from __future__ import annotations
from typing import Dict, Any

from .base import StorageBase

class MySQLStorage(StorageBase):
    def __init__(self, *, dsn: str):
        self._dsn = dsn
        # TODO: implement connector + schema

    def load_config(self, default_payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("MySQLStorage not implemented yet.")

    def save_config(self, payload: Dict[str, Any]) -> None:
        raise NotImplementedError("MySQLStorage not implemented yet.")

    def load_scores(self, default_payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("MySQLStorage not implemented yet.")

    def save_scores(self, payload: Dict[str, Any]) -> None:
        raise NotImplementedError("MySQLStorage not implemented yet.")
