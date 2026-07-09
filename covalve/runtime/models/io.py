from pydantic import BaseModel
from typing import Optional, Any
from enum import Enum
from covalve.runtime.models.metadata import ContentUnit
from covalve.runtime.models.infra import ContentBlock

class OutputStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    CLARIFICATION = "clarification"

class OutputSchema(BaseModel):
    text: str
    attachment: Optional[list[ContentBlock]] = None
    status: OutputStatus
    traceId: str

class MainLLMResponse(BaseModel):
    text: str
    summarize: str

class DataContent(BaseModel):
    session_id: str
    metadata: list[ContentUnit] = []
    user: str
    assistance: str = ""
    traceId: str
    summarize: str | None = None
    data: dict[str, Any] | list[Any] | None = None

class GenerateCondition(BaseModel):
    is_clarification: bool
    is_rejected: bool