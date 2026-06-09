import pytest
from covalve.runtime.hook.context import ReadOnlyContext
from covalve.runtime.models.context import ActiveHook, PipelineConfig, PipelineContext, ReturnSchema, SchemaCollections
from covalve.runtime.models.io import OutputSchema, OutputStatus
from tests.helpers import make_minimal_schema, make_pipeline_context, supports_context_local


def test_pipeline_context_and_return_schema_round_trip():
    context = make_pipeline_context(
        response=OutputSchema(
            text="done",
            status=OutputStatus.SUCCESS,
            traceId="trace-id",
        ),
    )
    result = ReturnSchema(event="NEXT", context=context)

    assert result.event == "NEXT"
    assert result.context.response.text == "done"


def test_schema_collections_and_pipeline_config_defaults():
    schema_colls = SchemaCollections(core_schema=make_minimal_schema())
    config = PipelineConfig()

    assert schema_colls.tools_schema is None
    assert config.dependencies is None


def test_active_hook_model_holds_nested_hooks():
    active = ActiveHook(observer={}, interceptor={})

    assert active.observer == {}
    assert active.interceptor == {}


def test_read_only_context_is_frozen():
    ctx = ReadOnlyContext(**make_pipeline_context().model_dump())

    try:
        ctx.query = "mutated"
        assert False, "expected frozen model assignment to fail"
    except Exception:
        assert ctx.query == "what is the answer"


@pytest.mark.skipif(not supports_context_local(), reason="ADR-007 local field not implemented yet")
def test_pipeline_context_local_defaults_to_none():
    context = make_pipeline_context()

    assert context.local is None


@pytest.mark.skipif(not supports_context_local(), reason="ADR-007 local field not implemented yet")
def test_pipeline_context_model_copy_can_update_local_without_mutating_original():
    context = make_pipeline_context()
    copied = context.model_copy(update={"local": {"step": "done"}})

    assert context.local is None
    assert copied.local == {"step": "done"}
    assert copied is not context
