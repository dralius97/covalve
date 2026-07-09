from covalve.runtime.models.context import ArgsCtx, ReturnSchema
from covalve.runtime.models.infra import ContentBlock
from covalve.infrastructure.contract import InfrastructureRegistry


def factory_attachment_assembler(deps: InfrastructureRegistry):
    async def handle_attachment_assembler(ctx: ArgsCtx) -> ReturnSchema:
        copy_context = ctx.context.model_copy(deep=True)
        tools_data = copy_context.tools_data or {}

        attachments: list[ContentBlock] = [
            block
            for blocks in tools_data.values()
            for block in blocks
            if block.type != "text"
        ]

        if copy_context.response is not None:
            copy_context.response.attachment = attachments or None

        return ReturnSchema(event="NEXT", context=copy_context)

    return handle_attachment_assembler