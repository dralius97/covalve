from plugins.implement.redis import RedisClient
from plugins.implement.llm import LlmClient
from plugins.implement.storage import StorageClient
from plugins.implement.mcp import MCPClient
from plugins.implement.log import LogClient
from runtime.schema.schema import InfrastructureRegistry



deps = InfrastructureRegistry(
    llm=LlmClient(),
    log=LogClient(),
    mcp=MCPClient(),
    storage=StorageClient(),
    redis=RedisClient()
)