from pydantic import ValidationError

from covalve.runtime.models.metadata import ContentUnit, QueryIntent, RuntimeMetadata


def test_content_unit_normalizes_intent_and_confidence():
    unit = ContentUnit(
        intent="LOOKUP",
        composition_context="search docs",
        confidence=1.234,
    )

    assert unit.intent == QueryIntent.LOOKUP.value
    assert unit.confidence == 1.0


def test_content_unit_rejects_unknown_intent():
    try:
        ContentUnit(
            intent="unknown",
            composition_context="search docs",
            confidence=0.5,
        )
        assert False, "expected validation error"
    except ValidationError as exc:
        assert "invalid intent" in str(exc)


def test_runtime_metadata_holds_content_units():
    metadata = RuntimeMetadata(
        raw_query="what is new",
        content=[
            ContentUnit(
                intent="explain",
                composition_context="context",
                confidence=0.7,
            )
        ],
    )

    assert metadata.raw_query == "what is new"
    assert metadata.content[0].intent == "explain"
