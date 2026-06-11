import pytest

from covalve.infrastructure.contract import InfrastructureRegistry
from covalve.runtime.hook import hooks
from covalve.runtime.hook.registry import InterceptorConfig, ObserverConfig, HookOn
from covalve.runtime.init import init_handlers, init_hooks, init_tools_schema
from covalve.runtime.models.context import PipelineConfig
from covalve.runtime.models.schema import CoreSchema
from tests.helpers import make_minimal_schema, make_pipeline_config, make_tools_schema


def test_init_handlers_builds_handlers_and_requires_dependencies(monkeypatch):
    from covalve.runtime import init as init_module

    monkeypatch.setitem(init_module.handlersRegistry, "START", lambda deps: f"handler-with-{deps}")
    config = make_pipeline_config(dependencies=InfrastructureRegistry())
    schema = CoreSchema.model_validate({"INITIAL":"START","FINAL":"END","states": {"START": {"transitions": {"NEXT": {"to": "END"}}}}})

    handlers = init_handlers(schema, config)

    assert handlers["START"].startswith("handler-with-")

def test_init_handlers_custom_node_conflicts_with_native(monkeypatch):
    from covalve.runtime import init as init_module
    from covalve.runtime.nodes.executor import CustomNodes
    from covalve.runtime.nodes.schema import NodesConfig, ReadsList

    fake_nodes = {"START": lambda deps: "conflict"}
    monkeypatch.setattr(
        CustomNodes, "get_nodes", lambda self: fake_nodes
    )
    monkeypatch.setitem(init_module.handlersRegistry, "START", lambda deps: "handler")

    schema = CoreSchema.model_validate({
        "INITIAL": "START",
        "FINAL": "END",
        "states": {"START": {"transitions": {"NEXT": {"to": "END"}}}}
    })

    with pytest.raises(ValueError, match="conflict"):
        init_handlers(schema, make_pipeline_config(dependencies=InfrastructureRegistry()))


def test_init_handlers_rejects_missing_dependencies(monkeypatch):
    from covalve.runtime import init as init_module

    monkeypatch.setitem(init_module.handlersRegistry, "START", lambda deps: "handler")
    schema = CoreSchema.model_validate({"INITIAL":"START","FINAL":"END","states": {"START": {"transitions": {"NEXT": {"to": "END"}}}}})

    with pytest.raises(ValueError, match="InfrastructureRegistry is required"):
        init_handlers(schema, PipelineConfig())


def test_init_hooks_registers_observer_and_interceptor(monkeypatch):
    async def observer(_ctx):
        return None

    async def interceptor(_ctx):
        return True

    monkeypatch.setattr(
        hooks,
        "_observer_registry",
        [(ObserverConfig(nodes=["START"], on=HookOn.ENTER), observer)],
    )
    monkeypatch.setattr(
        hooks,
        "_interceptor_registry",
        [(InterceptorConfig(node="START", on=HookOn.EXIT, on_false="NEXT"), interceptor)],
    )

    active = init_hooks(make_minimal_schema())

    assert active["observer"][HookOn.ENTER]["START"] == [observer]
    assert active["interceptor"][HookOn.EXIT]["START"] == [("NEXT", interceptor)]


def test_init_hooks_rejects_invalid_nodes(monkeypatch):
    monkeypatch.setattr(hooks, "_observer_registry", [])
    monkeypatch.setattr(hooks, "_interceptor_registry", [])

    from covalve.runtime.hook.registry import ObserverConfig

    monkeypatch.setattr(
        hooks,
        "_observer_registry",
        [(ObserverConfig(nodes=["UNKNOWN"], on=HookOn.ENTER), lambda _ctx: None)],
    )

    with pytest.raises(ValueError, match="invalid nodes"):
        init_hooks(make_minimal_schema())


def test_init_tools_schema_validates_shape():
    init_tools_schema(make_tools_schema())


def test_init_tools_schema_rejects_invalid_intent_list():
    with pytest.raises(ValueError, match="Invalid tools_schema"):
        init_tools_schema(
            {"tool_a": {"priority": 1, "skippable": True, "intent": []}}
        )
