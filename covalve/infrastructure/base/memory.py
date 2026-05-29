from abc import ABC, abstractmethod
from covalve.runtime.models.io import DataContent 
from covalve.runtime.models.infra import BackgroundUnit

class MemoryStoreBase(ABC):
    @abstractmethod
    async def save_conv(self, content:DataContent):...

    @abstractmethod
    async def retrieve_conv(self, session_id:str) -> BackgroundUnit | None:...