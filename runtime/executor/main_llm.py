from runtime.executor.schema import ArgsCtx, ReturnSchema, OutputSchema, OutputStatus, MainLLMResponse
from plugins.registry import callLLM
import json

with open('./runtime/prompt/clarification_template.txt') as f:
    main_llm_clarification_prompt = f.read()

with open('./runtime/prompt/main_llm_response.txt') as f:
    main_llm_response_prompt = f.read()


async def handle_main_llm(ctx: ArgsCtx) -> ReturnSchema:

    template_prompt = main_llm_clarification_prompt if ctx.context.is_clarification else main_llm_response_prompt
    prompt = f"""
        {template_prompt}

        ## Data
        {ctx.context.tools_data if not ctx.context.is_clarification else "No data available"}

        ## Clarification Context
        {ctx.context.fallback_content if ctx.context.is_clarification else ""}
        
        ## Previous Conversation
        {ctx.context.background}

        ##Question
        {ctx.context.query}

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

