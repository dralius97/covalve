from datetime import datetime
import hashlib
import time
from runtime.models.context import PipelineContext, ArgsCtx, ReturnSchema, STOP
from infrastructure.contract import InfrastructureRegistry
from runtime.models.logs import StateLog
import asyncio


def _init_context(query, session_id) -> tuple[str, str, PipelineContext]:
        new_session_id = session_id
        now = datetime.now()
        traceId = hashlib.sha256(f"traceId-{query}-{now}".encode('utf-8')).hexdigest()
        if new_session_id is None:
            new_session_id  = hashlib.sha256(f"{query}-{now}".encode('utf-8')).hexdigest()

        new_contex = PipelineContext(is_error=False,query=query,session_id=new_session_id ,current_time=now,traceId=traceId)
        return (traceId, new_session_id, new_contex)
        

async def _execute_state(states:dict, handlers, args_ctx:ArgsCtx) -> tuple[str, str, PipelineContext, str]:
    error = ""
    try:
        result:ReturnSchema = await handlers(args_ctx)
        running_context: PipelineContext = result.context
        if result.event not in states[args_ctx.state]["transitions"] and not result.event == STOP.HANDLER_ERROR:
            event_emmited = result.event
            current_state = STOP.INVALID_EVENT
        else:
            event_emmited = result.event
            current_state = states[args_ctx.state]["transitions"][event_emmited]["to"]
    except Exception as e:
        event_emmited = STOP.HANDLER_ERROR 
        running_context = args_ctx.context
        current_state = STOP.HANDLER_ERROR 
        error = str(e)

    return (event_emmited, current_state, running_context, error)

        
def _fire_state_log(deps:InfrastructureRegistry, log_data: StateLog) -> None:
    asyncio.create_task(deps.log.state_log(log_data))



def create_engine(schema:dict, handlers:dict, deps:InfrastructureRegistry):
    async def engine(query, session_id=None):
        stop_state = [schema["FINAL"], STOP.INVALID_EVENT, STOP.HANDLER_ERROR]     
        traceId, new_session_id, new_context = _init_context(query, session_id)
        running_context = new_context

        current_state = schema["INITIAL"]   
        cur_state_log = schema["INITIAL"]
        while current_state not in stop_state:

            args_ctx = ArgsCtx(state=current_state, context=running_context)
            handler = handlers[current_state]

            start = time.perf_counter()
            event_emmited, current_state, running_context, error = await _execute_state(schema["states"], handler, args_ctx)


            log_data = StateLog(
                session_id=new_session_id,
                traceId=traceId,
                current_state=cur_state_log,
                event= event_emmited,
                error= error,
                next_state=current_state,
                time_executed=datetime.now(),
                duration_ms = (time.perf_counter() - start) * 1000
            )

            _fire_state_log(deps, log_data)

            cur_state_log = current_state
        return running_context

    return engine
    
    