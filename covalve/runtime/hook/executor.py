from covalve.runtime.models.context import PipelineContext, STOP
from covalve.runtime.hook.context import ReadOnlyContext,HookReturn
import asyncio


async def hook_executor(on:str, states, cur_state, hooks: dict, ctx:PipelineContext) -> HookReturn:
    observe_hook = hooks["observer"][on][cur_state]
    intercept_hook = hooks["interceptor"][on][cur_state]

    copy_context = ReadOnlyContext(**ctx.model_copy(deep=True).model_dump())
    
    res = HookReturn(intercepted=False, to="", error="", event="")
    
    for fn in observe_hook:
        asyncio.create_task(fn(copy_context))
    
    for on_false, fn in intercept_hook:
        try:
            result = await fn(copy_context)

            if not result: 
                res.intercepted = True
                res.to = states[cur_state].transitions[on_false].to
                res.event = on_false
                break
        except Exception as e:
            res.intercepted = True
            res.to = STOP.INTERCEPTOR_ERROR
            res.error = str(e)
            res.event = STOP.INTERCEPTOR_ERROR
    return res
    