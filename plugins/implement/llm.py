from plugins.base.llm import LLMBase
from runtime.schema.schema import MainLLMResponse, RuntimeMetadata
class LlmClient(LLMBase):
    async def analyze(self, prompt) -> RuntimeMetadata:
        raise NotImplementedError("LLM analyze not implemented yet")
    
    async def generate(self, prompt) -> MainLLMResponse:
        raise NotImplementedError("LLM generate not implemented yet")