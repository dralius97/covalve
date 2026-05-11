from runtime.executor.schema import ArgsCtx, ReturnSchema, RuntimeMetadata
import json
from pydantic import ValidationError

with open('./prompt/query_analyze_prompt.txt') as f:
    query_analisis_prompt = f.read()


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
    """
    result_from_llm = await callLLM(prompt)
        
    try:
        metadata = RuntimeMetadata.model_validate_json(result_from_llm)
        ctx.context.metadata = metadata
    except (ValidationError, json.JSONDecodeError) as e:
        ctx.context.error = {"type": "PARSE_ERROR", "detail": str(e)}
        ctx.context.last_error_emitted = ctx.state
        return ReturnSchema(event='INTERNAL_ERROR', context=ctx.context)
    
    confidences = [unit.confidence for unit in metadata.content]
    any_low = any(c < 0.5 for c in confidences)
    mean_low = sum(confidences) / len(confidences) < 0.75

    if any_low or mean_low:
        return ReturnSchema(event='LOW_CONFIDENCE', context=ctx.context)

    return ReturnSchema(event= 'NEXT', context=ctx.context)


