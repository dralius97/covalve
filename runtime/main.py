import hashlib
import time
import asyncio
from datetime import datetime
from runtime.schema.schema import PipelineContext, ArgsCtx, StateLog
from plugins.registry import deps
from runtime.error.error_counter import factory_error_counter
from runtime.executor.tools_executor import factory_execute_tools
from runtime.executor.analyze_query import factory_analyzer
from runtime.error.error import factory_internal_error
from runtime.executor.retrieve_conv import factory_retrieve_memmory
from runtime.executor.fallback import factory_fallback
from runtime.executor.tools_mapper import factory_tools_mapper
from runtime.executor.main_llm import factory_main_llm
from runtime.executor.save_data import factory_save_data
from jsonSchema.jsonRegistry import core_schema




def main():
    handlers = {
        "RETRIEVE_PREVIOUS_CONVERSATION": factory_retrieve_memmory(deps),
        "ANALYZE": factory_analyzer(deps),
        "ERROR_COUNTER": factory_error_counter(deps),
        "INTERNAL_SERVER_ERROR": factory_internal_error(deps),
        "TOOLS_MAPPER": factory_tools_mapper(deps),
        "EXECUTE_TOOLS": factory_execute_tools(deps),
        "FALLBACK": factory_fallback(deps),
        "MAIN_LLM": factory_main_llm(deps),
        "SAVE_DATA_TO_PERSISTENCE": factory_save_data(deps),
    }

    async def runtime(query, session_id=None):
        now = datetime.now()
        traceId = hashlib.sha256(f"traceId-{query}-{now}".encode('utf-8')).hexdigest()
        if session_id  is None:
            session_id  = hashlib.sha256(f"{query}-{now}".encode('utf-8')).hexdigest()

        current_state = core_schema["INITIAL"]
        prev_context = PipelineContext(is_error=False,query=query,session_id=session_id ,current_time=now,traceId=traceId)
        while  current_state != core_schema["FINAL"]:
            temp_log_data = {
                "session_id": session_id,
                "traceId": traceId,
                "current_state": current_state,
                "error": None
            }
            start = time.perf_counter()

            try:
                result = await handlers[current_state](ArgsCtx(state = current_state, context = prev_context))
            except Exception as e:
                current_state = "INTERNAL_SERVER_ERROR"
                temp_log_data["error"] = str(e)
            else:
                temp_log_data["event"] = result.event
                if result.event not in core_schema["states"][current_state]["transitions"]:
                    prev_context.is_error = True
                    prev_context.error = {
                        "type": "INVALID_EVENT",
                        "state": current_state,
                        "event": result.event
                    }
                    current_state = "INTERNAL_SERVER_ERROR"
                else:
                    prev_context = result.context
                    current_state = core_schema["states"][current_state]["transitions"][result.event]["to"]

            asyncio.create_task(deps.log.state_log(StateLog( 
                session_id=session_id,
                traceId=traceId,
                current_state=temp_log_data['current_state'],
                event= temp_log_data.get("event", "NONE"),
                error= temp_log_data['error'],
                next_state=current_state,
                time_executed=datetime.now(),
                duration_ms = (time.perf_counter() - start) * 1000
                )))
            if prev_context.is_error: break

        return prev_context
    return runtime
