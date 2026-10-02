"""Tests for rendering existing beam diagram results."""

import pytest

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


def beam_result(
    *,
    point_loads: tuple[PointLoad, ...] = (),
    distributed_loads: tuple[DistributedLoad, ...] = (),
    applied_moments: tuple[AppliedMoment, ...] = (),
):
    beam = BeamSpec(
        length=quantity(10, "m"),
        supports=(
            SupportSpec(kind="pin", position=quantity(0, "m")),
            SupportSpec(kind="roller", position=quantity(10, "m")),
        ),
        point_loads=point_loads,
        distributed_loads=distributed_loads,
        applied_moments=applied_moments,
    )
    return solve_beam(beam)


def plot(result):
    from mechdac.plotting.beam import plot_beam_diagrams

    return plot_beam_diagrams(result)


def test_plot_beam_diagrams_preserves_point_force_shear_jump() -> None:
    result = beam_result(
        point_loads=(
            PointLoad(
                position=quantity(5, "m"),
                magnitude=quantity(1000, "N"),
                direction="down",
            ),
        )
    )

    figure = plot(result)

    assert len(figure.axes) == 2
    shear_axis, moment_axis = figure.axes
    assert shear_axis.get_ylabel() == "Shear force V [N]"
    assert moment_axis.get_ylabel() == "Bending moment M [N·m]"
    assert moment_axis.get_xlabel() == "Position x [m]"
    jump_segments = [
        segment
        for collection in shear_axis.collections
        for segment in collection.get_segments()
        if len(segment) == 2
        and segment[0][0] == pytest.approx(5)
        and segment[1][0] == pytest.approx(5)
    ]
    assert len(jump_segments) == 1
    assert sorted(point[1] for point in jump_segments[0]) == pytest.approx([-500, 500])
    assert not moment_axis.collections


def test_plot_beam_diagrams_samples_quadratic_uniform_load_moment() -> None:
    result = beam_result(
        distributed_loads=(
            DistributedLoad(
                start=quantity(0, "m"),
                end=quantity(10, "m"),
                intensity=quantity(100, "N/m"),
                direction="down",
            ),
        )
    )

    figure = plot(result)

    moment_axis = figure.axes[1]
    plotted_peak = max(max(line.get_ydata()) for line in moment_axis.lines)
    assert plotted_peak == pytest.approx(1250)


def test_plot_beam_diagrams_preserves_applied_couple_moment_jump() -> None:
    result = beam_result(
        applied_moments=(
            AppliedMoment(
                position=quantity(5, "m"),
                magnitude=quantity(1000, "N*m"),
                direction="counterclockwise",
            ),
        )
    )

    figure = plot(result)

    moment_axis = figure.axes[1]
    jump_segments = [
        segment
        for collection in moment_axis.collections
        for segment in collection.get_segments()
        if len(segment) == 2
        and segment[0][0] == pytest.approx(5)
        and segment[1][0] == pytest.approx(5)
    ]
    assert len(jump_segments) == 1
    assert sorted(point[1] for point in jump_segments[0]) == pytest.approx([-500, 500])
