import hashlib
import time
import asyncio
from typing import Optional
from datetime import datetime
from covalve.runtime.models.context import PipelineContext, ArgsCtx, ReturnSchema, STOP, SchemaCollections
from covalve.infrastructure.contract import InfrastructureRegistry
from covalve.runtime.models.logs import StateLog
from covalve.runtime.hook.executor import hook_executor
from covalve.runtime.hook.registry import HookOn


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
        if result.event not in states[args_ctx.state].transitions and not result.event == STOP.HANDLER_ERROR:
            event_emmited = result.event
            current_state = STOP.INVALID_EVENT
        else:
            event_emmited = result.event
            current_state =  states[args_ctx.state].transitions[event_emmited].to
    except Exception as e:
        event_emmited = STOP.HANDLER_ERROR 
        running_context = args_ctx.context
        current_state = STOP.HANDLER_ERROR 
        error = str(e)

    return (event_emmited, current_state, running_context, error)

        
def _fire_state_log(deps:InfrastructureRegistry, log_data: StateLog) -> None:
    if deps.log:
       asyncio.create_task(deps.log.state_log(log_data))



def create_engine(schemaCols:SchemaCollections, handlers:dict, hooks:dict, deps:Optional[InfrastructureRegistry] = None):
    core_schema = schemaCols.core_schema

    async def engine(query, session_id=None):
        stop_state = [core_schema.FINAL, STOP.INVALID_EVENT, STOP.HANDLER_ERROR, STOP.INTERCEPTOR_ERROR]     
        traceId, new_session_id, new_context = _init_context(query, session_id)
        running_context = new_context

        current_state = core_schema.INITIAL
        active_state = core_schema.INITIAL
        while current_state not in stop_state:
            error_string = ""
            args_ctx = ArgsCtx(state=current_state, context=running_context, schema_colls=schemaCols)
            handler = handlers[current_state]

            start = time.perf_counter()

            hook_result = await hook_executor(HookOn.ENTER,core_schema.states,current_state,hooks,running_context)
            if hook_result.intercepted:
                current_state = hook_result.to
                error_string = hook_result.error
                event_emmited = hook_result.event
            else:
                event_emmited, current_state, running_context, error_string = await _execute_state(core_schema.states, handler, args_ctx)

                hook_result = await hook_executor(HookOn.EXIT,core_schema.states,active_state,hooks,running_context)
                if hook_result.intercepted:
                    current_state = hook_result.to
                    error_string = hook_result.error
                    event_emmited = hook_result.event


            log_data = StateLog(
                session_id=new_session_id,
                traceId=traceId,
                current_state=active_state,
                event= event_emmited,
                error= error_string,
                next_state=current_state,
                time_executed=datetime.now(),
                duration_ms = (time.perf_counter() - start) * 1000
            )

            _fire_state_log(deps, log_data)

            active_state = current_state
        return running_context

    return engine
    
    