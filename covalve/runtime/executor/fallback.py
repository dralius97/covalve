from covalve.runtime.models.context import ArgsCtx, ReturnSchema 
from covalve.infrastructure.contract import InfrastructureRegistry


def factory_fallback(deps:InfrastructureRegistry):
    async def handle_fallback(ctx: ArgsCtx) -> ReturnSchema: 
        copy_context = ctx.context.model_copy(deep=True)
        content = copy_context.metadata.content if copy_context.metadata else [] 
        copy_context.is_clarification = True
        confidences = [unit.confidence for unit in content]

        threshold = 0.5 if any(c < 0.5 for c in confidences) else 0.75

        copy_context.fallback_content = [
            item for item in content
            if item.confidence < threshold
        ]

        return ReturnSchema(event="NEXT", context=copy_context)
    return handle_fallback