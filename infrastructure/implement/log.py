from infrastructure.base.log import LogBase
from runtime.models.logs import StateLog

class LogClient(LogBase):
    async def state_log(self, ctx: StateLog): 
        raise NotImplementedError("Log client not implemented yet")