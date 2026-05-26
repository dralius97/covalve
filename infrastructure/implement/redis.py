from typing import Any
from infrastructure.base.redis import RedisBase

class RedisClient(RedisBase):
    async def set(self, key:str, value:Any):
        raise NotImplementedError("Redis set not implemented yet")
    
    async def get(self, key:str):
        raise NotImplementedError("Redis get not implemented yet")
    
    async def delete(self, key:str):
        raise NotImplementedError("Redis delete not implemented yet")