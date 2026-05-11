from runtime.executor.schema import ArgsCtx, ReturnSchema 



async def handle_error_counter(ctx: ArgsCtx) -> ReturnSchema: 
    session_id = ctx.context.session_id
    emitter = ctx.context.last_error_emitted
    next_event = 'RETRY_TOOLS' if emitter == 'TOOLS_RUNTIME' else 'RETRY_ANALYZE'
    key = f'{session_id}:{emitter}'
    counter = int(redis.get(key) or 0)
    counter += 1
    redis.set(key, counter)
    if counter >= 3:
        next_event = 'RETRY_TIMES_OUT'
    return ReturnSchema(event=next_event, context=ctx.context)

