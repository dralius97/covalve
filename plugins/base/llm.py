from abc import ABC, abstractmethod

class LLMBase(ABC):
    
    @abstractmethod
    async def analyze(self, prompt: str) -> str: ...
    
    @abstractmethod
    async def generate(self, prompt: str) -> str: ...