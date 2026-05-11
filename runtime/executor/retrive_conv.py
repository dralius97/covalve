from runtime.executor.schema import ArgsCtx, ReturnSchema, BackgroundUnit

async def handle_retrieve_previous_conversation(ctx: ArgsCtx) -> ReturnSchema: 
    session_id = ctx.context.session_id
    previsous_conv = await call_db.get_conv(session_id)
    if previsous_conv is not None:
        ctx.context.background = BackgroundUnit(
            summarize=previsous_conv.summarize,
            conversation=previsous_conv.conversation
        )
    return ReturnSchema(event="NEXT", context=ctx.context)
