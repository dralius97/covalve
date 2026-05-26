from abc import ABC, abstractmethod
from runtime.models.logs import StateLog

class LogBase(ABC):
    @abstractmethod
    async def state_log(self, ctx: StateLog): ...