from infrastructure.base.llm import LLMBase
from runtime.models.io import MainLLMResponse 
from runtime.models.context import RuntimeMetadata
class LlmClient(LLMBase):
    async def analyze(self, prompt) -> RuntimeMetadata:
        raise NotImplementedError("LLM analyze not implemented yet")
    
    async def generate(self, prompt) -> MainLLMResponse:
        raise NotImplementedError("LLM generate not implemented yet")