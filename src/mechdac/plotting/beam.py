"""Plot adapters for beam statics results."""

from __future__ import annotations

from matplotlib.figure import Figure

from mechdac.core.results import BeamAnalysisResult

_SAMPLES_PER_SEGMENT = 51


def _sample_positions(start: float, end: float) -> list[float]:
    """Return evenly spaced render coordinates, including both endpoints."""

    return [
        start + (end - start) * index / (_SAMPLES_PER_SEGMENT - 1)
        for index in range(_SAMPLES_PER_SEGMENT)
    ]


def plot_beam_diagrams(result: BeamAnalysisResult) -> Figure:
    """Create shear-force and bending-moment plots from a solved beam result.

    The returned figure is not displayed or saved. Diagram values are sampled
    from the exact local segment polynomials in ``result``; event-side values
    preserve jumps from concentrated forces and couples.
    """

    figure = Figure(figsize=(8, 6), constrained_layout=True)
    shear_axis = figure.add_subplot(2, 1, 1)
    moment_axis = figure.add_subplot(2, 1, 2, sharex=shear_axis)

    for segment in result.diagram_segments:
        start = segment.start.to("m")
        end = segment.end.to("m")
        shear_start = segment.shear_start.to("N")
        shear_slope = segment.shear_slope.to("N/m")
        moment_start = segment.moment_start.to("N*m")
        moment_slope = segment.moment_slope.to("N")
        positions = _sample_positions(start, end)
        local_positions = [position - start for position in positions]
        shear_values = [shear_start + shear_slope * local for local in local_positions]
        moment_values = [
            moment_start + moment_slope * local + shear_slope * local**2 / 2
            for local in local_positions
        ]
        shear_axis.plot(positions, shear_values, color="tab:blue")
        moment_axis.plot(positions, moment_values, color="tab:orange")

    for point in result.shear_force_points:
        left = point.shear_left.to("N")
        right = point.shear_right.to("N")
        if left != right:
            position = point.position.to("m")
            shear_axis.vlines(position, min(left, right), max(left, right), color="tab:blue")

    for point in result.bending_moment_points:
        left = point.moment_left.to("N*m")
        right = point.moment_right.to("N*m")
        if left != right:
            position = point.position.to("m")
            moment_axis.vlines(
                position,
                min(left, right),
                max(left, right),
                color="tab:orange",
            )

    for axis in (shear_axis, moment_axis):
        axis.axhline(0, color="black", linewidth=0.8)
        axis.grid(True, alpha=0.3)
    shear_axis.set_title("Shear-force diagram (upward shear positive)")
    shear_axis.set_ylabel("Shear force V [N]")
    moment_axis.set_title("Bending-moment diagram (sagging positive)")
    moment_axis.set_ylabel("Bending moment M [N·m]")
    moment_axis.set_xlabel("Position x [m]")
    if result.bending_moment_points:
        moment_axis.set_xlim(
            result.bending_moment_points[0].position.to("m"),
            result.bending_moment_points[-1].position.to("m"),
        )
    return figure
