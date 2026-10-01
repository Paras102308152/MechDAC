"""Structured outputs from engineering solvers."""

from typing import Literal

from mechdac.core.units import DomainModel, QuantityValue
from mechdac.core.schema import SupportKind


class SupportReaction(DomainModel):
    """Signed vertical reaction at a support (upward is positive)."""

    kind: SupportKind
    position: QuantityValue
    force: QuantityValue


class ShearForcePoint(DomainModel):
    """Shear immediately to either side of a beam event position."""

    position: QuantityValue
    shear_left: QuantityValue
    shear_right: QuantityValue


class BendingMomentPoint(DomainModel):
    """Sagging-positive bending moment immediately either side of an event."""

    position: QuantityValue
    moment_left: QuantityValue
    moment_right: QuantityValue


class DiagramSegment(DomainModel):
    """Exact local polynomial coefficients between adjacent beam events.

    With ``x`` measured from ``start`` in metres, shear is
    ``shear_start + shear_slope*x`` and moment is
    ``moment_start + moment_slope*x + shear_slope*x**2/2``.
    """

    start: QuantityValue
    end: QuantityValue
    shear_start: QuantityValue
    shear_slope: QuantityValue
    moment_start: QuantityValue
    moment_slope: QuantityValue


class CalculationTraceEntry(DomainModel):
    """A readable equilibrium equation with its numeric substitution and result."""

    name: str
    equation: str
    substitution: str
    result: QuantityValue


class BeamAnalysisResult(DomainModel):
    """Reactions and piecewise SFD/BMD data from a beam statics solution."""

    support_reactions: tuple[SupportReaction, ...]
    shear_force_points: tuple[ShearForcePoint, ...]
    bending_moment_points: tuple[BendingMomentPoint, ...]
    diagram_segments: tuple[DiagramSegment, ...]
    calculation_trace: tuple[CalculationTraceEntry, ...] = ()
    maximum_absolute_shear: QuantityValue
    maximum_absolute_bending_moment: QuantityValue
    maximum_bending_moment_position: QuantityValue
    warnings: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    solver_name: Literal["mechdac.beam_statics"] = "mechdac.beam_statics"
    solver_version: str = "0.1.0"
