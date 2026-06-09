from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any, Optional

from covalve.infrastructure.contract import InfrastructureRegistry
from covalve.runtime.hook.registry import HookOn
from covalve.runtime.models.context import (
    ArgsCtx,
    ExecutedTools,
    PipelineConfig,
    PipelineContext,
    SchemaCollections,
)
from covalve.runtime.models.infra import (
    BackgroundUnit,
    ConvData,
    GuardRailResponse,
    MCPResponse,
    TextContent,
)
from covalve.runtime.models.schema import CoreSchema, StateConfig, Transition
from covalve.runtime.models.io import MainLLMResponse, OutputSchema, OutputStatus
from covalve.runtime.models.metadata import ContentUnit, RuntimeMetadata


def make_content_unit(
    intent: str = "lookup",
    composition_context: str = "context",
    confidence: float = 0.9,
) -> ContentUnit:
    return ContentUnit(
        intent=intent,
        composition_context=composition_context,
        confidence=confidence,
    )


def make_runtime_metadata(
    raw_query: str = "what is this",
    content: list[ContentUnit] | None = None,
) -> RuntimeMetadata:
    return RuntimeMetadata(
        raw_query=raw_query,
        content=content or [make_content_unit()],
    )


def make_background() -> BackgroundUnit:
    return BackgroundUnit(
        summarize="previous summary",
        conversation=[
            ConvData(
                user="user question",
                assistance="assistant answer",
                metadata=[make_content_unit()],
                data={"a": 1},
            )
        ],
    )


def make_pipeline_context(
    *,
    query: str = "what is the answer",
    session_id: str = "session-1",
    current_time: datetime | None = None,
    background: BackgroundUnit | None = None,
    metadata: RuntimeMetadata | None = None,
    tool_list: dict[int, list[dict]] | None = None,
    tools_data: dict[str, list[Any]] | None = None,
    last_error_emitted: str | None = None,
    is_clarification: bool = False,
    guardrail_rejection: str | None = None,
    response: OutputSchema | None = None,
    summarize: str | None = None,
    fallback_content: list[Any] | None = None,
    local: Optional[dict[str, Any]] = None 
) -> PipelineContext:
    return PipelineContext(
        query=query,
        session_id=session_id,
        current_time=current_time or datetime(2026, 1, 1, 12, 0, 0),
        is_error=False,
        background=background,
        metadata=metadata,
        tool_list=tool_list,
        tools_data=tools_data,
        executed_tools=ExecutedTools(),
        last_error_emitted=last_error_emitted,
        error=None,
        response=response,
        summarize=summarize,
        fallback_content=fallback_content,
        traceId="trace-id",
        is_clarification=is_clarification,
        guardrail_rejection=guardrail_rejection,
        local=local
    )


def make_args_ctx(
    *,
    state: str = "START",
    context: PipelineContext | None = None,
    core_schema: dict | None = None,
    tools_schema: dict | None = None,
) -> ArgsCtx:
    return ArgsCtx(
        state=state,
        context=context or make_pipeline_context(),
        schema_colls=SchemaCollections(
            core_schema=core_schema or make_minimal_schema(),
            tools_schema=tools_schema,
        ),
    )


def make_pipeline_config(
    dependencies: InfrastructureRegistry | None = None,
    add_handlers: dict[str, Any] | None = None,
    overrides: dict[str, Any] | None = None,
    tools_schema: dict[str, Any] | None = None,
) -> PipelineConfig:
    return PipelineConfig(
        dependencies=dependencies,
        add_handlers=add_handlers,
        overrides=overrides,
        tools_schema=tools_schema,
    )


def make_minimal_schema() -> CoreSchema:
    return CoreSchema(
        INITIAL="START",
        FINAL="END",
        states={
            "START": StateConfig(transitions={"NEXT": Transition(to="END")}),
            "END": StateConfig(transitions={}),
        },
    )


def make_linear_schema() -> dict:
    return {
        "INITIAL": "START",
        "FINAL": "END",
        "states": {
            "START": {"transitions": {"NEXT": {"to": "TOOLS_MAPPER"}}},
            "TOOLS_MAPPER": {"transitions": {"NEXT": {"to": "END"}}},
            "END": {"transitions": {}},
        },
    }


def supports_context_local() -> bool:
    return "local" in PipelineContext.model_fields


def assert_context_local_untouched(context: PipelineContext) -> None:
    if supports_context_local():
        assert context.local is None



def make_tools_schema() -> dict:
    return {
        "tool_a": {"priority": 0, "skippable": False, "intent": ["lookup"]},
        "tool_b": {"priority": 1, "skippable": True, "intent": ["explain"]},
    }


def make_empty_hooks() -> dict:
    return {
        "observer": defaultdict(lambda: defaultdict(list)),
        "interceptor": defaultdict(lambda: defaultdict(list)),
    }


class DummyMemory:
    def __init__(self, retrieved: BackgroundUnit | None = None, fail_on_save: bool = False):
        self.retrieved = retrieved
        self.fail_on_save = fail_on_save
        self.saved: list[Any] = []
        self.retrieve_calls: list[str] = []

    async def save_conv(self, content: Any):
        if self.fail_on_save:
            raise RuntimeError("save failed")
        self.saved.append(content)

    async def retrieve_conv(self, session_id: str):
        self.retrieve_calls.append(session_id)
        return self.retrieved


class DummyCache:
    def __init__(self, initial: dict[str, Any] | None = None):
        self.store = dict(initial or {})
        self.deleted: list[str] = []

    async def get(self, key: str):
        return self.store.get(key)

    async def set(self, key: str, value: Any) -> None:
        self.store[key] = value

    async def delete(self, key: str) -> None:
        self.deleted.append(key)
        self.store.pop(key, None)


class DummyLLM:
    def __init__(
        self,
        analyze_result: RuntimeMetadata | None = None,
        generate_result: MainLLMResponse | None = None,
        analyze_error: Exception | None = None,
    ):
        self.analyze_result = analyze_result or make_runtime_metadata()
        self.generate_result = generate_result or MainLLMResponse(
            text="final answer",
            summarize="summary",
        )
        self.analyze_error = analyze_error
        self.analyze_calls: list[str] = []
        self.generate_calls: list[tuple[str, Any]] = []

    async def analyze(self, context_payload: str):
        self.analyze_calls.append(context_payload)
        if self.analyze_error is not None:
            raise self.analyze_error
        return self.analyze_result

    async def generate(self, context_payload: str, condition: Any):
        self.generate_calls.append((context_payload, condition))
        return self.generate_result


class DummyGuardrail:
    def __init__(self, response: GuardRailResponse):
        self.response = response
        self.calls: list[tuple[str, BackgroundUnit | None]] = []

    async def validate(self, query: str, background: BackgroundUnit | None = None):
        self.calls.append((query, background))
        return self.response


class DummyToolClient:
    def __init__(self, response_map: dict[str, Any] | None = None):
        self.response_map = response_map or {}
        self.calls: list[tuple[str, Any]] = []

    async def retrieve(self, tool_name: str, metadata: Any):
        self.calls.append((tool_name, metadata))
        result = self.response_map.get(tool_name)
        if isinstance(result, Exception):
            raise result
        if result is None:
            return MCPResponse(
                content=[TextContent(type="text", text=f"{tool_name} output")],
                isError=False,
            )
        return result


class DummyLog:
    def __init__(self):
        self.calls: list[Any] = []

    async def state_log(self, ctx):
        self.calls.append(ctx)
