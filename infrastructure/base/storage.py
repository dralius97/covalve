from abc import ABC, abstractmethod
from runtime.models.io import DataContent 
from runtime.models.infra import BackgroundUnit

class StorageBase(ABC):
    @abstractmethod
    async def save_conv(self, content:DataContent):...

    @abstractmethod
    async def retrieve_conv(self, session_id:str) -> BackgroundUnit | None:...