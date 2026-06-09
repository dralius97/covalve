from datetime import datetime
from pydantic import BaseModel, ConfigDict
from dataclasses import dataclass
from typing import Optional, Any
from covalve.runtime.models.metadata import RuntimeMetadata, ContentUnit
from covalve.runtime.models.io import OutputSchema
from covalve.runtime.models.infra import BackgroundUnit, ContentBlock
from covalve.runtime.models.schema import CoreSchema
from covalve.infrastructure.contract import InfrastructureRegistry
from enum import Enum

class STOP(str,Enum):
    INVALID_EVENT =  "INVALID_EVENT"
    HANDLER_ERROR = "HANDLER_ERROR"
    INTERCEPTOR_ERROR = "INTERCEPTOR_ERROR"

class ActiveHook(BaseModel):
    observer: dict
    interceptor:dict
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
    tool_list: Optional[dict[int, list[dict]]] = None
    tools_data: Optional[dict[str, list[ContentBlock]]] = None
    executed_tools: ExecutedTools = ExecutedTools()
    last_error_emitted: Optional[str] = None
    error: Optional[dict] = None
    response: Optional[OutputSchema] = None
    summarize: Optional[str] = None
    fallback_content: Optional[list[ContentUnit]] = None
    traceId: str
    is_clarification: bool = False
    guardrail_rejection: Optional[str] = None
    local: Optional[dict[str,Any]] = None


class ReturnSchema(BaseModel):
    event: str
    context: PipelineContext

@dataclass
class SchemaCollections:
    core_schema: CoreSchema
    tools_schema: Optional[dict] = None

class ArgsCtx(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    state: str
    context: PipelineContext
    schema_colls: SchemaCollections

class PipelineConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    dependencies : Optional[InfrastructureRegistry] = None
    add_handlers: Optional[dict[str,Any]] = None
    overrides: Optional[dict[str,Any]] = None
    tools_schema: Optional[dict[str,Any]] = None
