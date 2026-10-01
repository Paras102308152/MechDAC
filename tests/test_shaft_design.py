import math

import pytest
from pydantic import ValidationError

from mechdac.core.schema import (
    DesignRequirementSpec,
    MaterialSpec,
    QuantityValue,
    ShaftLoadingSpec,
)
from mechdac.core.results import ShaftDesignResult
from mechdac.solvers.shafts import solve_shaft


def quantity(value: float, unit: str) -> QuantityValue:
    return QuantityValue(value=value, unit=unit)


def shaft_loading(moment: float, torque: float) -> ShaftLoadingSpec:
    return ShaftLoadingSpec(
        bending_moment=quantity(moment, "N*m"),
        torque=quantity(torque, "N*m"),
        material=MaterialSpec(
            name="test material",
            yield_strength=quantity(250, "MPa"),
        ),
        design_requirement=DesignRequirementSpec(minimum_factor_of_safety=2),
    )


def test_pure_bending_sizes_solid_round_shaft_for_target_yield_margin() -> None:
    spec = shaft_loading(moment=100, torque=0)

    result = solve_shaft(spec)

    expected_diameter = (32 * 100 * 2 / (math.pi * 250e6)) ** (1 / 3)
    assert result.minimum_required_diameter.to("m") == pytest.approx(expected_diameter)
    assert result.bending_stress.to("Pa") == pytest.approx(125e6)
    assert result.torsional_shear_stress.to("Pa") == pytest.approx(0)
    assert result.equivalent_stress.to("Pa") == pytest.approx(125e6)
    assert result.factor_of_safety == pytest.approx(2)


def test_combined_bending_and_torsion_meets_von_mises_requirement() -> None:
    spec = shaft_loading(moment=100, torque=50)

    result = solve_shaft(spec)

    diameter = result.minimum_required_diameter.to("m")
    bending_stress = 32 * 100 / (math.pi * diameter**3)
    torsional_shear = 16 * 50 / (math.pi * diameter**3)
    equivalent = math.sqrt(bending_stress**2 + 3 * torsional_shear**2)
    assert result.bending_stress.to("Pa") == pytest.approx(bending_stress)
    assert result.torsional_shear_stress.to("Pa") == pytest.approx(torsional_shear)
    assert result.equivalent_stress.to("Pa") == pytest.approx(equivalent)
    assert result.equivalent_stress.to("Pa") == pytest.approx(125e6)
    assert result.factor_of_safety == pytest.approx(2)


def test_pure_torsion_uses_torsional_stress_in_the_yield_check() -> None:
    result = solve_shaft(shaft_loading(moment=0, torque=50))

    diameter = result.minimum_required_diameter.to("m")
    expected_shear = 16 * 50 / (math.pi * diameter**3)
    assert result.bending_stress.to("Pa") == pytest.approx(0)
    assert result.torsional_shear_stress.to("Pa") == pytest.approx(expected_shear)
    assert result.equivalent_stress.to("Pa") == pytest.approx(math.sqrt(3) * expected_shear)
    assert result.factor_of_safety == pytest.approx(2)


def test_shaft_input_accepts_convertible_units_and_json_round_trip() -> None:
    spec = ShaftLoadingSpec(
        bending_moment=quantity(0.1, "kN*m"),
        torque=quantity(50, "N*m"),
        material=MaterialSpec(
            name="test material",
            yield_strength=quantity(250, "MPa"),
        ),
        design_requirement=DesignRequirementSpec(minimum_factor_of_safety=2),
    )

    restored = ShaftLoadingSpec.model_validate_json(spec.model_dump_json())
    result = solve_shaft(restored)
    restored_result = ShaftDesignResult.model_validate_json(result.model_dump_json())

    assert restored == spec
    assert restored_result == result
    assert result.calculation_trace
    assert result.solver_name == "mechdac.static_solid_shaft_yield"


def test_shaft_models_reject_wrong_dimensions_and_nonpositive_requirements() -> None:
    with pytest.raises(ValidationError, match=r"bending moment must have units compatible with N\*m"):
        ShaftLoadingSpec(
            bending_moment=quantity(100, "N"),
            torque=quantity(0, "N*m"),
            material=MaterialSpec(
                name="test material",
                yield_strength=quantity(250, "MPa"),
            ),
            design_requirement=DesignRequirementSpec(minimum_factor_of_safety=2),
        )

    with pytest.raises(ValidationError):
        DesignRequirementSpec(minimum_factor_of_safety=0)


def test_sizing_rejects_zero_combined_load() -> None:
    with pytest.raises(ValueError, match="nonzero bending moment or torque"):
        solve_shaft(shaft_loading(moment=0, torque=0))
