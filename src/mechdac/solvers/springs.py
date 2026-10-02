"""Static round-wire helical compression spring calculations."""

from __future__ import annotations

from math import isfinite, pi

from mechdac.core.results import CalculationTraceEntry, CompressionSpringResult
from mechdac.core.schema import CompressionSpringSpec
from mechdac.core.units import QuantityValue

_ASSUMPTIONS = (
    "The spring is a round-wire helical compression spring under a static axial load.",
    "The supplied active-coil count is the effective count used in the deflection and rate equations.",
    "The Wahl factor accounts for wire curvature and direct shear in the maximum shear-stress estimate.",
    "Deflection is calculated for a linear-elastic spring with constant mean coil diameter and wire diameter.",
    "End geometry, inactive coils, fatigue, buckling, coil bind, surge, manufacturing tolerances, and material selection are excluded.",
    "Results are a generic static numerical check, not a standards-compliance rating.",
)


def _q(value: float, unit: str) -> QuantityValue:
    return QuantityValue(value=value, unit=unit)


def _finite(value: float, quantity_name: str) -> float:
    if not isfinite(value):
        raise ValueError(f"{quantity_name} is outside the supported numeric range")
    return value


def solve_compression_spring(spec: CompressionSpringSpec) -> CompressionSpringResult:
    """Calculate static stress, deflection, rate, and utilization for one spring.

    Input quantities are converted to SI units. The maximum shear stress uses
    the Wahl correction ``K_w = (4C - 1)/(4C - 4) + 0.615/C``; deflection
    uses ``δ = 8 P D³ N_a/(G d⁴)``. No spring sizing or end geometry is inferred.
    """

    load = _finite(spec.load.to("N"), "spring load")
    wire = _finite(spec.wire_diameter.to("m"), "wire diameter")
    mean = _finite(spec.mean_coil_diameter.to("m"), "mean coil diameter")
    modulus = _finite(spec.shear_modulus.to("Pa"), "shear modulus")
    allowable = _finite(
        spec.allowable_shear_stress.to("Pa"), "allowable shear stress"
    )
    active_coils = spec.active_coils
    if min(load, wire, mean, modulus, allowable) <= 0:
        raise ValueError("spring inputs are outside the supported numeric range")
    if mean <= wire:
        raise ValueError("mean coil diameter must exceed wire diameter")

    try:
        spring_index = _finite(mean / wire, "spring index")
        if spring_index <= 1:
            raise ValueError("mean coil diameter must exceed wire diameter")
        wahl_factor = _finite(
            (4 * spring_index - 1) / (4 * spring_index - 4) + 0.615 / spring_index,
            "Wahl factor",
        )
        maximum_stress = _finite(
            wahl_factor * 8 * load * mean / (pi * wire**3),
            "maximum shear stress",
        )
        deflection = _finite(
            8 * load * mean**3 * active_coils / (modulus * wire**4),
            "spring deflection",
        )
        spring_rate = _finite(
            modulus * wire**4 / (8 * mean**3 * active_coils), "spring rate"
        )
        utilization = _finite(maximum_stress / allowable, "shear-stress utilization")
    except (OverflowError, ZeroDivisionError) as exc:
        raise ValueError("spring calculation is outside the supported numeric range") from exc
    if min(wahl_factor, maximum_stress, deflection, spring_rate, utilization) <= 0:
        raise ValueError("spring calculation is outside the supported numeric range")

    trace = (
        CalculationTraceEntry(
            name="Spring index",
            equation="C = D/d",
            substitution=(
                f"C = {mean:g} m / {wire:g} m = {spring_index:g}"
            ),
            result=_q(spring_index, "dimensionless"),
        ),
        CalculationTraceEntry(
            name="Wahl factor",
            equation="K_w = (4C - 1)/(4C - 4) + 0.615/C",
            substitution=(
                f"K_w = (4×{spring_index:g} - 1)/(4×{spring_index:g} - 4) "
                f"+ 0.615/{spring_index:g} = {wahl_factor:g}"
            ),
            result=_q(wahl_factor, "dimensionless"),
        ),
        CalculationTraceEntry(
            name="Maximum shear stress",
            equation="τ_max = K_w × 8PD/(πd³)",
            substitution=(
                f"τ_max = {wahl_factor:g} × 8×{load:g} N×{mean:g} m "
                f"/(π×{wire:g}³ m³) = {maximum_stress:g} Pa"
            ),
            result=_q(maximum_stress, "Pa"),
        ),
        CalculationTraceEntry(
            name="Load deflection",
            equation="δ = 8PD³N_a/(Gd⁴)",
            substitution=(
                f"δ = 8×{load:g} N×{mean:g}³ m³×{active_coils} "
                f"/({modulus:g} Pa×{wire:g}⁴ m⁴) = {deflection:g} m"
            ),
            result=_q(deflection, "m"),
        ),
        CalculationTraceEntry(
            name="Spring rate",
            equation="k = Gd⁴/(8D³N_a) = P/δ",
            substitution=(
                f"k = {modulus:g} Pa×{wire:g}⁴ m⁴ "
                f"/(8×{mean:g}³ m³×{active_coils}) = {spring_rate:g} N/m"
            ),
            result=_q(spring_rate, "N/m"),
        ),
        CalculationTraceEntry(
            name="Shear-stress utilization",
            equation="U_τ = τ_max/τ_allowable",
            substitution=(
                f"U_τ = {maximum_stress:g} Pa / {allowable:g} Pa "
                f"= {utilization:g}"
            ),
            result=_q(utilization, "dimensionless"),
        ),
    )
    warnings = (
        ("Calculated maximum shear stress exceeds the supplied allowable shear stress.",)
        if utilization > 1
        else ()
    )
    return CompressionSpringResult(
        spring_index=spring_index,
        wahl_factor=wahl_factor,
        maximum_shear_stress=_q(maximum_stress, "Pa"),
        allowable_shear_stress=_q(allowable, "Pa"),
        deflection=_q(deflection, "m"),
        spring_rate=_q(spring_rate, "N/m"),
        shear_stress_utilization=utilization,
        calculation_trace=trace,
        assumptions=_ASSUMPTIONS,
        warnings=warnings,
    )
