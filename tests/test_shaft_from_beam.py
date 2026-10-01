import math

import pytest

from mechdac.core.schema import (
    BeamShaftLoadingSpec,
    DesignRequirementSpec,
    MaterialSpec,
    QuantityValue,
)
from mechdac.core.results import BeamShaftDesignResult
from mechdac.solvers.shafts import solve_shaft_from_beam


def test_shaft_sizing_uses_beam_maximum_moment_and_preserves_both_results() -> None:
    spec = BeamShaftLoadingSpec.model_validate(
        {
            "beam": {
                "length": {"value": 4, "unit": "m"},
                "supports": [
                    {"kind": "pin", "position": {"value": 0, "unit": "m"}},
                    {"kind": "roller", "position": {"value": 4, "unit": "m"}},
                ],
                "point_loads": [
                    {
                        "position": {"value": 2, "unit": "m"},
                        "magnitude": {"value": 2000, "unit": "N"},
                        "direction": "down",
                    }
                ],
            },
            "torque_at_critical_section": {"value": 100, "unit": "N*m"},
            "material": {
                "name": "generic steel",
                "yield_strength": {"value": 250, "unit": "MPa"},
            },
            "design_requirement": {"minimum_factor_of_safety": 2},
        }
    )

    result = solve_shaft_from_beam(spec)
    restored_result = BeamShaftDesignResult.model_validate_json(result.model_dump_json())

    expected_diameter = (
        2
        * math.sqrt((32 * 2000 / math.pi) ** 2 + 3 * (16 * 100 / math.pi) ** 2)
        / 250e6
    ) ** (1 / 3)
    assert result.beam_analysis.maximum_absolute_bending_moment.to("N*m") == pytest.approx(2000)
    assert result.critical_section_position.to("m") == pytest.approx(2)
    assert result.critical_bending_moment.to("N*m") == pytest.approx(2000)
    assert result.shaft_design.minimum_required_diameter.to("m") == pytest.approx(expected_diameter)
    assert result.shaft_design.factor_of_safety == pytest.approx(2)
    assert restored_result == result
    assert "supplied torque is assumed to act at the beam-reported maximum-moment section" in (
        " ".join(result.assumptions)
    )


def test_beam_shaft_input_rejects_torque_with_wrong_dimensions() -> None:
    with pytest.raises(ValueError, match="torque at critical section must have units compatible"):
        BeamShaftLoadingSpec(
            beam={
                "length": QuantityValue(value=4, unit="m"),
                "supports": (
                    {"kind": "pin", "position": QuantityValue(value=0, unit="m")},
                    {"kind": "roller", "position": QuantityValue(value=4, unit="m")},
                ),
            },
            torque_at_critical_section=QuantityValue(value=10, unit="N"),
            material=MaterialSpec(
                name="generic steel", yield_strength=QuantityValue(value=250, unit="MPa")
            ),
            design_requirement=DesignRequirementSpec(minimum_factor_of_safety=2),
        )
