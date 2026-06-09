from covalve.runtime.models.context import  ArgsCtx, ReturnSchema 
from covalve.runtime.models.io import DataContent 
from covalve.infrastructure.contract import InfrastructureRegistry
import logging
logger = logging.getLogger(__name__)

def factory_save_data(deps:InfrastructureRegistry):
    if deps.memory is None or deps.cache is None:
        raise ValueError("MemoryStoreBase and CacheBase is required for SAVE_DATA_TO_PERSISTENCE")
    
    memory = deps.memory 
    cache = deps.cache


    async def handle_save_data_to_persistence(ctx: ArgsCtx) -> ReturnSchema: 
        copy_context = ctx.context.model_copy(deep=True)
        session_id = copy_context.session_id
        data_content = DataContent(
            session_id= session_id,
            metadata= [unit.model_dump() for unit in copy_context.metadata.content] if copy_context.metadata else [],
            user= copy_context.query,
            assistance= copy_context.response.text if copy_context.response else "",
            traceId= copy_context.traceId,
            summarize= copy_context.summarize,
            data= copy_context.tools_data
        )
        try:
            await memory.save_conv(data_content)
        except Exception as e:
            logger.warning("failed to save conversation traceId: %s", copy_context.traceId)
            logger.debug("failed metadata: %s", copy_context.metadata.model_dump() if copy_context.metadata else "")
        await cache.delete(f"{session_id}:ANALYZE")
        await cache.delete(f"{session_id}:EXECUTE_TOOLS")

        return ReturnSchema(event="NEXT", context=copy_context)
    return handle_save_data_to_persistence
