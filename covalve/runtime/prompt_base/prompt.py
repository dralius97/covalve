from covalve.runtime.models.metadata import RuntimeMetadata
import json


class BasePrompt:
    def __init__(self):
        self._analyzer = ""
        self.init()

    def init(self):
        analyzer_schema = RuntimeMetadata.model_json_schema()
        with open('query_analyze_prompt.txt') as f:
            _base_prompt = f.read() 

        self._analyzer = f"""
            {_base_prompt}

            ## Output Schema
            Respond ONLY in JSON matching this exact schema, no preamble, no markdown fences:
            {json.dumps(analyzer_schema, indent=2)}
            """
        
    def get_analyze_prompt(self) -> str:
        analyzer:str = self._analyzer
        return analyzer
    
Prompt = BasePrompt()