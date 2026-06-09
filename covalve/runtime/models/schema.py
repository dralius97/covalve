from pydantic import BaseModel

class Transition(BaseModel):
    to: str

class StateConfig(BaseModel):
    transitions: dict[str, Transition]

class CoreSchema(BaseModel):
    INITIAL: str
    FINAL: str
    states: dict[str, StateConfig]