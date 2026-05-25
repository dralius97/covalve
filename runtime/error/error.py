from runtime.schema.schema import ArgsCtx, ReturnSchema, OutputSchema, OutputStatus, InfrastructureRegistry

def factory_internal_error(deps:InfrastructureRegistry):
    async def handle_internal_server_error(ctx: ArgsCtx) -> ReturnSchema:
        ctx.context.response = OutputSchema(
             text="Something went wrong. Please try again later.",
            status=OutputStatus.ERROR,
            traceId=ctx.context.traceId
        )
        return ReturnSchema(event="NEXT", context=ctx.context)
    return handle_internal_server_error