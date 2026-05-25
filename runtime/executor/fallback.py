from runtime.schema.schema import ArgsCtx, ReturnSchema, QueryIntent, InfrastructureRegistry


def factory_fallback(deps:InfrastructureRegistry):
    async def handle_fallback(ctx: ArgsCtx) -> ReturnSchema: 
        copy_context = ctx.context.model_copy(deep=True)
        content = copy_context.metadata.content
        copy_context.is_clarification = True
        confidences = [unit.confidence for unit in content]

        threshold = 0.5 if any(c < 0.5 for c in confidences) else 0.75

        copy_context.fallback_content = [
            item for item in content
            if item.confidence < threshold or item.intent == QueryIntent.OUT_OF_CONTEXT
        ]

        return ReturnSchema(event="NEXT", context=copy_context)
    return handle_fallback