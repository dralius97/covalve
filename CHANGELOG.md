# Changelog

## [0.2.0]

### Added
- Custom node interface via `covalve.runtime.nodes`, including `node.handler`,
  `NodeContext`, `ReturnContext`, and typed field groups for conversation,
  tools, response, and error reads/writes
- Runtime validation that custom node handlers return `ReturnContext`
- Support for selective context merging from custom nodes, including nested
  `local` updates and merged `tools_data` / `executed_tools` payloads

### Changed
- `PipelineConfig` no longer exposes `add_handlers` and `overrides`
- `init_handlers` now loads custom nodes from the node registry and rejects
  name conflicts with native handlers
- Public exports now include the custom node helper and typed node schemas

### Fixed
- `executed_tools` is merged instead of replaced, so successful and skipped
  tools from earlier nodes are preserved

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
