from plugins.base.mcp import MCPBase
from runtime.schema.schema import MCPResponse, MCPContent

class MCPClient(MCPBase):
    async def retrieve(self, tool_name:str, metadata:MCPContent) -> MCPResponse:
        raise NotImplementedError("MCP client not implemented yet")