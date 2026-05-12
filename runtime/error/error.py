from runtime.schema.schema import ArgsCtx, ReturnSchema, OutputSchema, OutputStatus

async def handle_internal_server_error(ctx: ArgsCtx) -> ReturnSchema:
    ctx.context.response = OutputSchema(
         text="Something went wrong. Please try again later.",
        status=OutputStatus.ERROR,
        traceId=ctx.context.traceId
    )
    return ReturnSchema(event="NEXT", context=ctx.context)
