from abc import ABC, abstractmethod
from runtime.models.io import MainLLMResponse 
from runtime.models.context import RuntimeMetadata

class LLMBase(ABC):
    
    @abstractmethod
    async def analyze(self, prompt: str) -> RuntimeMetadata: ...
    
    @abstractmethod
    async def generate(self, prompt: str) -> MainLLMResponse: ...