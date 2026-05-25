from runtime.schema.schema import ArgsCtx, ReturnSchema, InfrastructureRegistry

def factory_error_counter(deps:InfrastructureRegistry):
    async def handle_error_counter(ctx: ArgsCtx) -> ReturnSchema: 
        session_id = ctx.context.session_id
        emitter = ctx.context.last_error_emitted
        next_event = 'RETRY_TOOLS' if emitter == 'EXECUTE_TOOLS' else 'RETRY_ANALYZE'
        key = f'{session_id}:{emitter}'
        counter = int(await deps.redis.get(key) or 0)
        counter += 1
        await deps.redis.set(key, counter)
        if counter >= 3:
            next_event = 'RETRY_TIMES_OUT'
        return ReturnSchema(event=next_event, context=ctx.context)
    return handle_error_counter

