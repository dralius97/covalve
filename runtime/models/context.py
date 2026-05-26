from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Any
from runtime.models.metadata import RuntimeMetadata, ContentUnit
from runtime.models.io import OutputSchema
from runtime.models.infra import BackgroundUnit, MCPContent

class ExecutedTools(BaseModel):
    success_tools: list[str] = []
    skipped_tools: list[str] = []

class PipelineContext(BaseModel):
    query: str
    session_id: str
    current_time: datetime
    is_error: bool = False
    background: Optional[BackgroundUnit] = None
    metadata: Optional[RuntimeMetadata] = None
    tool_list: Optional[dict[int, list[str]]] = None
    tools_data: Optional[dict[str, list[MCPContent]]] = None
    executed_tools: ExecutedTools = ExecutedTools()
    last_error_emitted: Optional[str] = None
    error: Optional[dict] = None
    response: Optional[OutputSchema] = None
    summarize: Optional[str] = None
    fallback_content: Optional[list[ContentUnit]] = None
    traceId: str
    is_clarification: bool = False


class ReturnSchema(BaseModel):
    event: str
    context: PipelineContext

class ArgsCtx(BaseModel):
    state: str
    context: PipelineContext

class PipelineConfig(BaseModel):
    add_handlers: Optional[dict[str,Any]] = None
    overrides: Optional[dict[str,Any]] = None

