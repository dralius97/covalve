from runtime.models.context import  ArgsCtx, ReturnSchema 
from infrastructure.contract import InfrastructureRegistry

def factory_error_counter(deps:InfrastructureRegistry):
    async def handle_error_counter(ctx: ArgsCtx) -> ReturnSchema:
        copy_context = ctx.context.model_copy(deep=True)
        session_id = copy_context.session_id
        emitter = copy_context.last_error_emitted
        next_event = 'RETRY_TOOLS' if emitter == 'EXECUTE_TOOLS' else 'RETRY_ANALYZE'
        key = f'{session_id}:{emitter}'
        counter = int(await deps.redis.get(key) or 0)
        counter += 1
        await deps.redis.set(key, counter)
        if counter >= 3:
            next_event = 'RETRY_TIMES_OUT'
        return ReturnSchema(event=next_event, context=copy_context)
    return handle_error_counter

