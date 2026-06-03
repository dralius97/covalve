# Changelog

## [0.1.1] - 2026-06-03

### Fixed
- `MCPResponse.content` now correctly typed as `list[ContentBlock]` union
  (TextContent | ImageContent | AudioContent | EmbeddedResource) per MCP spec
- `tools_data` in `PipelineContext` stores raw `list[ContentBlock]` instead of
  parsed JSON, preventing silent type coercion bypass via Pydantic `model_copy`
- `_get_context_tools` in `main_llm` now returns tools context string (was returning None)
- `intent_context` lookup in `main_llm` now correctly scoped per tool via
  `tools_schema[tool_name]["intent"]`, fixing wrong context assignment when multiple tools present
- `tool_list` type corrected from `dict[int, list[str]]` to `dict[int, list[dict]]`
  to match actual structure produced by `TOOLS_MAPPER` (name + skippable per tool)

## [0.1.0] - 2026-05-29

### Added
- Initial release