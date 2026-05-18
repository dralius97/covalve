from plugins.implement.redis import RedisClient
from plugins.implement.llm import LlmClient
from plugins.implement.storage import StorageClient
from plugins.implement.mcp import MCPClient
from plugins.implement.log import LogClient

redis = RedisClient()
callLLM = LlmClient()
storage = StorageClient()
mcp = MCPClient()
log = LogClient()