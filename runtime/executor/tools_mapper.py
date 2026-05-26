from collections import defaultdict
from runtime.models.context import  ArgsCtx, ReturnSchema 
from infrastructure.contract import InfrastructureRegistry
from jsonSchema.jsonRegistry import tools_schema


def factory_tools_mapper(deps: InfrastructureRegistry):
    async def handle_tools_mapper(ctx: ArgsCtx) -> ReturnSchema: 
        copy_context = ctx.context.model_copy(deep=True)
        content = copy_context.metadata.content
        priority_groups = defaultdict(list)
        for tool_name, tool_config in tools_schema.items():
            for intent in content:
                if intent.intent in tool_config["intent"]:
                    priority_groups[tool_config["priority"]].append({"name": tool_name, "skippable": tool_config["skippable"]})
                    break
        copy_context.tool_list = dict(priority_groups)
        return ReturnSchema(event="NEXT", context=copy_context)
    return handle_tools_mapper
