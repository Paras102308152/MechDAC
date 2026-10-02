"""Analytical checks for external spur and helical gear pair calculations."""

import math

import pytest
from pydantic import ValidationError

from mechdac.core.schema import HelicalGearPairSpec, SpurGearPairSpec
from mechdac.core.units import QuantityValue
from mechdac.solvers.gears import solve_helical_gear, solve_spur_gear


def q(value: float, unit: str) -> QuantityValue:
    return QuantityValue(value=value, unit=unit)


def test_spur_pair_converts_units_and_preserves_ideal_speed_torque_and_power() -> None:
    spec = SpurGearPairSpec(
        module=q(0.5, "cm"),
        pinion_teeth=20,
        gear_teeth=60,
        pressure_angle=q(20, "degree"),
        input_power=q(3.5, "kW"),
        pinion_speed=q(700, "rpm"),
    )

    result = solve_spur_gear(spec)

    assert result.gear_ratio == pytest.approx(3)
    assert result.pinion_pitch_diameter.to("m") == pytest.approx(0.1)
    assert result.gear_pitch_diameter.to("m") == pytest.approx(0.3)
    assert result.center_distance.to("m") == pytest.approx(0.2)
    assert result.output_speed.to("rpm") == pytest.approx(700 / 3)
    assert result.input_torque.to("N*m") == pytest.approx(47.74648293, rel=1e-8)
    assert result.output_torque.to("N*m") == pytest.approx(143.23944878, rel=1e-8)
    assert result.tangential_force.to("N") == pytest.approx(954.92965855, rel=1e-8)
    assert result.radial_force.to("N") == pytest.approx(347.56597153, rel=1e-8)
    assert result.output_speed.to("rad/s") * result.output_torque.to("N*m") == pytest.approx(
        result.input_torque.to("N*m") * 700 * 2 * math.pi / 60
    )


def test_spur_example_17_2_mesh_force_values_match_bhandari() -> None:
    # Bhandari, Ch. 17, Ex. 17.2, pp. 660-661. Model the A-B mesh, not the
    # complete idler train: the solver has one pair and reports magnitudes.
    result = solve_spur_gear(
        SpurGearPairSpec(
            module=q(5, "mm"),
            pinion_teeth=30,
            gear_teeth=60,
            pressure_angle=q(20, "degree"),
            input_power=q(3.5, "kW"),
            pinion_speed=q(700, "rpm"),
        )
    )

    assert result.pinion_pitch_diameter.to("mm") == pytest.approx(150, abs=0.01)
    assert result.gear_pitch_diameter.to("mm") == pytest.approx(300, abs=0.01)
    assert result.input_torque.to("N*mm") == pytest.approx(47746.48, abs=0.02)
    assert result.tangential_force.to("N") == pytest.approx(636.62, abs=0.02)
    assert result.radial_force.to("N") == pytest.approx(231.71, abs=0.03)


def test_helical_example_18_2_matches_bhandari_force_components() -> None:
    # Bhandari, Ch. 18, Ex. 18.2, pp. 699-700. Printed values are rounded;
    # force comparisons use tolerances consistent with that precision.
    spec = HelicalGearPairSpec(
        normal_module=q(5, "mm"),
        pinion_teeth=20,
        gear_teeth=30,
        normal_pressure_angle=q(20, "degree"),
        helix_angle=q(30, "degree"),
        input_power=q(5, "kW"),
        pinion_speed=q(720, "rpm"),
    )

    result = solve_helical_gear(spec)

    assert result.pinion_pitch_diameter.to("mm") == pytest.approx(115.47, abs=0.01)
    assert result.gear_pitch_diameter.to("mm") == pytest.approx(173.21, abs=0.01)
    assert result.input_torque.to("N*mm") == pytest.approx(66314.56, abs=0.02)
    assert result.output_speed.to("rpm") == pytest.approx(480)
    assert result.tangential_force.to("N") == pytest.approx(1148.6, abs=0.15)
    assert result.axial_force.to("N") == pytest.approx(663.14, abs=0.15)
    assert result.radial_force.to("N") == pytest.approx(482.73, abs=0.15)
    assert type(result).model_validate_json(result.model_dump_json()) == result


def test_gear_input_and_result_json_round_trip_preserves_trace_and_metadata() -> None:
    spec = SpurGearPairSpec(
        module=q(5, "mm"),
        pinion_teeth=20,
        gear_teeth=40,
        pressure_angle=q(20, "degree"),
        input_power=q(2, "kW"),
        pinion_speed=q(900, "rpm"),
    )

    result = solve_spur_gear(SpurGearPairSpec.model_validate_json(spec.model_dump_json()))
    restored = type(result).model_validate_json(result.model_dump_json())

    assert restored == result
    assert restored.solver_name == "mechdac.spur_gear_forces"
    assert restored.solver_version == "0.1.0"
    assert restored.calculation_trace
    assert all(entry.equation and entry.substitution for entry in restored.calculation_trace)
    assert restored.assumptions
    assert restored.model_dump(mode="json")["warnings"] == []


@pytest.mark.parametrize(
    "values",
    [
        {"module": {"value": 5, "unit": "N"}},
        {"pinion_teeth": 0},
        {"pressure_angle": {"value": 90, "unit": "degree"}},
        {"unexpected": 1},
    ],
)
def test_spur_spec_rejects_invalid_or_unknown_values(values: dict) -> None:
    data = {
        "module": {"value": 5, "unit": "mm"},
        "pinion_teeth": 20,
        "gear_teeth": 40,
        "pressure_angle": {"value": 20, "unit": "degree"},
        "input_power": {"value": 2, "unit": "kW"},
        "pinion_speed": {"value": 900, "unit": "rpm"},
    }
    data.update(values)

    with pytest.raises(ValidationError):
        SpurGearPairSpec.model_validate(data)


def test_helical_spec_rejects_zero_helix_angle() -> None:
    with pytest.raises(ValidationError):
        HelicalGearPairSpec(
            normal_module=q(5, "mm"),
            pinion_teeth=20,
            gear_teeth=40,
            normal_pressure_angle=q(20, "degree"),
            helix_angle=q(0, "degree"),
            input_power=q(2, "kW"),
            pinion_speed=q(900, "rpm"),
        )


def test_spur_solver_rejects_speed_below_supported_numeric_range() -> None:
    spec = SpurGearPairSpec(
        module=q(5, "mm"),
        pinion_teeth=20,
        gear_teeth=40,
        pressure_angle=q(20, "degree"),
        input_power=q(2, "kW"),
        pinion_speed=q(5e-324, "rpm"),
    )

    with pytest.raises(ValueError, match="supported numeric range"):
        solve_spur_gear(spec)
