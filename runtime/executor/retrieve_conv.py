from runtime.models.context import ArgsCtx, ReturnSchema, BackgroundUnit
from infrastructure.contract import InfrastructureRegistry

def factory_retrieve_memmory(deps:InfrastructureRegistry):
    async def handle_retrieve_previous_conversation(ctx: ArgsCtx) -> ReturnSchema: 
        copy_context = ctx.context.model_copy(deep=True)
        session_id = copy_context.session_id
        previsous_conv = await deps.storage.retrieve_conv(session_id)
        if previsous_conv is not None:
            copy_context.background = BackgroundUnit(
                summarize=previsous_conv.summarize,
                conversation=previsous_conv.conversation
            )
        return ReturnSchema(event="NEXT", context=copy_context)
    return handle_retrieve_previous_conversation
