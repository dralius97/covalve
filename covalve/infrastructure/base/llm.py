from abc import ABC, abstractmethod
from covalve.runtime.models.io import MainLLMResponse,GenerateCondition 
from covalve.runtime.models.context import RuntimeMetadata

class LLMBase(ABC):
    
    @abstractmethod
    async def analyze(self, system: str, user: str) -> RuntimeMetadata: ...
    
    @abstractmethod
    async def generate(self, system: str, user: str, condition: GenerateCondition) -> MainLLMResponse: ...