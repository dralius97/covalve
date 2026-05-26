from runtime.executor.error_counter import factory_error_counter
from runtime.executor.tools_executor import factory_execute_tools
from runtime.executor.analyze_query import factory_analyzer
from runtime.executor.error import factory_internal_error
from runtime.executor.retrieve_conv import factory_retrieve_memmory
from runtime.executor.fallback import factory_fallback
from runtime.executor.tools_mapper import factory_tools_mapper
from runtime.executor.main_llm import factory_main_llm
from runtime.executor.save_data import factory_save_data



handlersRegistry = {
    "RETRIEVE_PREVIOUS_CONVERSATION": factory_retrieve_memmory,
    "ANALYZE": factory_analyzer,
    "ERROR_COUNTER": factory_error_counter,
    "INTERNAL_SERVER_ERROR": factory_internal_error,
    "TOOLS_MAPPER": factory_tools_mapper,
    "EXECUTE_TOOLS": factory_execute_tools,
    "FALLBACK": factory_fallback,
    "MAIN_LLM": factory_main_llm,
    "SAVE_DATA_TO_PERSISTENCE": factory_save_data,
}