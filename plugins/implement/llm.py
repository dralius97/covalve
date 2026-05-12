from plugins.base.llm import LLMBase

class LlmClient(LLMBase):
    async def analyze(self, prompt):
        raise NotImplementedError("LLM analyze not implemented yet")
    
    async def generate(self, prompt):
        raise NotImplementedError("LLM generate not implemented yet")