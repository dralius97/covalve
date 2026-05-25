from runtime.schema.schema import ArgsCtx, ReturnSchema, OutputSchema, OutputStatus, MainLLMResponse,InfrastructureRegistry
from prompt.promptRegistry import main_llm_clarification_prompt,main_llm_response_prompt

def factory_main_llm(deps: InfrastructureRegistry):
    async def handle_main_llm(ctx: ArgsCtx) -> ReturnSchema:
        copy_context = ctx.context.model_copy()
        tools_context = ""
        if copy_context.tools_data:
            for _, data in copy_context.tools_data.items():
                intent_context = next(
                    (unit.composition_context for unit in copy_context.metadata.content 
                     if unit.intent in ['operate', 'lookup', 'validate', 'compare']),
                    copy_context.query
                )
                tools_context += f"\n### Data untuk: '{intent_context}'\n{data}\n"

        template_prompt = main_llm_clarification_prompt if copy_context.is_clarification else main_llm_response_prompt
        prompt = f"""
            {template_prompt}

            ## Data Hasil Query
            {tools_context}

            ## Clarification Context
            {copy_context.fallback_content if copy_context.is_clarification else ""}

            ## Previous Conversation
            {copy_context.background}

            ## Intent Analysis
            {[unit.model_dump() for unit in copy_context.metadata.content]}

            ## Question
            {copy_context.query}

            ## Current Date
            {copy_context.current_time.strftime('%Y-%m-%d')}

        """ 

        result_from_llm: MainLLMResponse = await deps.llm.generate(prompt)
        copy_context.summarize = result_from_llm.summarize

        result = OutputSchema(
            text=result_from_llm.text,
            attachment= None,
            status=OutputStatus.CLARIFICATION if copy_context.is_clarification else OutputStatus.SUCCESS,
            traceId=copy_context.traceId
        )

        copy_context.response = result
        return ReturnSchema(event="NEXT", context=copy_context)
    return handle_main_llm

