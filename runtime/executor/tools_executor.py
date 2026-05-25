from runtime.schema.schema import ArgsCtx, ReturnSchema,InfrastructureRegistry
from jsonSchema.jsonRegistry import tools_schema
import asyncio
import json




def factory_execute_tools(deps:InfrastructureRegistry):

    def _get_context_for_tool(tool_name: str, metadata_content: list, tools_schema: dict) -> str:
        tool_intents = tools_schema[tool_name]["intent"]
        relevant = [
            unit.composition_context 
            for unit in metadata_content 
            if unit.intent in tool_intents
        ]
        return " | ".join(relevant) if relevant else ""



    async def handle_execute_tools(ctx: ArgsCtx) -> ReturnSchema:
        copy_context = ctx.context.model_copy(deep=True)
        priority_group = copy_context.tool_list
        is_break = False
        event = "NEXT"
        copy_context.tools_data = copy_context.tools_data or {}
        for current_priority in sorted(priority_group):
            tools = priority_group[current_priority]
            tools_to_run = [
                t for t in tools
                if t["name"] not in copy_context.executed_tools.skipped_tools
                and t["name"] not in copy_context.executed_tools.success_tools
            ]
            results = await asyncio.gather(*[
                deps.mcp.retrieve(tool["name"], {
                    "question":copy_context.metadata.raw_query,
                    "context": _get_context_for_tool(
                    tool["name"], 
                    copy_context.metadata.content,
                    tools_schema
                    ) 
                    }) for tool in tools_to_run
            ], return_exceptions=True)
            for tool, result in zip(tools_to_run, results):
                if isinstance(result, Exception):
                    if tool["skippable"]:
                        copy_context.executed_tools.skipped_tools.append(tool["name"])
                        continue
                    is_break = True
                else:
                    text = result.content[0].text
                    try:
                        data = json.loads(text)
                    except json.JSONDecodeError:
                        data = text
                    copy_context.tools_data[tool["name"]] = data
                    copy_context.executed_tools.success_tools.append(tool["name"])
            if is_break is True:
                event = "INTERNAL_ERROR"
                copy_context.last_error_emitted = ctx.state
                break
        return ReturnSchema(event=event, context=copy_context)
    return handle_execute_tools
