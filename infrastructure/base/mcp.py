from abc import ABC, abstractmethod
from runtime.models.context import RuntimeMetadata 
from runtime.models.infra import MCPResponse

class MCPBase(ABC):
    @abstractmethod
    async def retrieve(self, tool_name: str, metadata:RuntimeMetadata) -> MCPResponse: ...