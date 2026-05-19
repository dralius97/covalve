from runtime.schema.schema import ArgsCtx, ReturnSchema, RuntimeMetadata, QueryIntent
from pydantic import ValidationError
from plugins.registry import callLLM
from prompt.promptRegistry import query_analisis_prompt
import json


async def handle_analyze(ctx: ArgsCtx) -> ReturnSchema: 
    prev_summarize = ctx.context.background.summarize if ctx.context.background else ""
    prev_conv = [conv.model_dump(exclude={'data'}) for conv in ctx.context.background.conversation] if ctx.context.background else []
    prompt = f"""
        {query_analisis_prompt}
        ## Summarize previous conversation
        {prev_summarize}

        ## Previous Conversation
        {prev_conv}

        ## Current Query
        {ctx.context.query}
        
        ## Current Date
        {ctx.context.current_time.strftime('%Y-%m-%d')}
    """
        
    try:
        metadata: RuntimeMetadata = await callLLM.analyze(prompt)
        ctx.context.metadata = metadata
    except (ValidationError, json.JSONDecodeError) as e:
        ctx.context.error = {"type": "PARSE_ERROR", "detail": str(e)}
        ctx.context.last_error_emitted = ctx.state
        return ReturnSchema(event='INTERNAL_ERROR', context=ctx.context)
    
    confidences = [unit.confidence for unit in metadata.content]
    intent = [unit.intent for unit in metadata.content]
    any_low = any(c < 0.5 for c in confidences)
    mean_low = sum(confidences) / len(confidences) < 0.75
    any_outofcontext = any(i == QueryIntent.OUT_OF_CONTEXT for i in intent)
    if any_low or mean_low or any_outofcontext:
        return ReturnSchema(event='LOW_CONFIDENCE', context=ctx.context)

    return ReturnSchema(event= 'NEXT', context=ctx.context)


