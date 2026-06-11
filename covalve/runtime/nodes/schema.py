from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from enum import Enum
from covalve.runtime.models.metadata import RuntimeMetadata, ContentUnit
from covalve.runtime.models.infra import BackgroundUnit, ContentBlock
from covalve.runtime.models.io import OutputSchema
from covalve.runtime.models.context import ExecutedTools


class ReadOnlyFields(BaseModel):
    query: str
    session_id: str
    current_time: datetime
    traceId: str


class ConversationFields(BaseModel):
    background: Optional[BackgroundUnit] = None
    metadata: Optional[RuntimeMetadata] = None


class ToolsFields(BaseModel):
    tools_data: Optional[dict[str, list[ContentBlock]]] = None
    executed_tools: ExecutedTools = ExecutedTools()
    tool_list: Optional[dict[int, list[dict]]] = None


class ResponseFields(BaseModel):
    response: Optional[OutputSchema] = None
    summarize: Optional[str] = None
    is_clarification: bool = False
    fallback_content: Optional[list[ContentUnit]] = None
    guardrail_rejection: Optional[str] = None


class ErrorFields(BaseModel):
    error: Optional[dict] = None
    last_error_emitted: Optional[str] = None


class ReturnContext(BaseModel):
    event: str
    local: Optional[dict[str, Any]] = None
    errors: Optional[ErrorFields] = None
    response: Optional[ResponseFields] = None
    tools: Optional[ToolsFields] = None

class NodeContext(BaseModel):
    readonly: ReadOnlyFields
    conversation: Optional[ConversationFields] = None
    tools: Optional[ToolsFields] = None
    response: Optional[ResponseFields] = None
    errors: Optional[ErrorFields] = None
    local: Optional[dict[str, Any]] = None


class ReadsList(str,Enum):
    ERROR = "error"
    RESPONSE = "response"
    TOOLS = "tools"
    CONV = "conversation"

class NodesConfig(BaseModel):
    name: str
    reads: list[ReadsList]