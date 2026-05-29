from pydantic import BaseModel 
from covalve.runtime.models.metadata import ContentUnit
from typing import Optional

class ConvData(BaseModel):
    user: str
    assistance: str
    metadata: list[ContentUnit]
    data: dict

class BackgroundUnit(BaseModel):
    summarize : str
    conversation : list[ConvData]

class MCPContent(BaseModel):
    type: str 
    text: str

class MCPResponse(BaseModel):
    content: list[MCPContent]
    isError: bool = False

class GuardRailResponse(BaseModel):
    reason: Optional[str] = None
    is_rejected: bool
