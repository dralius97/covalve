
from typing import Optional
from dataclasses import dataclass
from pydantic import BaseModel
from covalve.infrastructure.base.memory import MemoryStoreBase
from covalve.infrastructure.base.llm import LLMBase
from covalve.infrastructure.base.log import LogBase
from covalve.infrastructure.base.tools import ToolClientBase
from covalve.infrastructure.base.cache import CacheBase
from covalve.infrastructure.base.guardrails import GuardrailBase


@dataclass
class InfrastructureRegistry:
    llm: Optional[LLMBase] = None
    memory: Optional[MemoryStoreBase] = None
    cache: Optional[CacheBase] = None
    tools: Optional[ToolClientBase] = None
    log: Optional[LogBase] = None
    guardrail: Optional[GuardrailBase] = None