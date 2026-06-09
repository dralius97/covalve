import asyncio

import pytest

from covalve.runtime.hook.context import ReadOnlyContext
from covalve.runtime.hook.executor import hook_executor
from covalve.runtime.hook.registry import HookOn, HookRegistry, InterceptorConfig, ObserverConfig
from tests.helpers import make_empty_hooks, make_minimal_schema, make_pipeline_context


def test_hook_registry_collects_observer_and_interceptor_configs():
    registry = HookRegistry()

    @registry.observer(["START"], HookOn.ENTER)
    async def observer(_ctx):
        return None

    @registry.interceptor("START", HookOn.EXIT, "NEXT")
    async def interceptor(_ctx):
        return True

    assert registry.observer_collection[0][0] == ObserverConfig(nodes=["START"], on=HookOn.ENTER)
    assert registry.interceptor_collection[0][0] == InterceptorConfig(node="START", on=HookOn.EXIT, on_false="NEXT")
    assert registry.observer_collection[0][1] is observer
    assert registry.interceptor_collection[0][1] is interceptor


@pytest.mark.asyncio
async def test_hook_executor_schedules_observers_and_intercepts_on_false(monkeypatch):
    observed = []

    async def observer(ctx):
        observed.append(ctx.query)

    async def interceptor(_ctx):
        return False

    hooks = make_empty_hooks()
    hooks["observer"][HookOn.ENTER]["START"].append(observer)
    hooks["interceptor"][HookOn.ENTER]["START"].append(("NEXT", interceptor))
    states = make_minimal_schema().states
    ctx = make_pipeline_context()

    loop = asyncio.get_running_loop()
    monkeypatch.setattr(asyncio, "create_task", lambda coro: loop.create_task(coro))

    result = await hook_executor(HookOn.ENTER, states, "START", hooks, ctx)
    await asyncio.sleep(0)

    assert observed == ["what is the answer"]
    assert result.intercepted is True
    assert result.to == "END"
    assert result.event == "NEXT"


@pytest.mark.asyncio
async def test_hook_executor_handles_interceptor_exceptions():
    async def interceptor(_ctx):
        raise RuntimeError("boom")

    hooks = make_empty_hooks()
    hooks["interceptor"][HookOn.EXIT]["START"].append(("NEXT", interceptor))
    states = make_minimal_schema().states

    result = await hook_executor(HookOn.EXIT, states, "START", hooks, make_pipeline_context())

    assert result.intercepted is True
    assert result.to == "INTERCEPTOR_ERROR"
    assert result.event == "INTERCEPTOR_ERROR"
    assert "boom" in result.error


def test_read_only_context_prevents_mutation():
    ctx = ReadOnlyContext(**make_pipeline_context().model_dump())

    with pytest.raises(Exception):
        ctx.query = "changed"
