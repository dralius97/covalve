from datetime import datetime
from pydantic import BaseModel, ConfigDict
from dataclasses import dataclass
from typing import Optional, Any
from runtime.models.metadata import RuntimeMetadata, ContentUnit
from runtime.models.io import OutputSchema
from runtime.models.infra import BackgroundUnit, MCPContent
from enum import Enum

class STOP(str,Enum):
    INVALID_EVENT =  "INVALID_EVENT"
    HANDLER_ERROR = "HANDLER_ERROR"
    INTERCEPTOR_ERROR = "INTERCEPTOR_ERROR"

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
    guardrail_rejection: Optional[str] = None


class ReturnSchema(BaseModel):
    event: str
    context: PipelineContext

@dataclass
class SchemaCollections:
    core_schema: dict
    tools_schema: Optional[dict] = None

class ArgsCtx(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    state: str
    context: PipelineContext
    schema: SchemaCollections

class PipelineConfig(BaseModel):
    add_handlers: Optional[dict[str,Any]] = None
    overrides: Optional[dict[str,Any]] = None
    tools_schema: Optional[dict[str,Any]] = None


class PluginsType(str,Enum):
    MIDDLEWARE =  "MIDDLEWARE"
    HANGING = "HANGING"

class PluginsOn(str,Enum):
    ENTER = "ENTER",
    EXIT = "EXIT"
class PluginsConfig(BaseModel):
    type: PluginsType
    nodes: list[str]
    on: PluginsOn
    on_false: Optional[str] = None