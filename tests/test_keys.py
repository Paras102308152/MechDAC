"""Rectangular sunk-key strength checks and Bhandari Chapter 9 regression."""

import pytest
from pydantic import ValidationError

from mechdac.core.results import ShaftKeyResult
from mechdac.core.schema import (
    DesignRequirementSpec,
    MaterialSpec,
    ShaftKeySpec,
)
from mechdac.core.units import QuantityValue
from mechdac.solvers.keys import check_shaft_key


def q(value: float, unit: str) -> QuantityValue:
    return QuantityValue(value=value, unit=unit)


def key_spec(
    *,
    torque: QuantityValue | None = None,
    shaft_diameter: QuantityValue | None = None,
    key_width: QuantityValue | None = None,
    key_height: QuantityValue | None = None,
    key_length: QuantityValue | None = None,
    yield_strength: QuantityValue | None = None,
    minimum_factor_of_safety: float = 3,
) -> ShaftKeySpec:
    return ShaftKeySpec(
        torque=torque or q(475, "N*m"),
        shaft_diameter=shaft_diameter or q(50, "mm"),
        key_width=key_width or q(16, "mm"),
        key_height=key_height or q(10, "mm"),
        key_length=key_length or q(50, "mm"),
        material=MaterialSpec(
            name="commercial steel",
            yield_strength=yield_strength or q(230, "MPa"),
        ),
        design_requirement=DesignRequirementSpec(
            minimum_factor_of_safety=minimum_factor_of_safety,
        ),
    )


def _trace_step(result: ShaftKeyResult, prefix: str):
    return next(step for step in result.calculation_trace if step.name.startswith(prefix))


def test_bhandari_ch09_example_9_14_checks_stresses_lengths_and_factors() -> None:
    # Bhandari, Design of Machine Elements, Ch. 9 §9.13, Example 9.14, printed p. 352.
    result = check_shaft_key(key_spec())

    assert result.key_shear_stress.to("MPa") == pytest.approx(23.75)
    assert result.key_bearing_stress.to("MPa") == pytest.approx(76.0)
    assert result.required_length_in_shear.to("mm") == pytest.approx(30.98, abs=0.01)
    assert result.required_length_in_bearing.to("mm") == pytest.approx(49.56, abs=0.01)
    assert result.required_key_length.to("mm") == pytest.approx(49.56, abs=0.01)
    assert result.shear_factor_of_safety == pytest.approx(115 / 23.75)
    assert result.bearing_factor_of_safety == pytest.approx(230 / 76)
    assert "bearing controls" in _trace_step(result, "Governing").name.lower()
    assert result.warnings == ()


def test_key_solver_converts_mixed_units_and_emits_auditable_trace() -> None:
    result = check_shaft_key(
        key_spec(
            torque=q(0.475, "kN*m"),
            shaft_diameter=q(5, "cm"),
            key_width=q(1.6, "cm"),
            key_height=q(10, "mm"),
            key_length=q(5, "cm"),
            yield_strength=q(0.23, "GPa"),
        )
    )

    assert result.key_shear_stress.to("Pa") == pytest.approx(23.75e6)
    assert result.key_bearing_stress.to("Pa") == pytest.approx(76e6)
    assert len(result.calculation_trace) >= 8
    assert all(step.equation and step.substitution for step in result.calculation_trace)
    assert _trace_step(result, "Allowable key shear").result.to("MPa") == pytest.approx(230 / 6)
    assert _trace_step(result, "Allowable key bearing").result.to("MPa") == pytest.approx(230 / 3)


def test_shear_governs_when_its_required_length_exceeds_bearing_length() -> None:
    result = check_shaft_key(key_spec(key_width=q(10, "mm"), key_height=q(16, "mm")))

    assert result.required_length_in_shear.to("m") > result.required_length_in_bearing.to("m")
    assert result.required_key_length == result.required_length_in_shear
    assert "shear controls" in _trace_step(result, "Governing").name.lower()


def test_equal_key_dimensions_report_both_modes_as_governing() -> None:
    result = check_shaft_key(key_spec(key_width=q(10, "mm"), key_height=q(10, "mm")))

    assert result.required_length_in_shear.to("m") == pytest.approx(
        result.required_length_in_bearing.to("m")
    )
    assert result.required_key_length == result.required_length_in_shear
    assert "both modes govern" in _trace_step(result, "Governing").name.lower()


def test_short_provided_key_length_reports_warning_and_actual_safety_factors() -> None:
    result = check_shaft_key(key_spec(key_length=q(40, "mm")))

    assert result.required_key_length.to("mm") > 40
    assert result.bearing_factor_of_safety < 3
    assert any("shorter than the required length" in warning.lower() for warning in result.warnings)


def test_key_input_rejects_invalid_dimensions_and_incompatible_units() -> None:
    with pytest.raises(ValidationError, match="less than shaft diameter"):
        key_spec(key_width=q(50, "mm"))

    with pytest.raises(ValidationError, match="compatible with"):
        key_spec(torque=q(475, "N"))


def test_key_result_has_solver_metadata_assumptions_and_json_round_trip() -> None:
    result = check_shaft_key(key_spec())

    restored = ShaftKeyResult.model_validate_json(result.model_dump_json())
    assert restored == result
    assert result.solver_name == "mechdac.key_strength_check"
    assert result.solver_version
    assert result.assumptions
    assert result.calculation_trace
