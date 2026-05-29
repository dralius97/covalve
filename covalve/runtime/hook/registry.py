from typing import Callable
from pydantic import BaseModel
from enum import Enum

class HookOn(str, Enum):
    ENTER = "enter"
    EXIT = "exit"

class ObserverConfig(BaseModel):
    nodes: list[str]
    on: HookOn

class InterceptorConfig(BaseModel):
    node: str
    on: HookOn
    on_false: str

class HookRegistry:
    def __init__(self):
        self._observer_registry: list[tuple[ObserverConfig, Callable]] = []
        self._interceptor_registry: list[tuple[InterceptorConfig, Callable]] = []

    def observer(self, nodes: list[str], on: HookOn):
        def decorator(fn: Callable):
            self._observer_registry.append((ObserverConfig(nodes=nodes, on=on), fn))
            return fn
        return decorator

    def interceptor(self, node: str, on: HookOn, on_false: str):
        def decorator(fn: Callable):
            self._interceptor_registry.append((InterceptorConfig(nodes=node, on=on, on_false=on_false), fn))
            return fn
        return decorator
    
    @property
    def observer_collection(self):
        return self._observer_registry

    @property
    def interceptor_collection(self):
        return self._interceptor_registry
    

