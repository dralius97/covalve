from typing import Callable
from covalve.runtime.nodes.schema import ReturnContext, NodesConfig, ReadsList
from typing import get_type_hints

class NodesRegistry:
    def __init__(self)->None:
        self._nodes_registry: list[tuple[NodesConfig, Callable]] = []

    def handler(self, name: str, reads: list[ReadsList]):
        def decorator(fn: Callable):
            hints = get_type_hints(fn)
            if hints.get("return") is not ReturnContext:
                raise TypeError(
                    f"Custom node '{name}' must return ReturnContext, "
                    f"got {hints.get('return')}"
                )
            self._nodes_registry.append((NodesConfig(name=name, reads=reads), fn))
            return fn
        return decorator
    
    @property
    def nodes_collection(self) -> list:
        return self._nodes_registry


