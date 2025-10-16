from __future__ import annotations
from typing import Dict, Any
from abc import ABC, abstractmethod

class StorageBase(ABC):
    @abstractmethod
    def load_config(self, default_payload: Dict[str, Any]) -> Dict[str, Any]:
        ...

    @abstractmethod
    def save_config(self, payload: Dict[str, Any]) -> None:
        ...

    @abstractmethod
    def load_scores(self, default_payload: Dict[str, Any]) -> Dict[str, Any]:
        ...

    @abstractmethod
    def save_scores(self, payload: Dict[str, Any]) -> None:
        ...