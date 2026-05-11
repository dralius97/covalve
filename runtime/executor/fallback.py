from runtime.executor.schema import ArgsCtx, ReturnSchema


async def handle_fallback(ctx: ArgsCtx) -> ReturnSchema: 
    content = ctx.context.metadata.content
    ctx.context.is_clarification = True
    confidences = [unit.confidence for unit in content]
    if any(c < 0.5 for c in confidences):
        ctx.context.fallback_content = [item for item in content if item.confidence < 0.5]
    else:
        ctx.context.fallback_content = [item for item in content if item.confidence < 0.75]

    return ReturnSchema(event="NEXT", context=ctx.context)
