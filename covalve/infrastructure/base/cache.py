from abc import ABC, abstractmethod
from typing import Any

class CacheBase(ABC):
    @abstractmethod
    async def get(self, key:str) -> str | None: ...

    @abstractmethod
    async def set(self, key: str, value: Any) -> None: ...
    
    @abstractmethod
    async def delete(self, key: str) -> None: ...