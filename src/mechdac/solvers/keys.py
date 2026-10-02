"""Generic static shear and bearing strength checks for rectangular sunk keys."""

from __future__ import annotations

from math import isfinite

from mechdac.core.results import CalculationTraceEntry, ShaftKeyResult
from mechdac.core.schema import ShaftKeySpec
from mechdac.core.units import QuantityValue

_ASSUMPTIONS = (
    "One rectangular sunk key transmits the full applied torque at a single shaft section.",
    "The torque is represented by a tangential force P = 2T/d at the shaft surface.",
    "Nominal shear is uniform over the key area b·l; bearing acts over the projected area h·l/2.",
    "Maximum-shear theory sets key shear yield strength to S_y/2; bearing yield uses S_y.",
    "The supplied tensile yield strength is assumed equal to the key material's compressive yield strength.",
    "Key dimensions are user-supplied; no standard-size lookup or compliance rating is performed.",
    "Stress concentrations, keyway and hub strength, fatigue, and coupling behavior are excluded.",
)


def _q(value: float, unit: str) -> QuantityValue:
    return QuantityValue(value=value, unit=unit)


def _finite(value: float, quantity_name: str) -> float:
    if not isfinite(value):
        raise ValueError(f"{quantity_name} is outside the supported numeric range")
    return value


def _positive(value: float, quantity_name: str) -> float:
    value = _finite(value, quantity_name)
    if value <= 0:
        raise ValueError(f"{quantity_name} is outside the supported numeric range")
    return value


def check_shaft_key(spec: ShaftKeySpec) -> ShaftKeyResult:
    """Check a rectangular sunk key for nominal shear and bearing yield.

    Shear yield uses the frozen maximum-shear basis ``S_y/2``; bearing yield
    uses ``S_y``. The requested minimum factor of safety is applied to both
    allowable stresses when computing the required lengths.
    """

    torque = _positive(spec.torque.to("N*m"), "torque")
    diameter = _positive(spec.shaft_diameter.to("m"), "shaft diameter")
    width = _positive(spec.key_width.to("m"), "key width")
    height = _positive(spec.key_height.to("m"), "key height")
    length = _positive(spec.key_length.to("m"), "key length")
    yield_strength = _positive(spec.material.yield_strength.to("Pa"), "yield strength")
    minimum_factor_of_safety = _positive(
        spec.design_requirement.minimum_factor_of_safety,
        "minimum factor of safety",
    )

    tangential_force = _positive(2 * torque / diameter, "tangential force")
    shear_area = _positive(width * length, "key shear area")
    bearing_height = _positive(height / 2, "projected bearing height")
    bearing_area = _positive(bearing_height * length, "key projected bearing area")
    shear_stress = _positive(tangential_force / shear_area, "key shear stress")
    bearing_stress = _positive(tangential_force / bearing_area, "key bearing stress")

    shear_yield_strength = yield_strength / 2
    allowable_shear_stress = _positive(
        shear_yield_strength / minimum_factor_of_safety,
        "allowable key shear stress",
    )
    allowable_bearing_stress = _positive(
        yield_strength / minimum_factor_of_safety,
        "allowable key bearing stress",
    )

    required_shear_length = _positive(
        tangential_force / (width * allowable_shear_stress),
        "required key length in shear",
    )
    required_bearing_length = _positive(
        tangential_force / (bearing_height * allowable_bearing_stress),
        "required key length in bearing",
    )
    required_key_length = max(required_shear_length, required_bearing_length)
    if required_shear_length > required_bearing_length:
        governing_mode = "shear controls"
    elif required_bearing_length > required_shear_length:
        governing_mode = "bearing controls"
    else:
        governing_mode = "both modes govern equally"

    shear_factor_of_safety = _positive(shear_yield_strength / shear_stress, "shear factor of safety")
    bearing_factor_of_safety = _positive(yield_strength / bearing_stress, "bearing factor of safety")

    warnings: tuple[str, ...] = ()
    if length < required_key_length:
        warnings = (
            "The provided key length is shorter than the required length for the requested factor of safety.",
        )

    trace = (
        CalculationTraceEntry(
            name="Tangential force from transmitted torque",
            equation="P = 2T/d",
            substitution=f"P = 2×{torque:g} N·m / {diameter:g} m = {tangential_force:g} N",
            result=_q(tangential_force, "N"),
        ),
        CalculationTraceEntry(
            name="Key shear stress",
            equation="τ_k = P/(b·l) = 2T/(d·b·l)",
            substitution=(
                f"τ_k = {tangential_force:g} N / ({width:g} m×{length:g} m) "
                f"= {shear_stress:g} Pa"
            ),
            result=_q(shear_stress, "Pa"),
        ),
        CalculationTraceEntry(
            name="Key bearing stress",
            equation="σ_c = P/(h·l/2) = 4T/(d·h·l)",
            substitution=(
                f"σ_c = {tangential_force:g} N / ({height:g} m×{length:g} m/2) "
                f"= {bearing_stress:g} Pa"
            ),
            result=_q(bearing_stress, "Pa"),
        ),
        CalculationTraceEntry(
            name="Allowable key shear stress",
            equation="τ_allow = (S_y/2)/n_min",
            substitution=(
                f"τ_allow = ({yield_strength:g} Pa/2)/{minimum_factor_of_safety:g} "
                f"= {allowable_shear_stress:g} Pa"
            ),
            result=_q(allowable_shear_stress, "Pa"),
        ),
        CalculationTraceEntry(
            name="Allowable key bearing stress",
            equation="σ_c,allow = S_y/n_min",
            substitution=(
                f"σ_c,allow = {yield_strength:g} Pa/{minimum_factor_of_safety:g} "
                f"= {allowable_bearing_stress:g} Pa"
            ),
            result=_q(allowable_bearing_stress, "Pa"),
        ),
        CalculationTraceEntry(
            name="Required key length in shear",
            equation="l_s = P/(b·τ_allow) = 2T/[d·b·(S_y/(2n_min))]",
            substitution=(
                f"l_s = {tangential_force:g} N / ({width:g} m×{allowable_shear_stress:g} Pa) "
                f"= {required_shear_length:g} m"
            ),
            result=_q(required_shear_length, "m"),
        ),
        CalculationTraceEntry(
            name="Required key length in bearing",
            equation="l_b = P/[(h/2)·σ_c,allow] = 4T/[d·h·(S_y/n_min)]",
            substitution=(
                f"l_b = {tangential_force:g} N / ({height:g} m/2×{allowable_bearing_stress:g} Pa) "
                f"= {required_bearing_length:g} m"
            ),
            result=_q(required_bearing_length, "m"),
        ),
        CalculationTraceEntry(
            name=f"Governing required key length — {governing_mode}",
            equation="l_req = max(l_s, l_b)",
            substitution=(
                f"l_req = max({required_shear_length:g} m, {required_bearing_length:g} m) "
                f"= {required_key_length:g} m; {governing_mode}"
            ),
            result=_q(required_key_length, "m"),
        ),
        CalculationTraceEntry(
            name="Shear factor of safety for provided key length",
            equation="n_shear = (S_y/2)/τ_k",
            substitution=(
                f"n_shear = ({yield_strength:g} Pa/2)/{shear_stress:g} Pa "
                f"= {shear_factor_of_safety:g}"
            ),
            result=_q(shear_factor_of_safety, "dimensionless"),
        ),
        CalculationTraceEntry(
            name="Bearing factor of safety for provided key length",
            equation="n_bearing = S_y/σ_c",
            substitution=(
                f"n_bearing = {yield_strength:g} Pa/{bearing_stress:g} Pa "
                f"= {bearing_factor_of_safety:g}"
            ),
            result=_q(bearing_factor_of_safety, "dimensionless"),
        ),
    )

    return ShaftKeyResult(
        key_shear_stress=_q(shear_stress, "Pa"),
        key_bearing_stress=_q(bearing_stress, "Pa"),
        required_length_in_shear=_q(required_shear_length, "m"),
        required_length_in_bearing=_q(required_bearing_length, "m"),
        required_key_length=_q(required_key_length, "m"),
        shear_factor_of_safety=shear_factor_of_safety,
        bearing_factor_of_safety=bearing_factor_of_safety,
        calculation_trace=trace,
        assumptions=_ASSUMPTIONS,
        warnings=warnings,
    )
