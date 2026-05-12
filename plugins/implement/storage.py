from plugins.base.storage import StorageBase

class StorageClient(StorageBase):
    async def save_conv(self, content):
        raise NotImplementedError("Storage save_conv not implemented yet")
    
    async def retrive_conv(self, session_id):
        raise NotImplementedError("Storage retrive_conv not implemented yet")