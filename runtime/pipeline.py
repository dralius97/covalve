from runtime.models.context import PipelineConfig
from infrastructure.registry import deps
from runtime.registry import handlersRegistry
from runtime.validator.graph_traversal import validate_graph
from jsonSchema.jsonRegistry import core_schema
from runtime.engine import create_engine

base_schema = core_schema

def pipeline(schema:dict, config:PipelineConfig = None):
    if not validate_graph(schema):
        raise ValueError("schema.json does not valid, might be there hanging nodes or unreachable nodes")
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
    
    active_handler = {
        node: factory(deps) for node, factory in handler_collection.items()
    }

    engine = create_engine(schema, active_handler, deps)    

    return engine
