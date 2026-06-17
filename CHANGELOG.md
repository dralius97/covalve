# Changelog

## [0.2.7] - 2026-06-17

### bugfix
- intent validation convert to lowercase to solve case sensitive issue


## [0.2.6] - 2026-06-15

### bugfix
- fix typo conversational -> conversation at prompt base for analyzer nodes


## [0.2.5] - 2026-06-15

### bugfix
- pydantic extraction for schema transition in engine.py
- handle None context at merging metadata from custom node

## [0.2.3] - 2026-06-15

### bugfix
- Use pathlib for BasePrompt

## [0.2.2] - 2026-06-15

### Changed
- Expanded the package root API exports in `covalve/__init__.py` to expose
  additional runtime models and node schema helpers for direct imports

## [0.2.1] - 2026-06-15

### Added
- Structured query analysis fields for `metric`, `entities`, and `filters`
  in `RuntimeMetadata` / `ContentUnit`
- Query analysis prompt base loader in `covalve.runtime.prompt_base.prompt`
- Shared analyzer prompt template under `covalve/runtime/prompt_base/`

### Changed
- `analyze_query` now injects the shared analyzer prompt and validates the
  returned payload with `RuntimeMetadata.model_validate(...)`
- Query analysis examples and schema guidance were expanded to cover
  aggregation, negation, and conversational cases
- `pyproject.toml` version bumped to `0.2.1`

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
