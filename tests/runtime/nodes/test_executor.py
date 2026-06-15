import pytest

from covalve.runtime.models.context import ExecutedTools
from covalve.runtime.models.infra import TextContent
from covalve.runtime.nodes import node
from covalve.runtime.nodes.executor import CustomNodes
from covalve.runtime.nodes.registry import NodesRegistry
from covalve.runtime.nodes.schema import (
    ConversationFields,
    NodeContext,
    ReturnContext,
    ToolsFields,
)
from tests.helpers import make_pipeline_context, make_runtime_metadata


def _make_custom_nodes() -> CustomNodes:
    return CustomNodes(NodesRegistry())


def test_merge_return_context_does_not_overwrite_existing_metadata_when_incoming_fields_are_none():
    custom_nodes = _make_custom_nodes()
    ctx = make_pipeline_context(metadata=make_runtime_metadata())
    original_metadata = ctx.metadata.model_copy(deep=True)

    result = ReturnContext(
        event="NEXT",
        conversation=ConversationFields(metadata=None, background=None),
    )

    merged = custom_nodes._merge_return_context(result, ctx)

    assert merged.metadata == original_metadata


def test_merge_return_context_merges_dict_fields_instead_of_replacing_them():
    custom_nodes = _make_custom_nodes()
    ctx = make_pipeline_context(
        tools_data={
            "tool_a": [TextContent(type="text", text="from-tool-a")],
        }
    )

    result = ReturnContext(
        event="NEXT",
        tools=ToolsFields(
            tools_data={
                "tool_b": [TextContent(type="text", text="from-tool-b")],
            }
        ),
    )

    merged = custom_nodes._merge_return_context(result, ctx)

    assert merged.tools_data == {
        "tool_a": [TextContent(type="text", text="from-tool-a")],
        "tool_b": [TextContent(type="text", text="from-tool-b")],
    }


def test_merge_return_context_appends_success_tools_instead_of_replacing_them():
    custom_nodes = _make_custom_nodes()
    ctx = make_pipeline_context(local={"unused": True})
    ctx.executed_tools = ExecutedTools(success_tools=["tool_a"], skipped_tools=[])

    result = ReturnContext(
        event="NEXT",
        tools=ToolsFields(
            executed_tools=ExecutedTools(success_tools=["tool_b"], skipped_tools=[]),
        ),
    )

    merged = custom_nodes._merge_return_context(result, ctx)

    assert merged.executed_tools.success_tools == ["tool_a", "tool_b"]


def test_merge_return_context_merges_local_instead_of_replacing_it():
    custom_nodes = _make_custom_nodes()
    ctx = make_pipeline_context(local={"key_a": 1})

    result = ReturnContext(
        event="NEXT",
        local={"key_b": 2},
    )

    merged = custom_nodes._merge_return_context(result, ctx)

    assert merged.local == {"key_a": 1, "key_b": 2}


def test_merge_return_context_initializes_local_when_missing():
    custom_nodes = _make_custom_nodes()
    ctx = make_pipeline_context(local=None)

    result = ReturnContext(
        event="NEXT",
        local={"key_b": 2},
    )

    merged = custom_nodes._merge_return_context(result, ctx)

    assert merged.local == {"key_b": 2}


def test_build_node_context_always_includes_readonly_and_omits_unread_categories():
    custom_nodes = _make_custom_nodes()
    ctx = make_pipeline_context()

    node_ctx = custom_nodes._build_node_context([], ctx)

    assert node_ctx.readonly.query == ctx.query
    assert node_ctx.conversation is None


def test_node_handler_rejects_functions_that_do_not_return_return_context():
    with pytest.raises(TypeError, match="must return ReturnContext"):

        @node.handler("BAD_NODE", [])
        async def bad_node(_ctx: NodeContext) -> str:
            return "not-a-return-context"
