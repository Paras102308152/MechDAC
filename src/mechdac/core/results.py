"""Structured outputs from engineering solvers."""

from typing import Literal

from pydantic import Field

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


class ShaftDesignResult(DomainModel):
    """Static solid-shaft yield sizing result under bending and torsion."""

    minimum_required_diameter: QuantityValue
    bending_stress: QuantityValue
    torsional_shear_stress: QuantityValue
    equivalent_stress: QuantityValue
    yield_strength: QuantityValue
    minimum_factor_of_safety: float
    factor_of_safety: float
    calculation_trace: tuple[CalculationTraceEntry, ...]
    warnings: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    solver_name: Literal["mechdac.static_solid_shaft_yield"] = "mechdac.static_solid_shaft_yield"
    solver_version: str = "0.1.0"


class BeamShaftDesignResult(DomainModel):
    """Beam solution and static shaft sizing at its maximum-moment section."""

    beam_analysis: BeamAnalysisResult
    shaft_design: ShaftDesignResult
    critical_section_position: QuantityValue
    critical_bending_moment: QuantityValue
    assumptions: tuple[str, ...] = ()
    solver_name: Literal["mechdac.beam_shaft_static"] = "mechdac.beam_shaft_static"
    solver_version: str = "0.1.0"


class SpurGearResult(DomainModel):
    """Pitch geometry, speed/torque, and mesh forces for an external spur pair."""

    gear_ratio: float = Field(gt=0, allow_inf_nan=False)
    pinion_pitch_diameter: QuantityValue
    gear_pitch_diameter: QuantityValue
    center_distance: QuantityValue
    output_speed: QuantityValue
    input_torque: QuantityValue
    output_torque: QuantityValue
    tangential_force: QuantityValue
    radial_force: QuantityValue
    calculation_trace: tuple[CalculationTraceEntry, ...] = ()
    assumptions: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    solver_name: Literal["mechdac.spur_gear_forces"] = "mechdac.spur_gear_forces"
    solver_version: str = "0.1.0"


class HelicalGearResult(DomainModel):
    """Pitch geometry, speed/torque, and mesh forces for an external helical pair."""

    gear_ratio: float = Field(gt=0, allow_inf_nan=False)
    pinion_pitch_diameter: QuantityValue
    gear_pitch_diameter: QuantityValue
    center_distance: QuantityValue
    output_speed: QuantityValue
    input_torque: QuantityValue
    output_torque: QuantityValue
    tangential_force: QuantityValue
    radial_force: QuantityValue
    axial_force: QuantityValue
    calculation_trace: tuple[CalculationTraceEntry, ...] = ()
    assumptions: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    solver_name: Literal["mechdac.helical_gear_forces"] = "mechdac.helical_gear_forces"
    solver_version: str = "0.1.0"


class CompressionSpringResult(DomainModel):
    """Static spring index, corrected stress, deflection, and rate result."""

    spring_index: float = Field(gt=1, allow_inf_nan=False)
    wahl_factor: float = Field(gt=0, allow_inf_nan=False)
    maximum_shear_stress: QuantityValue
    allowable_shear_stress: QuantityValue
    deflection: QuantityValue
    spring_rate: QuantityValue
    shear_stress_utilization: float = Field(gt=0, allow_inf_nan=False)
    calculation_trace: tuple[CalculationTraceEntry, ...] = ()
    assumptions: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    solver_name: Literal["mechdac.compression_spring_static"] = "mechdac.compression_spring_static"
    solver_version: str = "0.1.0"


class ShaftKeyResult(DomainModel):
    """Rectangular-key shear/bearing stresses and required-length checks."""

    key_shear_stress: QuantityValue
    key_bearing_stress: QuantityValue
    required_length_in_shear: QuantityValue
    required_length_in_bearing: QuantityValue
    required_key_length: QuantityValue
    shear_factor_of_safety: float = Field(gt=0, allow_inf_nan=False)
    bearing_factor_of_safety: float = Field(gt=0, allow_inf_nan=False)
    calculation_trace: tuple[CalculationTraceEntry, ...] = ()
    assumptions: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    solver_name: Literal["mechdac.key_strength_check"] = "mechdac.key_strength_check"
    solver_version: str = "0.1.0"
