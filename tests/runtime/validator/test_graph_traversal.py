import pytest
from pydantic import ValidationError
from covalve.runtime.validator.graph_traversal import validate_graph
from covalve.runtime.models.schema import CoreSchema


def test_validate_graph_accepts_linear_graph():
    schema = CoreSchema.model_validate({
        "INITIAL": "START",
        "FINAL": "END",
        "states": {
            "START": {"transitions": {"NEXT": {"to": "MIDDLE"}}},
            "MIDDLE": {"transitions": {"NEXT": {"to": "END"}}},
            "END": {"transitions": {}},
        },
    })

    assert validate_graph(schema) is True


def test_validate_graph_rejects_missing_keys():
    with pytest.raises(ValidationError):
        validate_graph(CoreSchema.model_validate({"states": {}}))


def test_validate_graph_rejects_unreachable_states():
    schema = CoreSchema.model_validate({
        "INITIAL": "START",
        "FINAL": "END",
        "states": {
            "START": {"transitions": {"NEXT": {"to": "END"}}},
            "ISOLATED": {"transitions": {}},
            "END": {"transitions": {}},
        },
    })

    assert validate_graph(schema) is False
