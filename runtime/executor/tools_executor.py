from runtime.schema.schema import ArgsCtx, ReturnSchema
from plugins.registry import mcp
from jsonSchema.jsonRegistry import tools_schema
import asyncio
import json



def _get_context_for_tool(tool_name: str, metadata_content: list, tools_schema: dict) -> str:
    tool_intents = tools_schema[tool_name]["intent"]

    relevant = [
        unit.composition_context 
        for unit in metadata_content 
        if unit.intent in tool_intents
    ]
    
    return " | ".join(relevant) if relevant else ""



async def handle_execute_tools(ctx: ArgsCtx) -> ReturnSchema:
    priority_group = ctx.context.tool_list
    is_break = False
    event = "NEXT"
    ctx.context.tools_data = {}
    for current_priority in sorted(priority_group):
        tools = priority_group[current_priority]
        results = await asyncio.gather(*[
            mcp.retrieve(tool["name"], {
                "question":ctx.context.metadata.raw_query,
                "context": _get_context_for_tool(
                tool["name"], 
                ctx.context.metadata.content,
                tools_schema
                ) 
                }) for tool in tools
        ], return_exceptions=True)
        for tool, result in zip(tools, results):
            if isinstance(result, Exception):
                if tool["skippable"]:
                    ctx.context.tool_list[current_priority].remove(tool)
                    continue
                is_break = True
            else:
                text = result.content[0].text
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    data = text
                ctx.context.tools_data[tool["name"]] = data
                ctx.context.tool_list[current_priority].remove(tool)
        if is_break is True:
            event = "INTERNAL_ERROR"
            ctx.context.last_error_emitted = ctx.state
            break
        
    return ReturnSchema(event=event, context=ctx.context)

