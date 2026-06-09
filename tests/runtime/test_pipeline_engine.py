from collections import defaultdict

import pytest

from covalve.infrastructure.contract import InfrastructureRegistry
from covalve.runtime.engine import create_engine
from covalve.runtime.models.context import ReturnSchema, SchemaCollections
from covalve.runtime.pipeline import pipeline
from tests.helpers import (
    assert_context_local_untouched,
    make_empty_hooks,
    make_linear_schema,
    make_minimal_schema,
    make_pipeline_config,
    make_pipeline_context,
)


@pytest.mark.asyncio
async def test_create_engine_runs_simple_graph():
    schema = make_minimal_schema()
    schema_colls = SchemaCollections(core_schema=schema, tools_schema=None)

    async def start_handler(ctx):
        return ReturnSchema(event="NEXT", context=ctx.context.model_copy(deep=True))

    handlers = {"START": start_handler, "END": start_handler}
    engine = create_engine(schema_colls, handlers, make_empty_hooks(), InfrastructureRegistry(log=None))

    result = await engine("hello")

    assert result.query == "hello"
    assert result.session_id is not None
    assert_context_local_untouched(result)


def test_pipeline_wires_validation_handlers_and_engine(monkeypatch):
    calls = {}

    monkeypatch.setattr("covalve.runtime.pipeline.validate_graph", lambda schema: True)
    def fake_init_handlers(schema, config=None):
        calls["init_handlers"] = (schema, config)
        return {
            "START": lambda ctx: None,
            "TOOLS_MAPPER": lambda ctx: None, 
            "END": lambda ctx: None,
        }

    def fake_init_hooks(schema):
        calls["init_hooks"] = schema
        return make_empty_hooks()

    def fake_init_tools_schema(tools_schema):
        calls["tools_schema"] = tools_schema

    monkeypatch.setattr("covalve.runtime.pipeline.init_handlers", fake_init_handlers)
    monkeypatch.setattr("covalve.runtime.pipeline.init_hooks", fake_init_hooks)
    monkeypatch.setattr("covalve.runtime.pipeline.init_tools_schema", fake_init_tools_schema)
    monkeypatch.setattr(
        "covalve.runtime.pipeline.create_engine",
        lambda schema_colls, handlers, hooks, deps: {"schema_colls": schema_colls, "handlers": handlers, "hooks": hooks, "deps": deps},
    )

    config = make_pipeline_config(
        dependencies=InfrastructureRegistry(),
         tools_schema={"tool_a": {"priority": 0, "skippable": False, "intent": ["lookup"]}},
    )
    result = pipeline(make_linear_schema(), config)

    assert result["deps"] == config.dependencies
    assert calls["tools_schema"]["tool_a"]["priority"] == 0
