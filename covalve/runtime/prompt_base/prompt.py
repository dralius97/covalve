from covalve.runtime.models.metadata import RuntimeMetadata
from covalve.runtime.models.io import MainLLMResponse
import json
from pathlib import Path


_MAIN_LLM_SYSTEM = """You are an analytical assistant. Your job is to answer the user's question based strictly on the provided data.

## Rules
- Answer only based on the data provided, do not fabricate information
- If data is insufficient to answer, say so clearly
- Be concise and accurate
- Use the same language as the user's question
"""


class BasePrompt:
    def __init__(self):
        self.BASE_DIR = Path(__file__).parent
        self._analyzer = ""
        self._main_llm = _MAIN_LLM_SYSTEM
        self.init()

    def init(self):
        analyzer_schema = RuntimeMetadata.model_json_schema()
        main_llm_schema = MainLLMResponse.model_json_schema()
        with open(self.BASE_DIR / 'query_analyze_prompt.txt') as f:
            _base_prompt = f.read() 

        self._analyzer = f"""
            {_base_prompt}

            ## Output Schema
            Respond ONLY in JSON matching this exact schema, no preamble, no markdown fences:
            {json.dumps(analyzer_schema, indent=2)}
            """
        self._main_llm = f"""
            {_MAIN_LLM_SYSTEM}

            ## Output Schema
            Respond ONLY in JSON matching this exact schema, no preamble, no markdown fences:
            {json.dumps(main_llm_schema, indent=2)}
        """
        
    def get_analyze_prompt(self) -> str:
        analyzer:str = self._analyzer
        return analyzer

    def get_main_llm_system(self) -> str:
        main_llm:str = self._main_llm
        return main_llm

Prompt = BasePrompt()