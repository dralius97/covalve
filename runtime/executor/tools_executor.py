from runtime.schema.schema import ArgsCtx, ReturnSchema
from plugins.registry import mcp
import asyncio


async def handle_execute_tools(ctx: ArgsCtx) -> ReturnSchema:
    priority_group = ctx.context.tool_list
    is_break = False
    event = "NEXT"
    ctx.context.tools_data = {}
    for current_priority in sorted(priority_group):
        tools = priority_group[current_priority]
        results = await asyncio.gather(*[
            mcp.retrieve(tool["name"]) for tool in tools
        ], return_exceptions=True)
        for tool, result in zip(tools, results):
            if isinstance(result, Exception):
                if tool["skippable"]:
                    ctx.context.tool_list[current_priority].remove(tool)
                    continue
                is_break = True
            else:
                ctx.context.tools_data.update(result)
                ctx.context.tool_list[current_priority].remove(tool)
        if is_break is True:
            event = "INTERNAL_ERROR"
            ctx.context.last_error_emitted = ctx.state
            break
        
    return ReturnSchema(event=event, context=ctx.context)

