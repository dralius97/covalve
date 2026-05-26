from infrastructure.base.storage import StorageBase
from runtime.models.infra import BackgroundUnit
from runtime.models.io import DataContent

class StorageClient(StorageBase):
    async def save_conv(self, content:DataContent):
        raise NotImplementedError("Storage save_conv not implemented yet")
    
    async def retrieve_conv(self, session_id:str) -> BackgroundUnit | None:
        raise NotImplementedError("Storage retrieve_conv not implemented yet")