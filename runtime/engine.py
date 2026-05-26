from datetime import datetime
import hashlib
import time
from runtime.models.context import PipelineContext, ArgsCtx 
from infrastructure.contract import InfrastructureRegistry
from runtime.models.logs import StateLog
import asyncio

def create_runtime(schema:dict, handlers:dict, deps:InfrastructureRegistry):
    async def runtime(query, session_id=None):
        now = datetime.now()
        traceId = hashlib.sha256(f"traceId-{query}-{now}".encode('utf-8')).hexdigest()
        if session_id  is None:
            session_id  = hashlib.sha256(f"{query}-{now}".encode('utf-8')).hexdigest()

        current_state = schema["INITIAL"]
        prev_context = PipelineContext(is_error=False,query=query,session_id=session_id ,current_time=now,traceId=traceId)
        while  current_state != schema["FINAL"]:
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
                if result.event not in schema["states"][current_state]["transitions"]:
                    prev_context.is_error = True
                    prev_context.error = {
                        "type": "INVALID_EVENT",
                        "state": current_state,
                        "event": result.event
                    }
                    current_state = "INTERNAL_SERVER_ERROR"
                else:
                    prev_context = result.context
                    current_state = schema["states"][current_state]["transitions"][result.event]["to"]

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