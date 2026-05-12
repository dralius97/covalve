from plugins.base.storage import StorageBase
from runtime.executor.schema import BackgroundUnit,DataContent

class StorageClient(StorageBase):
    async def save_conv(self, content:DataContent):
        raise NotImplementedError("Storage save_conv not implemented yet")
    
    async def retrive_conv(self, session_id:str) -> BackgroundUnit | None:
        raise NotImplementedError("Storage retrive_conv not implemented yet")