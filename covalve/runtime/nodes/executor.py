# covalve/runtime/nodes/executor

from typing import Callable
from collections import defaultdict
from covalve.runtime.nodes.schema import (
    NodeContext, ReadOnlyFields, ConversationFields,
    ToolsFields, ResponseFields, ErrorFields,
    ReturnContext, NodesConfig, ReadsList
)
from covalve.runtime.models.context import ArgsCtx, ReturnSchema, PipelineContext
from covalve.infrastructure.contract import InfrastructureRegistry
from covalve.runtime.nodes.registry import NodesRegistry


class CustomNodes:
    def __init__(self, nodes:NodesRegistry)->None:
        self._raw_node_collections = nodes.nodes_collection
        self._node_collections:dict = defaultdict(str)
        self.CATEGORY_FIELDS = {
            "tools": ["tools_data", "tool_list", "executed_tools"],
            "response": ["response", "summarize", "is_clarification", 
                         "fallback_content", "guardrail_rejection"],
            "errors": ["error", "last_error_emitted"],
        }
        self._init()

    def _init(self):
        for config, call in self._raw_node_collections:
            name = config.name
            self._node_collections[name] = self._make_node_factory(config, call)
    
    def _build_node_context(self, reads: list[ReadsList], ctx: PipelineContext) -> NodeContext:
        readonly = ReadOnlyFields(
            query=ctx.query,
            session_id=ctx.session_id,
            current_time=ctx.current_time,
            traceId=ctx.traceId
        )

        conversation = ConversationFields(
            background=ctx.background,
            metadata=ctx.metadata
        ) if ReadsList.CONV in reads else None

        tools = ToolsFields(
            tools_data=ctx.tools_data,
            executed_tools=ctx.executed_tools,
            tool_list=ctx.tool_list
        ) if ReadsList.TOOLS in reads else None

        response = ResponseFields(
            response=ctx.response,
            summarize=ctx.summarize,
            is_clarification=ctx.is_clarification,
            fallback_content=ctx.fallback_content,
            guardrail_rejection=ctx.guardrail_rejection
        ) if ReadsList.RESPONSE in reads else None

        errors = ErrorFields(
            error=ctx.error,
            last_error_emitted=ctx.last_error_emitted
        ) if ReadsList.ERROR in reads else None

        return NodeContext(
            readonly=readonly,
            conversation=conversation,
            tools=tools,
            response=response,
            errors=errors,
        )
    
    def _handling_nested_context(self, field,existing, incoming):
        merged = existing
        if field == "executed_tools" and existing is not None:
            merged = {
                "success_tools": existing["success_tools"] + incoming["success_tools"],
                "skipped_tools": existing["skipped_tools"] + incoming["skipped_tools"],
            }

        return merged

    def _merge_return_context(self, result: ReturnContext, ctx: PipelineContext) -> PipelineContext:
        copy_context = ctx.model_copy(deep=True).model_dump()
        dump_result = result.model_dump()

        for category, fields in self.CATEGORY_FIELDS.items():
            category_data = dump_result.get(category)
            if category_data is None:
                continue
            for field in fields:
                incoming = category_data.get(field)
                if incoming is None:
                    continue
                existing = copy_context.get(field)
                if field in ["executed_tools"]:
                    copy_context[field] = self._handling_nested_context(field,existing,incoming)
                elif isinstance(existing, dict):
                    copy_context[field] = {**existing, **incoming}
                elif isinstance(existing, list):
                    copy_context[field] = existing + incoming
                else:
                    copy_context[field] = incoming

        if result.local is not None:
            copy_context["local"] = {**copy_context["local"],**result.local}

        return PipelineContext.model_validate(copy_context)



    def _make_node_factory(self, config: NodesConfig, fn: Callable) -> Callable:
        def factory(deps: InfrastructureRegistry):
            async def handle(args: ArgsCtx) -> ReturnSchema:
                copy_context = args.context.model_copy(deep=True)
                node_ctx = self._build_node_context(config.reads, copy_context)

                result: ReturnContext = await fn(node_ctx)

                merged = self._merge_return_context(result, copy_context)
                return ReturnSchema(event=result.event, context=merged)

            return handle
        return factory
    
    def get_nodes(self):
        return self._node_collections
    