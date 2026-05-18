from plugins.base.log import LogBase
from runtime.schema.schema import StateLog

class LogClient(LogBase):
    async def state_log(self, ctx: StateLog): 
        raise NotImplementedError("MCP client not implemented yet")