from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class ProviderResponse:
    raw_output: str


class LLMProvider(ABC):
    def __init__(self, timeout_seconds: float = 30.0) -> None:
        self._timeout_seconds = timeout_seconds

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    def timeout_seconds(self) -> float:
        return self._timeout_seconds

    @abstractmethod
    async def decode_brief(self, text: str) -> ProviderResponse:
        raise NotImplementedError
