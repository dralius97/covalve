from runtime.executor.schema import ArgsCtx, ReturnSchema, DataContent
from plugins.registry import redis, storage


async def handle_save_data_to_persistence(ctx: ArgsCtx) -> ReturnSchema: 
    session_id = ctx.context.session_id
    data_content = DataContent(
        session_id= session_id,
        metadata= [unit.model_dump() for unit in ctx.context.metadata.content] if ctx.context.metadata else [],
        user= ctx.context.query,
        assistance= ctx.context.response.text if ctx.context.response else "",
        traceId= ctx.context.traceId,
        summarize= ctx.context.summarize,
        data= ctx.context.tools_data
    )
    await storage.save_conv(data_content)
    await redis.delete(f"{session_id}:ANALYZE")
    await redis.delete(f"{session_id}:EXECUTE_TOOLS")

    return ReturnSchema(event="NEXT", context=ctx.context)

