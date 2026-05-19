from pydantic import BaseModel, field_validator
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
    OUT_OF_CONTEXT = "outofcontext"
    CONVERSATION = "conversation"

class MainLLMResponse(BaseModel):
    text: str
    summarize: str

class ContentUnit(BaseModel):
    intent: str
    composition_context: str
    confidence: float

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        return round(max(0.0, min(1.0, float(v))), 2)

    @field_validator('intent')
    @classmethod
    def validate_intent(cls, v: str) -> str:
        valid = {intent.value for intent in QueryIntent}
        if v.lower() not in valid:
            raise ValueError(f"invalid intent: {v}. must be one of {valid}")
        return v.lower()

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

class PipelineContext(BaseModel):
    query: str
    session_id: str
    current_time: datetime
    is_error: bool = False
    background: Optional[BackgroundUnit] = None
    metadata: Optional[RuntimeMetadata] = None
    tool_list: Optional[dict[int, list[str]]] = None
    tools_data: Optional[dict[str, list[MCPContent]]] = None
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


class DataContent(BaseModel):
    session_id: str
    metadata: list[ContentUnit] = []
    user: str
    assistance: str = ""
    traceId: str
    summarize: str | None = None
    data: dict[str, Any] | list[Any] | None = None

class MCPContent(BaseModel):
    type: str  # "text", "image", dll
    text: str

class MCPResponse(BaseModel):
    content: list[MCPContent]
    isError: bool = False

class StateLog(BaseModel):
    session_id: str 
    traceId: str
    current_state: str 
    event: str 
    next_state: str 
    time_executed: datetime
    duration_ms: float
    error: Optional[str] = None