from covalve.runtime.models.context import PipelineConfig, SchemaCollections
from covalve.runtime.validator.graph_traversal import validate_graph
from importlib.resources import files
from covalve.runtime.engine import create_engine
from covalve.runtime.init import init_handlers,init_hooks,init_tools_schema
import json
_schema_text = files("covalve.schemas").joinpath("schema.json").read_text()



base_schema = json.loads(_schema_text)

def pipeline(schema:dict, config:PipelineConfig = None):
    TOOLS_REQUIRED_NODES = {"TOOLS_MAPPER","EXECUTE_TOOLS"}
    deps = config.dependencies if config else None
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
