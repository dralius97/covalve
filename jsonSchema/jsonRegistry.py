import json

with open("./jsonSchema/tools_schema.json") as data:
    tools_schema = json.load(data)

with open("./jsonSchema/schema.json") as data:
    schema = json.load(data)


tools_schema = tools_schema

core_schema = schema
