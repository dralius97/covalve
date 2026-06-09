# Contributing to covalve

## Requirements

- Python 3.10+
- pip

## Setup

```bash
git clone https://github.com/dralius97/covalve
cd covalve
pip install -e ".[dev]"
pip install -r requirements-dev.txt
```

## Project Structure

```
covalve/
├── runtime/
│   ├── engine.py
│   ├── pipeline.py
│   ├── registry.py
│   ├── init.py
│   ├── models/
│   ├── executor/
│   ├── validator/
│   └── hook/
├── infrastructure/
│   ├── base/
│   └── contract.py
├── schemas/
│   └── schema.json
examples/
tests/
ADR/
```

## Running Tests

```bash
pytest
```

For verbose output:

```bash
pytest -v
```

## Writing Tests

Tests live in `tests/`. Mirror the source structure — for example, tests for
`covalve/runtime/engine.py` go in `tests/runtime/test_engine.py`.

covalve is async-heavy. Use `pytest-asyncio` for async test cases:

```python
import pytest

@pytest.mark.asyncio
async def test_something():
    result = await some_async_function()
    assert result is not None
```

`asyncio_mode = "auto"` is already configured in `pyproject.toml`, so the
`@pytest.mark.asyncio` decorator is optional — but explicit is preferred.

## Architecture Decisions

Before making significant changes, read the ADRs in `ADR/`. Key ones:

- **ADR-001** — FSM as core execution model
- **ADR-002** — Python + asyncio + Pydantic
- **ADR-003** — Hook system (decorator, observer, interceptor)
- **ADR-004** — GUARDRAIL as optional node
- **ADR-005** — No direct mutation (`model_copy(deep=True)`)
- **ADR-006** — TERMINAL_RESPONSE as an Optional Core Node
- **ADR-007** — PipelineContext Contract Clarity
- **ADR-008** — Pipeline Cancellation via asyncio.Event
- **ADR-009** — Domain Routing via Graph

If your change introduces a new architectural pattern or overrides an existing
decision, propose a new ADR before implementing.

## Build

```bash
hatch build
```

Output goes to `dist/`.

## Release (maintainers only)

1. Bump `version` in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Build and upload:

```bash
hatch build
twine upload dist/*
```

## Commit Convention

covalve uses [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add OUTPUT_BUILDER node
fix: _get_context_tools missing return statement
docs: update ADR-006
chore: bump version to 0.1.1
```