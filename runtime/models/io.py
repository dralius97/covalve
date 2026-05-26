from pydantic import BaseModel
from typing import Optional, Any
from enum import Enum
from runtime.models.metadata import ContentUnit

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