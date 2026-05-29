from pydantic import BaseModel, field_validator
from enum import Enum

class QueryIntent(str, Enum):
    EXPLAIN  = "explain"
    LOOKUP   = "lookup"
    OPERATE  = "operate"
    VALIDATE = "validate"
    COMPARE  = "compare"
    SOURCE = "source"
    CONVERSATION = "conversation"

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

class RuntimeMetadata(BaseModel):
    content: list[ContentUnit]
    raw_query: str