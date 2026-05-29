from covalve.runtime.models.context import ArgsCtx, ReturnSchema, OutputSchema 
from covalve.runtime.models.io import OutputStatus 
from covalve.infrastructure.contract import InfrastructureRegistry

def factory_internal_error(deps:InfrastructureRegistry):
    async def handle_internal_server_error(ctx: ArgsCtx) -> ReturnSchema:
        copy_context = ctx.context.model_copy(deep=True)
        copy_context.response = OutputSchema(
             text="Something went wrong. Please try again later.",
            status=OutputStatus.ERROR,
            traceId=copy_context.traceId
        )
        return ReturnSchema(event="NEXT", context=copy_context)
    return handle_internal_server_error