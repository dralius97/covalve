from runtime.schema.schema import ArgsCtx, ReturnSchema, OutputSchema, OutputStatus, MainLLMResponse
from plugins.registry import callLLM
from prompt.promptRegistry import main_llm_clarification_prompt,main_llm_response_prompt


async def handle_main_llm(ctx: ArgsCtx) -> ReturnSchema:

    tools_context = ""
    if ctx.context.tools_data:
        for _, data in ctx.context.tools_data.items():
            intent_context = next(
                (unit.composition_context for unit in ctx.context.metadata.content 
                 if unit.intent in ['operate', 'lookup', 'validate', 'compare']),
                ctx.context.query
            )
            tools_context += f"\n### Data untuk: '{intent_context}'\n{data}\n"

    template_prompt = main_llm_clarification_prompt if ctx.context.is_clarification else main_llm_response_prompt
    prompt = f"""
        {template_prompt}

        ## Data Hasil Query
        {tools_context}
        
        ## Clarification Context
        {ctx.context.fallback_content if ctx.context.is_clarification else ""}
        
        ## Previous Conversation
        {ctx.context.background}

        ## Intent Analysis
        {[unit.model_dump() for unit in ctx.context.metadata.content]}

        ## Question
        {ctx.context.query}

        ## Current Date
        {ctx.context.current_time.strftime('%Y-%m-%d')}

    """ 

    result_from_llm: MainLLMResponse = await callLLM.generate(prompt)
    ctx.context.summarize = result_from_llm.summarize

    result = OutputSchema(
        text=result_from_llm.text,
        attachment= None,
        status=OutputStatus.CLARIFICATION if ctx.context.is_clarification else OutputStatus.SUCCESS,
        traceId=ctx.context.traceId
    )

    ctx.context.response = result
    return ReturnSchema(event="NEXT", context=ctx.context)

