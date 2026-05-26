from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class StateLog(BaseModel):
    session_id: str 
    traceId: str
    current_state: str 
    event: str 
    next_state: str 
    time_executed: datetime
    duration_ms: float
    error: Optional[str] = None
