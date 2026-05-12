from plugins.base.mcp import MCPBase
from typing import Any

class MCPClient(MCPBase):
    async def retrieve(self, tool_name: str) -> dict[str, Any]:
        raise NotImplementedError("MCP client not implemented yet")