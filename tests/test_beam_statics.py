import pytest
from pydantic import ValidationError

from mechdac.core.schema import (
    AppliedMoment,
    BeamSpec,
    DistributedLoad,
    PointLoad,
    QuantityValue,
    SupportSpec,
)
from mechdac.solvers.beam import solve_beam


def quantity(value: float, unit: str) -> QuantityValue:
    return QuantityValue(value=value, unit=unit)


def simply_supported(length: QuantityValue = quantity(10, "m")) -> list[SupportSpec]:
    return [
        SupportSpec(kind="pin", position=quantity(0, "m")),
        SupportSpec(kind="roller", position=length),
    ]


def test_central_point_load_reactions_shear_and_bending_moment() -> None:
    beam = BeamSpec(
        length=quantity(10, "m"),
        supports=simply_supported(),
        point_loads=[
            PointLoad(
                position=quantity(5, "m"),
                magnitude=quantity(1000, "N"),
                direction="down",
            )
        ],
    )

    result = solve_beam(beam)

    assert [reaction.force.value for reaction in result.support_reactions] == pytest.approx([500, 500])
    assert result.maximum_absolute_shear.value == pytest.approx(500)
    assert result.maximum_absolute_bending_moment.value == pytest.approx(2500)
    assert result.maximum_bending_moment_position.value == pytest.approx(5)
    assert result.shear_force_points[1].shear_left.value == pytest.approx(500)
    assert result.shear_force_points[1].shear_right.value == pytest.approx(-500)


def test_off_center_point_load_reactions_and_peak_moment() -> None:
    beam = BeamSpec(
        length=quantity(10, "m"),
        supports=simply_supported(),
        point_loads=[
            PointLoad(
                position=quantity(4, "m"),
                magnitude=quantity(1000, "N"),
                direction="down",
            )
        ],
    )

    result = solve_beam(beam)

    assert [reaction.force.value for reaction in result.support_reactions] == pytest.approx([600, 400])
    assert result.maximum_absolute_bending_moment.value == pytest.approx(2400)
    assert result.maximum_bending_moment_position.value == pytest.approx(4)


def test_uniformly_distributed_load_has_quadratic_moment_diagram() -> None:
    beam = BeamSpec(
        length=quantity(10, "m"),
        supports=simply_supported(),
        distributed_loads=[
            DistributedLoad(
                start=quantity(0, "m"),
                end=quantity(10, "m"),
                intensity=quantity(100, "N/m"),
                direction="down",
            )
        ],
    )

    result = solve_beam(beam)

    assert [reaction.force.value for reaction in result.support_reactions] == pytest.approx([500, 500])
    assert result.maximum_absolute_shear.value == pytest.approx(500)
    assert result.maximum_absolute_bending_moment.value == pytest.approx(1250)
    assert len(result.diagram_segments) == 1
    assert result.diagram_segments[0].shear_slope.value == pytest.approx(-100)


def test_applied_counterclockwise_moment_creates_moment_jump() -> None:
    beam = BeamSpec(
        length=quantity(10, "m"),
        supports=simply_supported(),
        applied_moments=[
            AppliedMoment(
                position=quantity(5, "m"),
                magnitude=quantity(1000, "N*m"),
                direction="counterclockwise",
            )
        ],
    )

    result = solve_beam(beam)
    center = result.bending_moment_points[1]

    assert [reaction.force.value for reaction in result.support_reactions] == pytest.approx([100, -100])
    assert center.moment_left.value == pytest.approx(500)
    assert center.moment_right.value == pytest.approx(-500)
    assert result.maximum_absolute_bending_moment.value == pytest.approx(500)


def test_beam_round_trips_through_json() -> None:
    beam = BeamSpec(
        length=quantity(10, "m"),
        supports=simply_supported(),
        point_loads=[
            PointLoad(
                position=quantity(5, "m"),
                magnitude=quantity(1, "kN"),
                direction="down",
            )
        ],
    )

    restored = BeamSpec.model_validate_json(beam.model_dump_json())

    assert restored == beam
    assert solve_beam(restored).support_reactions[0].force.value == pytest.approx(500)


def test_mixed_input_units_are_converted_to_result_units() -> None:
    beam = BeamSpec(
        length=quantity(10000, "mm"),
        supports=[
            SupportSpec(kind="pin", position=quantity(0, "m")),
            SupportSpec(kind="roller", position=quantity(10000, "mm")),
        ],
        point_loads=[
            PointLoad(
                position=quantity(5000, "mm"),
                magnitude=quantity(1, "kN"),
                direction="down",
            )
        ],
    )

    result = solve_beam(beam)

    assert result.support_reactions[0].force.value == pytest.approx(500)
    assert result.maximum_absolute_bending_moment.value == pytest.approx(2500)
    assert result.maximum_bending_moment_position.value == pytest.approx(5)


def test_invalid_support_configuration_is_rejected() -> None:
    with pytest.raises(ValidationError, match="exactly one pin and one roller"):
        BeamSpec(
            length=quantity(10, "m"),
            supports=[
                SupportSpec(kind="pin", position=quantity(0, "m")),
                SupportSpec(kind="pin", position=quantity(10, "m")),
            ],
        )


def test_load_outside_beam_is_rejected() -> None:
    with pytest.raises(ValidationError, match="within the beam"):
        BeamSpec(
            length=quantity(10, "m"),
            supports=simply_supported(),
            point_loads=[
                PointLoad(
                    position=quantity(11, "m"),
                    magnitude=quantity(100, "N"),
                    direction="down",
                )
            ],
        )


def test_unknown_fields_are_rejected() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        BeamSpec(
            length=quantity(10, "m"),
            supports=simply_supported(),
            safety_factor=2,
        )


def test_unknown_units_are_rejected_as_validation_errors() -> None:
    with pytest.raises(ValidationError, match="unknown unit"):
        QuantityValue(value=2, unit="not_a_unit")


def test_incompatible_physical_dimensions_are_rejected() -> None:
    with pytest.raises(ValidationError, match="support position must have units compatible with m"):
        SupportSpec(kind="pin", position=quantity(2, "s"))


def test_distributed_load_outside_beam_is_rejected() -> None:
    with pytest.raises(ValidationError, match="distributed loads must be within the beam"):
        BeamSpec(
            length=quantity(10, "m"),
            supports=simply_supported(),
            distributed_loads=[
                DistributedLoad(
                    start=quantity(0, "m"),
                    end=quantity(11, "m"),
                    intensity=quantity(100, "N/m"),
                    direction="down",
                )
            ],
        )
