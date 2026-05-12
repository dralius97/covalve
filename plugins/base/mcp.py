from abc import ABC, abstractmethod
from typing import Any

class MCPBase(ABC):
    @abstractmethod
    async def retrieve(self, tool_name: str) -> dict[str, Any]: ...