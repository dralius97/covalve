from runtime.schema.schema import ArgsCtx, ReturnSchema, RuntimeMetadata, QueryIntent, InfrastructureRegistry
from pydantic import ValidationError
from prompt.promptRegistry import query_analisis_prompt
import json

def factory_analyzer(deps: InfrastructureRegistry):
    async def handle_analyze(ctx: ArgsCtx) -> ReturnSchema: 
        copy_context = ctx.context.model_copy(deep=True)
        prev_summarize = copy_context.background.summarize if copy_context.background else ""
        prev_conv = [conv.model_dump(exclude={'data'}) for conv in copy_context.background.conversation] if ctx.context.background else []
        prompt = f"""
            {query_analisis_prompt}
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
            metadata: RuntimeMetadata = await deps.llm.analyze(prompt)
            copy_context.metadata = metadata
        except (ValidationError, json.JSONDecodeError) as e:
            copy_context.error = {"type": "PARSE_ERROR", "detail": str(e)}
            copy_context.last_error_emitted = ctx.state
            return ReturnSchema(event='INTERNAL_ERROR', context=copy_context)

        confidences = [unit.confidence for unit in metadata.content]
        intent = [unit.intent for unit in metadata.content]
        any_low = any(c < 0.5 for c in confidences)
        mean_low = sum(confidences) / len(confidences) < 0.75
        any_outofcontext = any(i == QueryIntent.OUT_OF_CONTEXT for i in intent)
        if any_low or mean_low or any_outofcontext:
            return ReturnSchema(event='LOW_CONFIDENCE', context=copy_context)

        return ReturnSchema(event= 'NEXT', context=copy_context)

    return handle_analyze

