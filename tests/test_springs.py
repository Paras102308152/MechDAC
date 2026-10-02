"""Static round-wire compression spring checks."""

import math

import pytest
from pydantic import ValidationError

from mechdac.core.results import CompressionSpringResult
from mechdac.core.schema import CompressionSpringSpec
from mechdac.core.units import QuantityValue
from mechdac.solvers.springs import solve_compression_spring


def q(value: float, unit: str) -> QuantityValue:
    return QuantityValue(value=value, unit=unit)


def spring_spec(**overrides: object) -> CompressionSpringSpec:
    values: dict[str, object] = {
        "load": q(1250, "N"),
        "wire_diameter": q(7, "mm"),
        "mean_coil_diameter": q(42, "mm"),
        "active_coils": 8,
        "shear_modulus": q(81370, "MPa"),
        "allowable_shear_stress": q(545, "MPa"),
    }
    values.update(overrides)
    return CompressionSpringSpec.model_validate(values)


def test_static_spring_outputs_follow_round_wire_equations() -> None:
    spec = spring_spec()

    result = solve_compression_spring(spec)

    wire = spec.wire_diameter.to("m")
    mean = spec.mean_coil_diameter.to("m")
    load = spec.load.to("N")
    coils = spec.active_coils
    modulus = spec.shear_modulus.to("Pa")
    allowable = spec.allowable_shear_stress.to("Pa")
    index = mean / wire
    wahl = (4 * index - 1) / (4 * index - 4) + 0.615 / index
    expected_stress = wahl * 8 * load * mean / (math.pi * wire**3)
    expected_deflection = 8 * load * mean**3 * coils / (modulus * wire**4)
    expected_rate = modulus * wire**4 / (8 * mean**3 * coils)

    assert result.spring_index == pytest.approx(index)
    assert result.wahl_factor == pytest.approx(wahl)
    assert result.maximum_shear_stress.to("Pa") == pytest.approx(expected_stress)
    assert result.allowable_shear_stress.to("Pa") == pytest.approx(allowable)
    assert result.deflection.to("m") == pytest.approx(expected_deflection)
    assert result.spring_rate.to("N/m") == pytest.approx(expected_rate)
    assert result.shear_stress_utilization == pytest.approx(expected_stress / allowable)
    assert [entry.name for entry in result.calculation_trace] == [
        "Spring index",
        "Wahl factor",
        "Maximum shear stress",
        "Load deflection",
        "Spring rate",
        "Shear-stress utilization",
    ]
    assert result.solver_name == "mechdac.compression_spring_static"
    assert result.solver_version == "0.1.0"


def test_static_spring_calculation_converts_mixed_units() -> None:
    metric = solve_compression_spring(spring_spec())
    mixed = solve_compression_spring(
        spring_spec(
            load=q(1.25, "kN"),
            wire_diameter=q(0.7, "cm"),
            mean_coil_diameter=q(4.2, "cm"),
            shear_modulus=q(81.37, "GPa"),
            allowable_shear_stress=q(0.545, "GPa"),
        )
    )

    assert mixed.spring_index == pytest.approx(metric.spring_index)
    assert mixed.wahl_factor == pytest.approx(metric.wahl_factor)
    assert mixed.maximum_shear_stress.to("Pa") == pytest.approx(
        metric.maximum_shear_stress.to("Pa")
    )
    assert mixed.deflection.to("m") == pytest.approx(metric.deflection.to("m"))
    assert mixed.spring_rate.to("N/m") == pytest.approx(metric.spring_rate.to("N/m"))
    assert mixed.shear_stress_utilization == pytest.approx(metric.shear_stress_utilization)


def test_spring_result_round_trips_with_trace_and_metadata() -> None:
    result = solve_compression_spring(spring_spec())

    restored = CompressionSpringResult.model_validate_json(result.model_dump_json())

    assert restored == result
    assert restored.calculation_trace
    assert restored.assumptions
    assert restored.warnings == ()


@pytest.mark.parametrize(
    "overrides",
    [
        {"load": q(0, "N")},
        {"wire_diameter": q(-7, "mm")},
        {"mean_coil_diameter": q(7, "mm")},
        {"active_coils": 0},
        {"shear_modulus": q(0, "MPa")},
        {"allowable_shear_stress": q(-545, "MPa")},
        {"wire_diameter": q(7, "N")},
    ],
)
def test_spring_spec_rejects_invalid_geometry_or_material_inputs(
    overrides: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        spring_spec(**overrides)


def test_over_allowable_static_stress_is_reported_as_a_warning() -> None:
    result = solve_compression_spring(
        spring_spec(allowable_shear_stress=q(400, "MPa"))
    )

    assert result.shear_stress_utilization > 1
    assert any("exceeds the supplied allowable" in warning for warning in result.warnings)


def test_solver_rejects_positive_inputs_that_underflow_a_derived_output() -> None:
    with pytest.raises(ValueError, match="spring calculation is outside the supported numeric range"):
        solve_compression_spring(spring_spec(load=q(1e-323, "N")))


def test_bhandari_example_10_1_reproduces_static_spring_results() -> None:
    """Validate Bhandari Ch. 10, Example 10.1, printed pp. 407–408.

    The source gives P=1250 N, requested deflection 30 mm, C=6, G=81,370
    N/mm², and allowable shear 545 N/mm². It rounds the calculated wire
    diameter 6.63 mm to 7 mm and active coils 7.91 to 8; the solver uses
    those selected dimensions and computes the resulting actual deflection.
    """
    spec = spring_spec()

    result = solve_compression_spring(spec)

    # Source Eqs. (10.7), (10.8), and (10.13), independently evaluated.
    assert result.spring_index == pytest.approx(6)
    assert result.wahl_factor == pytest.approx(1.2525)
    assert result.maximum_shear_stress.to("MPa") == pytest.approx(488.18, abs=0.01)
    assert result.allowable_shear_stress.to("MPa") == pytest.approx(545)
    assert result.deflection.to("mm") == pytest.approx(30.34, abs=0.01)
    assert result.spring_rate.to("N/mm") == pytest.approx(41.20, abs=0.01)
    assert result.shear_stress_utilization == pytest.approx(0.89575, abs=1e-5)
