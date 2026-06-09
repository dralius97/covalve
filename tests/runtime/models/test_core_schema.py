import pytest
from pydantic import ValidationError

schema_module = pytest.importorskip("covalve.runtime.models.schema")

CoreSchema = schema_module.CoreSchema
StateConfig = schema_module.StateConfig
Transition = schema_module.Transition


def test_core_schema_can_be_built_from_valid_dict():
    schema = CoreSchema.model_validate(
        {
            "INITIAL": "START",
            "FINAL": "END",
            "states": {
                "START": {
                    "transitions": {
                        "NEXT": {"to": "END"},
                    }
                },
                "END": {"transitions": {}},
            },
        }
    )

    assert schema.INITIAL == "START"
    assert schema.FINAL == "END"
    assert schema.states["START"].transitions["NEXT"].to == "END"


def test_core_schema_rejects_missing_initial_or_final():
    with pytest.raises(ValidationError):
        CoreSchema.model_validate({"states": {}})


def test_schema_hierarchy_uses_transition_stateconfig_coreschema():
    transition = Transition.model_validate({"to": "END"})
    state = StateConfig.model_validate({"transitions": {"NEXT": {"to": "END"}}})
    schema = CoreSchema.model_validate(
        {
            "INITIAL": "START",
            "FINAL": "END",
            "states": {
                "START": {"transitions": {"NEXT": {"to": "END"}}},
                "END": {"transitions": {}},
            },
        }
    )

    assert transition.to == "END"
    assert state.transitions["NEXT"].to == "END"
    assert schema.states["START"].transitions["NEXT"].to == "END"
