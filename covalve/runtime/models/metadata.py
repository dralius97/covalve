from pydantic import BaseModel, field_validator
from enum import Enum
from typing import Any, Optional
class QueryIntent(str, Enum):
    EXPLAIN      = "explain"
    LOOKUP       = "lookup"
    OPERATE      = "operate"
    VALIDATE     = "validate"
    COMPARE      = "compare"
    SOURCE       = "source"
    CONVERSATION = "conversation"
    
class FilterOperator(str, Enum):
    EQ          = "eq"
    NEQ         = "neq"
    GT          = "gt"
    GTE         = "gte"
    LT          = "lt"
    LTE         = "lte"
    IN          = "in"
    NOT_IN      = "not_in"
    LIKE        = "like"
    IS_NULL     = "is_null"
    IS_NOT_NULL = "is_not_null"

class Metric(str, Enum):
    COUNT = "count"
    SUM   = "sum"
    AVG   = "avg"
    MAX   = "max"
    MIN   = "min"

class AssertionKind(str, Enum):
    THRESHOLD = "threshold"
    COMPLIANCE = "compliance"
    EXISTENCE = "existence"
    EQUALITY = "equality"
    STATUS = "status"
    UNCLASSIFIED = "unclassified"

class FilterUnit(BaseModel):
    attribute: str
    value: Any
    operator: FilterOperator

class EntityType(str, Enum):
    SUBJECT = "subject"
    OBJECT  = "object"
    DOMAIN  = "domain"
class EntityUnit(BaseModel):
    type: EntityType
    value: str

class AssertionUnit(BaseModel):
    kind: AssertionKind
    surface: str
    expected: bool

class ContentUnit(BaseModel):
    intent: QueryIntent
    composition_context: str
    confidence: float
    metric: Optional[Metric] = None
    entities: list[EntityUnit] = []
    filters: list[FilterUnit] = []
    assertions: list[AssertionUnit] = []
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
        return QueryIntent(v.lower())
    
class RuntimeMetadata(BaseModel):
    content: list[ContentUnit]
    raw_query: str