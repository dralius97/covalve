import json
from runtime.validator.graph_traversal import validate_graph


with open("./jsonSchema/tools_schema.json") as data:
    tools_schema = json.load(data)

with open("./jsonSchema/schema.json") as data:
    schema = json.load(data)
    if not validate_graph(schema):
        raise ValueError("schema.json does not valid, might be there hanging nodes or unreachable nodes")



tools_schema = tools_schema

core_schema = schema
