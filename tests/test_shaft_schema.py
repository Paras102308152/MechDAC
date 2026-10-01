import pytest
from pydantic import ValidationError

from mechdac.core.schema import DesignRequirementSpec, MaterialSpec, QuantityValue, ShaftLoadingSpec


def test_shaft_loading_spec_accepts_physical_units_and_round_trips_json() -> None:
    spec = ShaftLoadingSpec(
        bending_moment=QuantityValue(value=0.1, unit="kN*m"),
        torque=QuantityValue(value=50, unit="N*m"),
        material=MaterialSpec(
            name="generic steel",
            yield_strength=QuantityValue(value=250, unit="MPa"),
        ),
        design_requirement=DesignRequirementSpec(minimum_factor_of_safety=2),
    )

    restored = ShaftLoadingSpec.model_validate_json(spec.model_dump_json())

    assert restored == spec
    assert restored.bending_moment.to("N*m") == pytest.approx(100)
    assert restored.material.yield_strength.to("Pa") == pytest.approx(250e6)


def test_material_and_shaft_schema_reject_physically_invalid_values() -> None:
    with pytest.raises(ValidationError, match="yield strength must be positive"):
        MaterialSpec(name="invalid", yield_strength=QuantityValue(value=0, unit="Pa"))
    with pytest.raises(ValidationError, match="compatible with N\\*m"):
        ShaftLoadingSpec(
            bending_moment=QuantityValue(value=100, unit="N"),
            torque=QuantityValue(value=10, unit="N*m"),
            material=MaterialSpec(
                name="generic steel", yield_strength=QuantityValue(value=250, unit="MPa")
            ),
            design_requirement=DesignRequirementSpec(minimum_factor_of_safety=2),
        )


def test_shaft_schema_rejects_unknown_nested_fields() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        MaterialSpec(
            name="generic steel",
            yield_strength=QuantityValue(value=250, unit="MPa"),
            ultimate_strength=QuantityValue(value=400, unit="MPa"),
        )


def test_design_requirement_rejects_nonpositive_or_nonfinite_safety_factor() -> None:
    for value in (0, -1, float("inf"), float("nan")):
        with pytest.raises(ValidationError):
            DesignRequirementSpec(minimum_factor_of_safety=value)
