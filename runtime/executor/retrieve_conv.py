from runtime.schema.schema import ArgsCtx, ReturnSchema, BackgroundUnit, InfrastructureRegistry

async def factory_retrieve_memmory(deps:InfrastructureRegistry):
    async def handle_retrieve_previous_conversation(ctx: ArgsCtx) -> ReturnSchema: 
        session_id = ctx.context.session_id
        previsous_conv = await deps.storage.retrieve_conv(session_id)
        if previsous_conv is not None:
            ctx.context.background = BackgroundUnit(
                summarize=previsous_conv.summarize,
                conversation=previsous_conv.conversation
            )
        return ReturnSchema(event="NEXT", context=ctx.context)
    return handle_retrieve_previous_conversation
