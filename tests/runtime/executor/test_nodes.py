from datetime import datetime

import json
import pytest
from pydantic import ValidationError

from covalve.infrastructure.contract import InfrastructureRegistry
from covalve.runtime.executor.analyze_query import factory_analyzer
from covalve.runtime.executor.error import factory_internal_error
from covalve.runtime.executor.error_counter import factory_error_counter
from covalve.runtime.executor.fallback import factory_fallback
from covalve.runtime.executor.guardrail import factory_guardrails
from covalve.runtime.executor.main_llm import factory_main_llm
from covalve.runtime.executor.retrieve_conv import factory_retrieve_memmory
from covalve.runtime.executor.save_data import factory_save_data
from covalve.runtime.executor.tools_executor import factory_execute_tools
from covalve.runtime.executor.tools_mapper import factory_tools_mapper
from covalve.runtime.models.context import ExecutedTools, PipelineContext
from covalve.runtime.models.infra import BackgroundUnit, ConvData, GuardRailResponse, MCPResponse, TextContent
from covalve.runtime.models.io import DataContent, GenerateCondition, MainLLMResponse, OutputSchema, OutputStatus
from tests.helpers import (
    assert_context_local_untouched,
    DummyCache,
    DummyGuardrail,
    DummyLLM,
    DummyMemory,
    DummyToolClient,
    make_args_ctx,
    make_background,
    make_content_unit,
    make_empty_hooks,
    make_linear_schema,
    make_minimal_schema,
    make_pipeline_context,
    make_tools_schema,
    make_runtime_metadata,
)


@pytest.mark.asyncio
async def test_factory_retrieve_memory_loads_background():
    memory = DummyMemory(retrieved=make_background())
    handler = factory_retrieve_memmory(InfrastructureRegistry(memory=memory))
    ctx = make_args_ctx(context=make_pipeline_context())

    result = await handler(ctx)

    assert result.event == "NEXT"
    assert result.context.background.summarize == "previous summary"
    assert memory.retrieve_calls == ["session-1"]
    assert_context_local_untouched(result.context)


def test_factory_retrieve_memory_requires_dependency():
    with pytest.raises(ValueError, match="MemoryStoreBase is required"):
        factory_retrieve_memmory(InfrastructureRegistry())


@pytest.mark.asyncio
async def test_factory_analyzer_handles_success_and_low_confidence():
    llm = DummyLLM(
        analyze_result=make_runtime_metadata(
            content=[
                make_content_unit(intent="lookup", composition_context="ctx", confidence=0.4)
            ]
        )
    )
    handler = factory_analyzer(InfrastructureRegistry(llm=llm))
    ctx = make_args_ctx(context=make_pipeline_context(background=make_background()))

    result = await handler(ctx)

    assert result.event == "LOW_CONFIDENCE"
    assert result.context.metadata.raw_query == "what is this"
    assert "Current Query" in llm.analyze_calls[0]
    assert_context_local_untouched(result.context)


@pytest.mark.asyncio
async def test_factory_analyzer_returns_parse_error_on_exception():
    llm = DummyLLM(analyze_error=json.JSONDecodeError("bad payload", "{}", 0))
    handler = factory_analyzer(InfrastructureRegistry(llm=llm))
    ctx = make_args_ctx(context=make_pipeline_context(background=make_background()))

    result = await handler(ctx)

    assert result.event == "INTERNAL_ERROR"
    assert result.context.last_error_emitted == "START"
    assert result.context.error["type"] == "PARSE_ERROR"
    assert_context_local_untouched(result.context)


def test_factory_analyzer_requires_llm():
    with pytest.raises(ValueError, match="LLMBase is required"):
        factory_analyzer(InfrastructureRegistry())


@pytest.mark.asyncio
async def test_factory_guardrails_rejects_out_of_scope():
    guardrail = DummyGuardrail(GuardRailResponse(reason="nope", is_rejected=True))
    handler = factory_guardrails(InfrastructureRegistry(guardrail=guardrail))
    ctx = make_args_ctx(context=make_pipeline_context(background=make_background()))

    result = await handler(ctx)

    assert result.event == "OUT_OF_SCOPE"
    assert result.context.is_clarification is True
    assert result.context.guardrail_rejection == "nope"
    assert_context_local_untouched(result.context)


def test_factory_guardrails_requires_dependency():
    with pytest.raises(ValueError, match="guardrailStoreBase is required"):
        factory_guardrails(InfrastructureRegistry())


@pytest.mark.asyncio
async def test_factory_error_counter_increments_and_times_out():
    cache = DummyCache(initial={"session-1:EXECUTE_TOOLS": 2})
    handler = factory_error_counter(InfrastructureRegistry(cache=cache))
    ctx = make_args_ctx(
        state="ERROR_COUNTER",
        context=make_pipeline_context(last_error_emitted="EXECUTE_TOOLS"),
    )

    result = await handler(ctx)

    assert result.event == "RETRY_TIMES_OUT"
    assert cache.store["session-1:EXECUTE_TOOLS"] == 3
    assert_context_local_untouched(result.context)


def test_factory_error_counter_requires_cache():
    with pytest.raises(ValueError, match="CacheBase is required"):
        factory_error_counter(InfrastructureRegistry())


@pytest.mark.asyncio
async def test_factory_tools_mapper_groups_tools_by_priority():
    handler = factory_tools_mapper(InfrastructureRegistry())
    context = make_pipeline_context(metadata=make_runtime_metadata())
    ctx = make_args_ctx(
        state="TOOLS_MAPPER",
        context=context,
        tools_schema=make_tools_schema(),
    )

    result = await handler(ctx)

    assert result.event == "NEXT"
    assert result.context.tool_list == {
        0: [{"name": "tool_a", "skippable": False}],
    }
    assert_context_local_untouched(result.context)


@pytest.mark.asyncio
async def test_factory_execute_tools_collects_successful_results():
    tool_response = MCPResponse(
        content=[TextContent(type="text", text="tool output")],
        isError=False,
    )
    client = DummyToolClient(response_map={"tool_a": tool_response})
    handler = factory_execute_tools(InfrastructureRegistry(tools=client))
    context = make_pipeline_context(
        metadata=make_runtime_metadata(),
        tool_list={0: [{"name": "tool_a", "skippable": False}]},
        tools_data={"previous_tool": [TextContent(type="text", text="previous output")]},
    )
    ctx = make_args_ctx(
        state="EXECUTE_TOOLS",
        context=context,
        tools_schema=make_tools_schema(),
    )

    result = await handler(ctx)

    assert result.event == "NEXT"
    assert result.context.tools_data["tool_a"][0].text == "tool output"
    assert result.context.executed_tools.success_tools == ["tool_a"]
    assert client.calls[0][2] == {
        "previous_tool": [TextContent(type="text", text="previous output")]
    }
    assert_context_local_untouched(result.context)


@pytest.mark.asyncio
async def test_factory_execute_tools_skips_skippable_errors():
    client = DummyToolClient(response_map={"tool_b": RuntimeError("boom")})
    handler = factory_execute_tools(InfrastructureRegistry(tools=client))
    context = make_pipeline_context(
        metadata=make_runtime_metadata(content=[make_content_unit(intent="explain")]),
        tool_list={1: [{"name": "tool_b", "skippable": True}]},
    )
    ctx = make_args_ctx(
        state="EXECUTE_TOOLS",
        context=context,
        tools_schema=make_tools_schema(),
    )

    result = await handler(ctx)

    assert result.event == "NEXT"
    assert result.context.executed_tools.skipped_tools == ["tool_b"]
    assert result.context.tools_data == {}
    assert_context_local_untouched(result.context)


@pytest.mark.asyncio
async def test_factory_execute_tools_fails_on_non_skippable_error():
    client = DummyToolClient(response_map={"tool_a": RuntimeError("boom")})
    handler = factory_execute_tools(InfrastructureRegistry(tools=client))
    context = make_pipeline_context(
        metadata=make_runtime_metadata(),
        tool_list={0: [{"name": "tool_a", "skippable": False}]},
    )
    ctx = make_args_ctx(
        state="EXECUTE_TOOLS",
        context=context,
        tools_schema=make_tools_schema(),
    )

    result = await handler(ctx)

    assert result.event == "INTERNAL_ERROR"
    assert result.context.last_error_emitted == "EXECUTE_TOOLS"
    assert_context_local_untouched(result.context)


def test_factory_execute_tools_requires_dependency():
    with pytest.raises(ValueError, match="ToolClientBase is required"):
        factory_execute_tools(InfrastructureRegistry())


@pytest.mark.asyncio
async def test_factory_main_llm_generates_response_and_prompt():
    llm = DummyLLM(
        generate_result=MainLLMResponse(text="final", summarize="summary"),
    )
    handler = factory_main_llm(InfrastructureRegistry(llm=llm))
    context = make_pipeline_context(
        background=make_background(),
        metadata=make_runtime_metadata(),
        tools_data={"tool_a": [TextContent(type="text", text="tool output")]},
    )
    ctx = make_args_ctx(
        state="MAIN_LLM",
        context=context,
        tools_schema=make_tools_schema(),
    )

    result = await handler(ctx)

    assert result.event == "NEXT"
    assert result.context.response.status == OutputStatus.SUCCESS
    assert "tool output" in llm.generate_calls[0][0]
    assert isinstance(llm.generate_calls[0][1], GenerateCondition)
    assert_context_local_untouched(result.context)


@pytest.mark.asyncio
async def test_factory_main_llm_sets_clarification_output():
    llm = DummyLLM(generate_result=MainLLMResponse(text="clarify", summarize="sum"))
    handler = factory_main_llm(InfrastructureRegistry(llm=llm))
    context = make_pipeline_context(
        background=make_background(),
        metadata=make_runtime_metadata(),
        is_clarification=True,
        guardrail_rejection="blocked",
    )
    ctx = make_args_ctx(
        state="MAIN_LLM",
        context=context,
        tools_schema=make_tools_schema(),
    )

    result = await handler(ctx)

    assert result.context.response.status == OutputStatus.CLARIFICATION
    assert result.context.summarize == "sum"
    assert llm.generate_calls[0][1].is_clarification is True
    assert llm.generate_calls[0][1].is_rejected is True
    assert_context_local_untouched(result.context)


def test_factory_main_llm_requires_dependency():
    with pytest.raises(ValueError, match="LLMBase is required"):
        factory_main_llm(InfrastructureRegistry())


@pytest.mark.asyncio
async def test_factory_internal_error_sets_default_response():
    handler = factory_internal_error(InfrastructureRegistry())
    ctx = make_args_ctx(context=make_pipeline_context())

    result = await handler(ctx)

    assert result.event == "NEXT"
    assert result.context.response.text.startswith("Something went wrong")
    assert result.context.response.status == OutputStatus.ERROR
    assert_context_local_untouched(result.context)


@pytest.mark.asyncio
async def test_factory_fallback_marks_clarification_and_filters_content():
    handler = factory_fallback(InfrastructureRegistry())
    context = make_pipeline_context(
        metadata=make_runtime_metadata(
            content=[
                make_content_unit(intent="lookup", composition_context="keep", confidence=0.4),
                make_content_unit(intent="explain", composition_context="drop", confidence=0.9),
            ]
        )
    )
    ctx = make_args_ctx(state="FALLBACK", context=context)

    result = await handler(ctx)

    assert result.context.is_clarification is True
    assert len(result.context.fallback_content) == 1
    assert result.context.fallback_content[0].composition_context == "keep"
    assert_context_local_untouched(result.context)


@pytest.mark.asyncio
async def test_factory_save_data_persists_and_clears_cache():
    memory = DummyMemory()
    cache = DummyCache(initial={"session-1:ANALYZE": 1, "session-1:EXECUTE_TOOLS": 1})
    handler = factory_save_data(InfrastructureRegistry(memory=memory, cache=cache))
    context = make_pipeline_context(
        metadata=make_runtime_metadata(),
        response=OutputSchema(text="final", status=OutputStatus.SUCCESS, traceId="trace-id"),
        summarize="summary",
        tools_data={"tool_a": [TextContent(type="text", text="tool output")]},
    )
    ctx = make_args_ctx(state="SAVE_DATA_TO_PERSISTENCE", context=context)

    result = await handler(ctx)

    assert result.event == "NEXT"
    assert len(memory.saved) == 1
    assert isinstance(memory.saved[0], DataContent)
    assert cache.deleted == ["session-1:ANALYZE", "session-1:EXECUTE_TOOLS"]
    assert_context_local_untouched(result.context)


@pytest.mark.asyncio
async def test_factory_save_data_keeps_going_when_persistence_fails():
    memory = DummyMemory(fail_on_save=True)
    cache = DummyCache(initial={"session-1:ANALYZE": 1, "session-1:EXECUTE_TOOLS": 1})
    handler = factory_save_data(InfrastructureRegistry(memory=memory, cache=cache))
    ctx = make_args_ctx(state="SAVE_DATA_TO_PERSISTENCE", context=make_pipeline_context())

    result = await handler(ctx)

    assert result.event == "NEXT"
    assert cache.deleted == ["session-1:ANALYZE", "session-1:EXECUTE_TOOLS"]
    assert_context_local_untouched(result.context)
