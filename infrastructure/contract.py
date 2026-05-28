
from typing import Optional
from dataclasses import dataclass
from infrastructure.base.storage import StorageBase
from infrastructure.base.llm import LLMBase
from infrastructure.base.log import LogBase
from infrastructure.base.mcp import MCPBase
from infrastructure.base.redis import RedisBase
from infrastructure.base.guardrails import GuardrailBase


@dataclass
class InfrastructureRegistry:
    llm: Optional[LLMBase] = None
    storage: Optional[StorageBase] = None
    redis: Optional[RedisBase] = None
    mcp: Optional[MCPBase] = None
    log: Optional[LogBase] = None
    guardrail: Optional[GuardrailBase] = None
    tools_map: Optional[dict] = None
