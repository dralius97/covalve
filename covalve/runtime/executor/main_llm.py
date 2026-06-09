from covalve.runtime.models.context import ArgsCtx, ReturnSchema, OutputSchema 
from covalve.runtime.models.io import OutputStatus, MainLLMResponse, GenerateCondition
from covalve.infrastructure.contract import InfrastructureRegistry

def factory_main_llm(deps: InfrastructureRegistry):
    if deps.llm is None:
        raise ValueError("LLMBase is required for MAIN_LLM")
    
    llm = deps.llm 
    

    def _get_context_tools(context, schema):
        tools_context = ""
        if not context.tools_data:
            return tools_context
        tools_schema = schema.tools_schema
        for tool_name, content_blocks in context.tools_data.items():
            tool_intents = tools_schema[tool_name]["intent"]
            intent_context = next(
                (unit.composition_context for unit in context.metadata.content
                 if unit.intent in tool_intents),
                context.query
            )
            text_parts = [b.text for b in content_blocks if b.type == "text"]
            combined_text = "\n".join(text_parts)
            tools_context += f"\n### Data for: '{intent_context}'\n{combined_text}\n"
        return tools_context


    async def handle_main_llm(ctx: ArgsCtx) -> ReturnSchema:
        copy_context = ctx.context.model_copy(deep=True)
        tools_context = _get_context_tools(copy_context, ctx.schema_colls)
        is_rejected = True if copy_context.guardrail_rejection else False
        generate_condition = GenerateCondition(
            is_clarification=copy_context.is_clarification, 
            is_rejected=is_rejected)
        context_payload = f"""

            ## Data Hasil Query
            {tools_context}

            ## Previous Conversation
            {copy_context.background}

            ## Intent Analysis
            {[unit.model_dump() for unit in copy_context.metadata.content] if copy_context.metadata else []}

            ## Question
            {copy_context.query}

            ## Current Date
            {copy_context.current_time.strftime('%Y-%m-%d')}
        """ 

        if copy_context.is_clarification:
            clarification_section = f"## Clarification Context\n{copy_context.fallback_content}" if copy_context.fallback_content else ""
            guardrail_section = f"## Out Of Context Reason\n{copy_context.guardrail_rejection}" if copy_context.guardrail_rejection else ""
            context_payload = f"""

            ## Previous Conversation
            {copy_context.background}

            {clarification_section}

            {guardrail_section}
            
            ## Question
            {copy_context.query}

            ## Current Date
            {copy_context.current_time.strftime('%Y-%m-%d')}

            """

        result_from_llm: MainLLMResponse = await llm.generate(context_payload, generate_condition)
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

