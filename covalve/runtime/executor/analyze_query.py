from covalve.runtime.models.context import ArgsCtx, ReturnSchema, RuntimeMetadata
from covalve.infrastructure.contract import InfrastructureRegistry
from pydantic import ValidationError
from covalve.runtime.prompt_base.prompt import Prompt
import json

def factory_analyzer(deps: InfrastructureRegistry):
    if deps.llm is None:
        raise ValueError("LLMBase is required for ANALYZE")
    
    llm = deps.llm 
    async def handle_analyze(ctx: ArgsCtx) -> ReturnSchema: 
        copy_context = ctx.context.model_copy(deep=True)
        prev_summarize = copy_context.background.summarize if copy_context.background else ""
        prev_conv = [conv.model_dump(exclude={'data'}) for conv in copy_context.background.conversation] if copy_context.background else []
        context_payload = f"""
            {Prompt.get_analyze_prompt()}

            ## Summarize previous conversation
            {prev_summarize}

            ## Previous Conversation
            {prev_conv}

            ## Current Query
            {copy_context.query}

            ## Current Date
            {copy_context.current_time.strftime('%Y-%m-%d')}
        """

        try:
            metadata = await llm.analyze(context_payload)
            copy_context.metadata = RuntimeMetadata.model_validate(metadata)
        except (ValidationError, json.JSONDecodeError) as e:
            copy_context.error = {"type": "PARSE_ERROR", "detail": str(e)}
            copy_context.last_error_emitted = ctx.state
            return ReturnSchema(event='INTERNAL_ERROR', context=copy_context)

        confidences = [unit.confidence for unit in metadata.content]
        any_low = any(c < 0.5 for c in confidences)
        mean_low = sum(confidences) / len(confidences) < 0.75
        if any_low or mean_low:
            return ReturnSchema(event='LOW_CONFIDENCE', context=copy_context)

        return ReturnSchema(event= 'NEXT', context=copy_context)

    return handle_analyze

