from pydantic import BaseModel, ConfigDict
from covalve.runtime.models.context import PipelineContext

class ReadOnlyContext(PipelineContext):
    model_config = ConfigDict(frozen=True)

class HookReturn(BaseModel):
    intercepted: bool
    to: str
    error: str
    event:str