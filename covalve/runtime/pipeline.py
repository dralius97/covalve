from covalve.runtime.models.context import PipelineConfig, SchemaCollections
from covalve.runtime.validator.graph_traversal import validate_graph
from importlib.resources import files
from covalve.runtime.engine import create_engine
from covalve.runtime.init import init_handlers,init_hooks,init_tools_schema
from covalve.runtime.models.schema import CoreSchema
import json
from typing import Optional
_schema_text = files("covalve.schemas").joinpath("schema.json").read_text()



base_schema = CoreSchema.model_validate(json.loads(_schema_text))

def pipeline(schema:dict, config:Optional[PipelineConfig] = None):
    TOOLS_REQUIRED_NODES = {"TOOLS_MAPPER","EXECUTE_TOOLS"}
    core_schema = CoreSchema.model_validate(schema)
    deps = config.dependencies if config else None
    if not validate_graph(core_schema):
        raise ValueError("schema.json does not valid, might be there hanging nodes or unreachable nodes")
    schema_collection = SchemaCollections(core_schema=core_schema, tools_schema=None)
    
    active_handlers = init_handlers(core_schema, config)
    key_active_handler = set(active_handlers.keys())

    active_hooks = init_hooks(core_schema)

    if key_active_handler & TOOLS_REQUIRED_NODES:
        if config is None or config.tools_schema is None:
            raise ValueError("tools_schema is required when using TOOLS_MAPPER or EXECUTE_TOOLS nodes.")
        init_tools_schema(config.tools_schema)
        schema_collection.tools_schema=config.tools_schema

    engine = create_engine(schema_collection, active_handlers, active_hooks, deps)    

    return engine
