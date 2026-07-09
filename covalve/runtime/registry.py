from covalve.runtime.executor.error_counter import factory_error_counter
from covalve.runtime.executor.tools_executor import factory_execute_tools
from covalve.runtime.executor.analyze_query import factory_analyzer
from covalve.runtime.executor.error import factory_internal_error
from covalve.runtime.executor.retrieve_conv import factory_retrieve_memmory
from covalve.runtime.executor.fallback import factory_fallback
from covalve.runtime.executor.tools_mapper import factory_tools_mapper
from covalve.runtime.executor.main_llm import factory_main_llm
from covalve.runtime.executor.save_data import factory_save_data
from covalve.runtime.executor.guardrail import factory_guardrails
from covalve.runtime.executor.attachment_assembler import factory_attachment_assembler




handlersRegistry = {
    "ATTACHMENT_ASSEMBLER": factory_attachment_assembler,
    "RETRIEVE_PREVIOUS_CONVERSATION": factory_retrieve_memmory,
    "ANALYZE": factory_analyzer,
    "ERROR_COUNTER": factory_error_counter,
    "INTERNAL_SERVER_ERROR": factory_internal_error,
    "TOOLS_MAPPER": factory_tools_mapper,
    "EXECUTE_TOOLS": factory_execute_tools,
    "FALLBACK": factory_fallback,
    "MAIN_LLM": factory_main_llm,
    "SAVE_DATA_TO_PERSISTENCE": factory_save_data,
    "GUARDRAIL": factory_guardrails
}