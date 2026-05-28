from runtime.models.context import PipelineConfig, SchemaCollections
from infrastructure.registry import deps
from runtime.validator.graph_traversal import validate_graph
from jsonSchema.jsonRegistry import core_schema
from runtime.engine import create_engine
from runtime.init import init_handlers,init_hooks,init_tools_schema



base_schema = core_schema

def pipeline(schema:dict, config:PipelineConfig = None):
    TOOLS_REQUIRED_NODES = {"TOOLS_MAPPER","EXECUTE_TOOLS"}
    if not validate_graph(schema):
        raise ValueError("schema.json does not valid, might be there hanging nodes or unreachable nodes")
    schema_collection = SchemaCollections(core_schema=schema, tools_schema=None)
    
    active_handlers = init_handlers(schema, config)
    key_active_handler = set(active_handlers.keys())

    active_hooks = init_hooks(schema)

    if key_active_handler & TOOLS_REQUIRED_NODES:
        init_tools_schema(config.tools_schema if config else None)
        schema_collection.tools_schema=config.tools_schema

    
    engine = create_engine(schema_collection, active_handlers, active_hooks, deps)    

    return engine
