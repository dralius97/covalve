from covalve.infrastructure.contract import InfrastructureRegistry
from covalve.runtime.models.context import ArgsCtx, ReturnSchema

def factory_guardrails(deps: InfrastructureRegistry):
    if deps.guardrail is None:
        raise ValueError("guardrailStoreBase is required for RETRIEVE_PREVIOUS_CONVERSATION")
    
    guardrail = deps.guardrail 
    
    async def handle_guardrails(ctx: ArgsCtx) -> ReturnSchema:
        copy_context = ctx.context.model_copy(deep=True)
        result = await guardrail.validate(copy_context.query,copy_context.background)
        if result.is_rejected:
            copy_context.guardrail_rejection = result.reason
            copy_context.is_clarification = True
            return ReturnSchema(event='OUT_OF_SCOPE', context=copy_context)       
        return ReturnSchema(event='NEXT', context=copy_context)
    return handle_guardrails