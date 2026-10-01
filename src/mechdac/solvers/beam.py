"""Deterministic 1D vertical beam statics and SFD/BMD solver."""

from __future__ import annotations

from collections import defaultdict

from mechdac.core.results import (
    BeamAnalysisResult,
    BendingMomentPoint,
    CalculationTraceEntry,
    DiagramSegment,
    ShearForcePoint,
    SupportReaction,
)
from mechdac.core.schema import BeamSpec
from mechdac.core.units import QuantityValue

_ASSUMPTIONS = (
    "Analysis is planar and includes vertical forces and bending couples only.",
    "Supports provide vertical reactions only; axial effects are outside this model.",
    "Beam self-weight is omitted unless supplied as a distributed load.",
)


def _q(value: float, unit: str) -> QuantityValue:
    return QuantityValue(value=value, unit=unit)


def _signed_direction(magnitude: float, direction: str, positive: str) -> float:
    return magnitude if direction == positive else -magnitude


def _solve_reactions(
    beam: BeamSpec,
) -> tuple[tuple[SupportReaction, ...], dict[float, float], tuple[CalculationTraceEntry, ...]]:
    supports = sorted(beam.supports, key=lambda support: support.position.to("m"))
    x_left, x_right = (support.position.to("m") for support in supports)
    force_terms: list[str] = []
    moment_terms: list[str] = []
    total_force = 0.0
    total_moment_about_left_support = 0.0

    for load in beam.point_loads:
        position = load.position.to("m")
        force = _signed_direction(load.magnitude.to("N"), load.direction, "up")
        force_terms.append(f"({force:+g} N)")
        moment_terms.append(f"({force:+g} N × ({position:g} m - {x_left:g} m))")
        total_force += force
        total_moment_about_left_support += force * (position - x_left)

    for load in beam.distributed_loads:
        start = load.start.to("m")
        end = load.end.to("m")
        intensity = _signed_direction(load.intensity.to("N/m"), load.direction, "up")
        width = end - start
        resultant = intensity * width
        centroid = start + width / 2
        force_terms.append(f"({intensity:+g} N/m × {width:g} m)")
        moment_terms.append(
            f"({intensity:+g} N/m × {width:g} m × ({centroid:g} m - {x_left:g} m))"
        )
        total_force += resultant
        total_moment_about_left_support += resultant * (centroid - x_left)

    for moment in beam.applied_moments:
        couple = _signed_direction(moment.magnitude.to("N*m"), moment.direction, "counterclockwise")
        moment_terms.append(f"({couple:+g} N·m)")
        total_moment_about_left_support += couple

    support_span = x_right - x_left
    right_reaction = -total_moment_about_left_support / support_span
    left_reaction = -total_force - right_reaction
    reaction_by_position = {x_left: left_reaction, x_right: right_reaction}
    reactions = tuple(
        SupportReaction(
            kind=support.kind,
            position=_q(support.position.to("m"), "m"),
            force=_q(reaction_by_position[support.position.to("m")], "N"),
        )
        for support in supports
    )
    force_substitution = " + ".join(force_terms) or "0 N"
    moment_substitution = " + ".join(moment_terms) or "0 N·m"
    right_support = supports[1]
    left_support = supports[0]
    trace = (
        CalculationTraceEntry(
            name="External vertical resultant",
            equation="F_ext = ΣF_point + Σ(q_i Δx_i)",
            substitution=f"F_ext = {force_substitution} = {total_force:+g} N",
            result=_q(total_force, "N"),
        ),
        CalculationTraceEntry(
            name="External moment about support A",
            equation="M_A = Σ[F_i(x_i - x_A)] + Σ[M_i]",
            substitution=(
                f"M_A = {moment_substitution} = "
                f"{total_moment_about_left_support:+g} N·m"
            ),
            result=_q(total_moment_about_left_support, "N*m"),
        ),
        CalculationTraceEntry(
            name=f"{right_support.kind} reaction",
            equation="R_B = -M_A / (x_B - x_A)",
            substitution=(
                f"R_B = -({total_moment_about_left_support:+g} N·m) / "
                f"({x_right:g} m - {x_left:g} m) = {right_reaction:+g} N"
            ),
            result=_q(right_reaction, "N"),
        ),
        CalculationTraceEntry(
            name=f"{left_support.kind} reaction",
            equation="R_A = -F_ext - R_B",
            substitution=(
                f"R_A = -({total_force:+g} N) - ({right_reaction:+g} N) "
                f"= {left_reaction:+g} N"
            ),
            result=_q(left_reaction, "N"),
        ),
    )
    return reactions, reaction_by_position, trace


def solve_beam(beam: BeamSpec) -> BeamAnalysisResult:
    """Solve reactions and piecewise shear/moment behavior for a validated beam.

    Positive vertical force is upward, positive applied couple is
    counterclockwise, and positive internal bending moment is sagging.
    Distributed-load intensity uses the same upward-positive sign convention.
    """

    reactions, reaction_by_position, calculation_trace = _solve_reactions(beam)
    length = beam.length.to("m")

    event_positions = {0.0, length, *reaction_by_position}
    event_shear_jumps: defaultdict[float, float] = defaultdict(float)
    event_moment_couples: defaultdict[float, float] = defaultdict(float)

    for position, reaction in reaction_by_position.items():
        event_shear_jumps[position] += reaction
    for load in beam.point_loads:
        position = load.position.to("m")
        event_positions.add(position)
        event_shear_jumps[position] += _signed_direction(
            load.magnitude.to("N"), load.direction, "up"
        )
    for moment in beam.applied_moments:
        position = moment.position.to("m")
        event_positions.add(position)
        event_moment_couples[position] += _signed_direction(
            moment.magnitude.to("N*m"), moment.direction, "counterclockwise"
        )
    for load in beam.distributed_loads:
        event_positions.update((load.start.to("m"), load.end.to("m")))

    positions = sorted(event_positions)
    shear_points: list[ShearForcePoint] = []
    moment_points: list[BendingMomentPoint] = []
    segments: list[DiagramSegment] = []
    shear_candidates: list[tuple[float, float]] = []
    moment_candidates: list[tuple[float, float]] = []
    shear = 0.0
    moment_value = 0.0

    for index, position in enumerate(positions):
        shear_left = shear
        moment_left = moment_value
        shear += event_shear_jumps[position]
        moment_value -= event_moment_couples[position]

        shear_points.append(
            ShearForcePoint(
                position=_q(position, "m"),
                shear_left=_q(shear_left, "N"),
                shear_right=_q(shear, "N"),
            )
        )
        moment_points.append(
            BendingMomentPoint(
                position=_q(position, "m"),
                moment_left=_q(moment_left, "N*m"),
                moment_right=_q(moment_value, "N*m"),
            )
        )
        shear_candidates.extend(((position, shear_left), (position, shear)))
        moment_candidates.extend(((position, moment_left), (position, moment_value)))

        if index == len(positions) - 1:
            continue

        next_position = positions[index + 1]
        interval = next_position - position
        intensity = sum(
            _signed_direction(load.intensity.to("N/m"), load.direction, "up")
            for load in beam.distributed_loads
            if load.start.to("m") <= position < load.end.to("m")
        )
        segments.append(
            DiagramSegment(
                start=_q(position, "m"),
                end=_q(next_position, "m"),
                shear_start=_q(shear, "N"),
                shear_slope=_q(intensity, "N/m"),
                moment_start=_q(moment_value, "N*m"),
                moment_slope=_q(shear, "N"),
            )
        )

        shear_end = shear + intensity * interval
        moment_end = moment_value + shear * interval + intensity * interval**2 / 2
        shear_candidates.append((next_position, shear_end))
        moment_candidates.append((next_position, moment_end))
        if intensity != 0:
            stationary_distance = -shear / intensity
            if 0 < stationary_distance < interval:
                stationary_moment = (
                    moment_value
                    + shear * stationary_distance
                    + intensity * stationary_distance**2 / 2
                )
                moment_candidates.append((position + stationary_distance, stationary_moment))
        shear = shear_end
        moment_value = moment_end

    maximum_shear = max(shear_candidates, key=lambda candidate: abs(candidate[1]))
    maximum_moment = max(moment_candidates, key=lambda candidate: abs(candidate[1]))
    return BeamAnalysisResult(
        support_reactions=reactions,
        shear_force_points=tuple(shear_points),
        bending_moment_points=tuple(moment_points),
        diagram_segments=tuple(segments),
        calculation_trace=calculation_trace,
        maximum_absolute_shear=_q(abs(maximum_shear[1]), "N"),
        maximum_absolute_bending_moment=_q(abs(maximum_moment[1]), "N*m"),
        maximum_bending_moment_position=_q(maximum_moment[0], "m"),
        assumptions=_ASSUMPTIONS,
    )
