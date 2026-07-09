from abc import ABC, abstractmethod
from covalve.runtime.models.context import RuntimeMetadata 
from covalve.runtime.models.infra import MCPResponse, ContentBlock

class ToolClientBase(ABC):
    @abstractmethod
    async def retrieve(self, tool_name: str, metadata:RuntimeMetadata, tools_data: dict[str, list[ContentBlock]]) -> MCPResponse: ...