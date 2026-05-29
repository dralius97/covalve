from abc import ABC, abstractmethod
from covalve.runtime.models.logs import StateLog

class LogBase(ABC):
    @abstractmethod
    async def state_log(self, ctx: StateLog):
        raise NotImplementedError("Log Client is not implemented yet")