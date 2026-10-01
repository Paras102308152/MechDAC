"""Generic static solid-round shaft sizing for bending and torsion."""

from __future__ import annotations

from math import pi, sqrt

from mechdac.core.results import BeamShaftDesignResult, CalculationTraceEntry, ShaftDesignResult
from mechdac.core.schema import BeamShaftLoadingSpec, ShaftLoadingSpec
from mechdac.core.units import QuantityValue
from mechdac.solvers.beam import solve_beam

_ASSUMPTIONS = (
    "The shaft is solid, circular, prismatic, and evaluated at one critical section.",
    "Loading is static and consists only of bending moment and torque.",
    "Nominal elastic stress formulas are used; stress concentrations and fatigue are excluded.",
    "Yield is screened using the von Mises distortion-energy criterion; this is not an ASME rating.",
)
_BEAM_COMPOSITION_ASSUMPTIONS = (
    "The beam's single-plane maximum absolute bending moment is used as shaft-section bending load.",
    "The supplied torque is assumed to act at the beam-reported maximum-moment section.",
    "Only the selected section is sized; tied moment maxima and torque elsewhere are not evaluated.",
)


def _q(value: float, unit: str) -> QuantityValue:
    return QuantityValue(value=value, unit=unit)


def solve_shaft(spec: ShaftLoadingSpec) -> ShaftDesignResult:
    """Find the minimum solid-round diameter meeting a static yield requirement.

    For a solid circular section, nominal bending stress is ``32M/(πd³)`` and
    nominal torsional shear is ``16T/(πd³)``. The generic static von Mises
    criterion is ``sqrt(σ_b² + 3τ²) <= S_y / n``. No standard-specific rating,
    fatigue method, or stress-concentration factor is applied.
    """

    moment = abs(spec.bending_moment.to("N*m"))
    torque = abs(spec.torque.to("N*m"))
    yield_strength = spec.material.yield_strength.to("Pa")
    target_safety_factor = spec.design_requirement.minimum_factor_of_safety
    if moment == 0 and torque == 0:
        raise ValueError("shaft sizing requires a nonzero bending moment or torque")

    equivalent_stress_coefficient = sqrt(
        (32 * moment / pi) ** 2 + 3 * (16 * torque / pi) ** 2
    )
    diameter = (target_safety_factor * equivalent_stress_coefficient / yield_strength) ** (1 / 3)
    bending_stress = 32 * moment / (pi * diameter**3)
    torsional_shear = 16 * torque / (pi * diameter**3)
    equivalent_stress = sqrt(bending_stress**2 + 3 * torsional_shear**2)
    factor_of_safety = yield_strength / equivalent_stress

    trace = (
        CalculationTraceEntry(
            name="Minimum required diameter",
            equation=(
                "d_min = [n_min × sqrt((32|M|/π)² + 3(16|T|/π)²) / S_y]^(1/3)"
            ),
            substitution=(
                f"d_min = [{target_safety_factor:g} × "
                f"sqrt((32×{moment:g}/π)² + 3(16×{torque:g}/π)²) / "
                f"{yield_strength:g}]^(1/3) = {diameter:g} m"
            ),
            result=_q(diameter, "m"),
        ),
        CalculationTraceEntry(
            name="Nominal bending stress",
            equation="σ_b = 32|M|/(πd³)",
            substitution=f"σ_b = 32×{moment:g}/(π×{diameter:g}³) = {bending_stress:g} Pa",
            result=_q(bending_stress, "Pa"),
        ),
        CalculationTraceEntry(
            name="Nominal torsional shear stress",
            equation="τ = 16|T|/(πd³)",
            substitution=f"τ = 16×{torque:g}/(π×{diameter:g}³) = {torsional_shear:g} Pa",
            result=_q(torsional_shear, "Pa"),
        ),
        CalculationTraceEntry(
            name="Equivalent von Mises stress",
            equation="σ_vm = sqrt(σ_b² + 3τ²)",
            substitution=(
                f"σ_vm = sqrt({bending_stress:g}² + 3×{torsional_shear:g}²) "
                f"= {equivalent_stress:g} Pa"
            ),
            result=_q(equivalent_stress, "Pa"),
        ),
        CalculationTraceEntry(
            name="Yield factor of safety",
            equation="n_y = S_y / σ_vm",
            substitution=(
                f"n_y = {yield_strength:g} Pa / {equivalent_stress:g} Pa "
                f"= {factor_of_safety:g}"
            ),
            result=_q(factor_of_safety, "dimensionless"),
        ),
    )
    return ShaftDesignResult(
        minimum_required_diameter=_q(diameter, "m"),
        bending_stress=_q(bending_stress, "Pa"),
        torsional_shear_stress=_q(torsional_shear, "Pa"),
        equivalent_stress=_q(equivalent_stress, "Pa"),
        yield_strength=_q(yield_strength, "Pa"),
        minimum_factor_of_safety=target_safety_factor,
        factor_of_safety=factor_of_safety,
        calculation_trace=trace,
        assumptions=_ASSUMPTIONS,
    )


def solve_shaft_from_beam(spec: BeamShaftLoadingSpec) -> BeamShaftDesignResult:
    """Size one shaft section using a beam's maximum absolute bending moment.

    The input torque is taken at the position reported by the beam solver as
    having the maximum absolute bending moment. This composition does not
    model bending in multiple planes, distributed torque, or stress history.
    """

    beam_result = solve_beam(spec.beam)
    shaft_result = solve_shaft(
        ShaftLoadingSpec(
            bending_moment=beam_result.maximum_absolute_bending_moment,
            torque=spec.torque_at_critical_section,
            material=spec.material,
            design_requirement=spec.design_requirement,
        )
    )
    return BeamShaftDesignResult(
        beam_analysis=beam_result,
        shaft_design=shaft_result,
        critical_section_position=beam_result.maximum_bending_moment_position,
        critical_bending_moment=beam_result.maximum_absolute_bending_moment,
        assumptions=_BEAM_COMPOSITION_ASSUMPTIONS,
    )
