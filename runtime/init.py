from runtime.models.context import PipelineConfig
from infrastructure.registry import deps
from runtime.registry import handlersRegistry
from runtime.hook import hooks
from collections import defaultdict


def init_handlers(schema:dict, config: PipelineConfig = None) -> dict:
    available_nodes = set(schema["states"].keys())
    handler_collection = {}
    for node in available_nodes:
        if node in handlersRegistry:
            handler_collection[node] = handlersRegistry[node]
    if config and config.overrides:
        for key, factory in config.overrides.items():

            handler_collection[key] = factory
    if config and config.add_handlers:
        for key, factory in config.add_handlers.items():
            if key in handler_collection:
                raise ValueError(f"add_handler conflict with existing: {key}")
            handler_collection[key] = factory
    missing = set(schema["states"].keys()) - set(handler_collection.keys())
    if missing:
        raise ValueError(f"missing handlers: {missing}")
    
    return {
        node: factory(deps) for node, factory in handler_collection.items()
    }

def init_hooks(schema: dict):
    states:dict = schema["states"]
    available_nodes = set(states.keys())

    active_hook = {
        "observer": defaultdict(lambda: defaultdict(list)),
        "interceptor": defaultdict(lambda: defaultdict(list))
    }
    for config, fn in hooks.observer_collection:
        nodes = config.nodes
        hook_on = config.on
        for node in nodes:
            if node not in available_nodes:
                raise ValueError(f"invalid nodes: Node {node} is not available on schema.")
            active_hook["observer"][hook_on][node].append(fn)

    for config, fn in hooks.interceptor_collection:
        node = config.node
        hook_on = config.on
        on_false = config.on_false
        if node not in available_nodes:
            raise ValueError(f"invalid nodes: Node {node} is not available on schema.")
        
        available_event = set(states[node]["transitions"].keys())
        if on_false not in available_event:
            raise ValueError(f"invalid event: Event {on_false} is not available on {node} transitions.")
        
        interceptor_data = (on_false, fn)
        active_hook["interceptor"][hook_on][node].append(interceptor_data)

    return active_hook

def init_tools_schema(tools_schema:dict) -> None:
    if tools_schema is None:
        raise ValueError("tools_schema is required when using TOOLS_MAPPER or EXECUTE_TOOLS nodes.")
    for  tool_name,val in tools_schema.items():
        priority = val["priority"]
        skippable = val["skippable"]
        intent = val["intent"]
        
        if not all([isinstance(priority, int),isinstance(skippable, bool),isinstance(intent, list)]) or len(intent) < 1:
            raise ValueError(
                f"Invalid tools_schema for '{tool_name}': "
                f"'priority' must be int, "
                f"'skippable' must be bool, "
                f"'intent' must contain at least one item."
            )