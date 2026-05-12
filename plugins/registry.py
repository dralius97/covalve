from plugins.implement.redis import RedisClient
from plugins.implement.llm import LlmClient
from plugins.implement.storage import StorageClient

redis = RedisClient()
callLLM = LlmClient()
storage = StorageClient()