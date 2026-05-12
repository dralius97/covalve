from abc import ABC, abstractmethod
from runtime.schema.schema import MainLLMResponse, RuntimeMetadata

class LLMBase(ABC):
    
    @abstractmethod
    async def analyze(self, prompt: str) -> RuntimeMetadata: ...
    
    @abstractmethod
    async def generate(self, prompt: str) -> MainLLMResponse: ...