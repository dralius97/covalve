from infrastructure.implement.redis import RedisClient
from infrastructure.implement.llm import LlmClient
from infrastructure.implement.storage import StorageClient
from infrastructure.implement.mcp import MCPClient
from infrastructure.implement.log import LogClient
from infrastructure.contract import  InfrastructureRegistry



deps = InfrastructureRegistry(
    llm=LlmClient(),
    log=LogClient(),
    mcp=MCPClient(),
    storage=StorageClient(),
    redis=RedisClient()
)