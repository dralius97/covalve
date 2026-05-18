from abc import ABC, abstractmethod
from runtime.schema.schema import RuntimeMetadata, MCPResponse
from typing import Any

class MCPBase(ABC):
    @abstractmethod
    async def retrieve(self, tool_name: str, metadata:RuntimeMetadata) -> MCPResponse: ...