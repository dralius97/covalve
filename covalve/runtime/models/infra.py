from pydantic import BaseModel 
from covalve.runtime.models.metadata import ContentUnit
from typing import Literal, Union, Optional, Any

class ConvData(BaseModel):
    user: str
    assistance: str
    metadata: list[ContentUnit]
    data: dict

class BackgroundUnit(BaseModel):
    summarize : str
    conversation : list[ConvData]

class TextContent(BaseModel):
    type: Literal["text"]
    text: str

class ImageContent(BaseModel):
    type: Literal["image"]
    data: str
    mimeType: str

class AudioContent(BaseModel):
    type: Literal["audio"]
    data: str
    mimeType: str

class EmbeddedResource(BaseModel):
    type: Literal["resource"]
    resource: dict[str, Any]

ContentBlock = Union[TextContent, ImageContent, AudioContent, EmbeddedResource]

class MCPResponse(BaseModel):
    content: list[ContentBlock]
    structuredContent: Optional[dict[str, Any]] = None
    isError: bool = False

class GuardRailResponse(BaseModel):
    reason: Optional[str] = None
    is_rejected: bool
