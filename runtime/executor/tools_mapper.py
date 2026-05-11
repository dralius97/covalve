from collections import defaultdict
from runtime.executor.schema import ArgsCtx, ReturnSchema
import json

with open("./jsonSchema/tools_schema.json") as data:
    tools_schema = json.load(data)


async def handle_tools_mapper(ctx: ArgsCtx) -> ReturnSchema: 
    content = ctx.context.metadata.content
    priority_groups = defaultdict(list)
    for tool_name, tool_config in tools_schema.items():
        for intent in content:
            if intent.intent in tool_config["intent"]:
                priority_groups[tool_config["priority"]].append({"name": tool_name, "skippable": tool_config["skippable"]})
                break
    ctx.context.tool_list = dict(priority_groups)
    return ReturnSchema(event="NEXT", context=ctx.context)
    
