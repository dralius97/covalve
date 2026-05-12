from abc import ABC, abstractmethod
from runtime.executor.schema import DataContent, BackgroundUnit

class StorageBase(ABC):
    @abstractmethod
    async def save_conv(self, content:DataContent):...

    @abstractmethod
    async def retrive_conv(self, session_id:str) -> BackgroundUnit:...