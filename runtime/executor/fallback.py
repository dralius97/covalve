from runtime.schema.schema import ArgsCtx, ReturnSchema, QueryIntent



async def handle_fallback(ctx: ArgsCtx) -> ReturnSchema: 
    content = ctx.context.metadata.content
    ctx.context.is_clarification = True
    confidences = [unit.confidence for unit in content]

    threshold = 0.5 if any(c < 0.5 for c in confidences) else 0.75

    ctx.context.fallback_content = [
        item for item in content
        if item.confidence < threshold or item.intent == QueryIntent.OUT_OF_CONTEXT
    ]

    return ReturnSchema(event="NEXT", context=ctx.context)

