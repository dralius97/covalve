import json
import hashlib
from datetime import datetime
from runtime.schema.schema import PipelineContext
from runtime.error.error_counter import handle_error_counter
from runtime.executor.tools_executor import handle_execute_tools
from runtime.executor.analyze_query import handle_analyze
from runtime.error.error import handle_internal_server_error
from runtime.executor.retrive_conv import handle_retrieve_previous_conversation
from runtime.executor.fallback import handle_fallback
from runtime.executor.tools_mapper import handle_tools_mapper
from runtime.executor.main_llm import handle_main_llm
from runtime.executor.save_data import handle_save_data_to_persistence


with open("./jsonSchema/schema.json") as data:
    schema = json.load(data)




handlers = {
    "RETRIVE_PREVIOUS_CONVERSATION": handle_retrieve_previous_conversation,
    "ANALYZE": handle_analyze,
    "ERROR_COUNTER": handle_error_counter,
    "INTERNAL_SERVER_ERROR": handle_internal_server_error,
    "TOOLS_MAPPER": handle_tools_mapper,
    "EXECUTE_TOOLS": handle_execute_tools,
    "FALLBACK": handle_fallback,
    "MAIN_LLM": handle_main_llm,
    "SAVE_DATA_TO_PERSISTENCE": handle_save_data_to_persistence,
}


async def runtime(query, session_id =None):
    now = datetime.now()
    traceId = hashlib.sha256(f"traceId-{query}-{now}".encode('utf-8')).hexdigest()
    if session_id  is None:
        session_id  = hashlib.sha256(f"{query}-{now}".encode('utf-8')).hexdigest()
    
    current_state = schema["INITIAL"]
    prev_context = PipelineContext(is_error=False,query=query,session_id=session_id ,current_time=now,traceId=traceId)

    while  current_state != schema["FINAL"]:

        result = await handlers[current_state](state = current_state, context = prev_context)

        prev_context = result.context
        if result.event not in schema["states"][current_state]["transitions"]:
            prev_context.is_error = True
            prev_context.error = {
                "type": "INVALID_EVENT",
                "state": current_state,
                "event": result.event
            }
            break
        current_state = schema["states"][current_state]["transitions"][result.event]["to"]

    return prev_context

