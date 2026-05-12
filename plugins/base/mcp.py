from abc import ABC, abstractmethod
from typing import Any

class MCPBase(ABC):
    @abstractmethod
    async def tools(self, tools:str) -> dict(name = Any):...