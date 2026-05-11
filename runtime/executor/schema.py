from pydantic import BaseModel
from enum import Enum
from typing import Optional, Any
from datetime import datetime


class QueryIntent(str, Enum):
    EXPLAIN  = "explain"
    LOOKUP   = "lookup"
    OPERATE  = "operate"
    VALIDATE = "validate"
    COMPARE  = "compare"
    SOURCE = "source"

class ContentUnit(BaseModel):
    intent: str
    composition_context: str
    confidence: float

class ConvData(BaseModel):
    user: str
    assistance: str
    metadata: list[ContentUnit]
    data: dict

class BackgroundUnit(BaseModel):
    summarize : str
    conversation : list[ConvData]

class RuntimeMetadata(BaseModel):
    content: list[ContentUnit]
    raw_query: str


class PipelineContext(BaseModel):
    query: str
    session_id: str
    current_time: datetime
    is_error: bool = False
    background: Optional[BackgroundUnit] = None
    metadata: Optional[RuntimeMetadata] = None
    tool_list: Optional[dict[int, list[str]]] = None
    tools_data: Optional[dict[str, Any]] = None
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


class OutputStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    CLARIFICATION = "clarification"

class AttachmentUnit(BaseModel):
    type: str
    data: str

class OutputSchema(BaseModel):
    text: str
    attachment: Optional[list[AttachmentUnit]] = None
    status: OutputStatus
    traceId: str