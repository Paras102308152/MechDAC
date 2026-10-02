"""Ideal pitch geometry and mesh-force magnitudes for external gear pairs."""

from __future__ import annotations

from math import atan, cos, isfinite, pi, radians, tan

from mechdac.core.results import (
    CalculationTraceEntry,
    HelicalGearResult,
    SpurGearResult,
)
from mechdac.core.schema import HelicalGearPairSpec, SpurGearPairSpec
from mechdac.core.units import QuantityValue

_SPUR_ASSUMPTIONS = (
    "An external, parallel-axis involute spur gear pair is assumed to have conjugate pitch contact.",
    "Input power and pinion speed define steady-state operation; losses and transients are neglected.",
    "The tooth-count ratio sets the magnitude of output speed and torque, with ideal power conserved.",
    "Tooth forces are pitch-circle magnitudes; directions and vector resolution are not reported.",
    "Tooth strength, fatigue, wear, interference, undercut, face-width load sharing, and standards ratings are not evaluated.",
)
_HELICAL_ASSUMPTIONS = (
    "An external, parallel-axis involute helical gear pair is assumed to have conjugate pitch contact.",
    "Normal-system module and pressure angle are converted to the transverse plane using the helix angle.",
    "The helix angle is used as a positive magnitude; helix hand and force directions are not resolved.",
    "Input power and pinion speed define steady-state operation; losses and transients are neglected.",
    "The tooth-count ratio sets the magnitude of output speed and torque, with ideal power conserved.",
    "Tooth forces are pitch-circle magnitudes; directions and vector resolution are not reported.",
    "Tooth strength, fatigue, wear, interference, undercut, face-width load sharing, and standards ratings are not evaluated.",
)


def _q(value: float, unit: str) -> QuantityValue:
    return QuantityValue(value=value, unit=unit)


def _finite(value: float, quantity_name: str) -> float:
    if not isfinite(value):
        raise ValueError(f"{quantity_name} is outside the supported numeric range")
    return value


def _trace(
    name: str,
    equation: str,
    substitution: str,
    value: float,
    unit: str,
) -> CalculationTraceEntry:
    return CalculationTraceEntry(
        name=name,
        equation=equation,
        substitution=substitution,
        result=_q(value, unit),
    )


def _ratio_trace(pinion_teeth: int, gear_teeth: int, ratio: float) -> CalculationTraceEntry:
    return _trace(
        "Gear ratio",
        "i = z_g/z_p",
        f"i = {gear_teeth}/{pinion_teeth} = {ratio:g}",
        ratio,
        "dimensionless",
    )


def _transfer_values(
    input_power: float,
    pinion_speed_rpm: float,
    ratio: float,
    pinion_diameter: float,
) -> tuple[float, float, float, float]:
    """Return output speed, input/output torque, and pitch tangential force."""

    try:
        input_angular_speed = _finite(
            pinion_speed_rpm * (2 * pi / 60), "pinion angular speed"
        )
        if input_angular_speed <= 0 or ratio <= 0 or pinion_diameter <= 0:
            raise ValueError("gear calculation is outside the supported numeric range")
        input_torque = _finite(input_power / input_angular_speed, "input torque")
        output_speed = _finite(pinion_speed_rpm / ratio, "output speed")
        output_torque = _finite(input_torque * ratio, "output torque")
        tangential_force = _finite(2 * input_torque / pinion_diameter, "tangential force")
    except (OverflowError, ZeroDivisionError) as exc:
        raise ValueError("gear calculation is outside the supported numeric range") from exc
    if min(input_angular_speed, input_torque, output_speed, output_torque, tangential_force) <= 0:
        raise ValueError("gear calculation is outside the supported numeric range")
    return output_speed, input_torque, output_torque, tangential_force


def solve_spur_gear(spec: SpurGearPairSpec) -> SpurGearResult:
    """Solve pitch geometry, ideal transfer, and force magnitudes for a spur pair."""

    module = _finite(spec.module.to("m"), "module")
    pressure_angle = radians(_finite(spec.pressure_angle.to("degree"), "pressure angle"))
    input_power = _finite(spec.input_power.to("W"), "input power")
    pinion_speed = _finite(spec.pinion_speed.to("rpm"), "pinion speed")
    pinion_teeth = spec.pinion_teeth
    gear_teeth = spec.gear_teeth

    try:
        ratio = _finite(gear_teeth / pinion_teeth, "gear ratio")
        pinion_diameter = _finite(module * pinion_teeth, "pinion pitch diameter")
        gear_diameter = _finite(module * gear_teeth, "gear pitch diameter")
    except OverflowError as exc:
        raise ValueError("gear geometry is outside the supported numeric range") from exc
    center_distance = _finite((pinion_diameter + gear_diameter) / 2, "center distance")
    if min(module, pinion_diameter, gear_diameter, center_distance) <= 0:
        raise ValueError("gear geometry is outside the supported numeric range")

    output_speed, input_torque, output_torque, tangential_force = _transfer_values(
        input_power, pinion_speed, ratio, pinion_diameter
    )
    radial_force = _finite(tangential_force * tan(pressure_angle), "radial force")

    trace = (
        _ratio_trace(pinion_teeth, gear_teeth, ratio),
        _trace(
            "Pinion pitch diameter",
            "d_p = m z_p",
            f"d_p = {module:g} m × {pinion_teeth} = {pinion_diameter:g} m",
            pinion_diameter,
            "m",
        ),
        _trace(
            "Gear pitch diameter",
            "d_g = m z_g",
            f"d_g = {module:g} m × {gear_teeth} = {gear_diameter:g} m",
            gear_diameter,
            "m",
        ),
        _trace(
            "Center distance",
            "a = (d_p + d_g)/2",
            f"a = ({pinion_diameter:g} m + {gear_diameter:g} m)/2 = {center_distance:g} m",
            center_distance,
            "m",
        ),
        _trace(
            "Output speed",
            "n_g = n_p/i",
            f"n_g = {pinion_speed:g} rpm/{ratio:g} = {output_speed:g} rpm",
            output_speed,
            "rpm",
        ),
        _trace(
            "Input torque",
            "T_p = P/[2π(n_p/60)]",
            f"T_p = {input_power:g} W/[2π({pinion_speed:g} rpm/60)] = {input_torque:g} N·m",
            input_torque,
            "N*m",
        ),
        _trace(
            "Ideal output torque",
            "T_g = i T_p",
            f"T_g = {ratio:g} × {input_torque:g} N·m = {output_torque:g} N·m",
            output_torque,
            "N*m",
        ),
        _trace(
            "Tangential force magnitude",
            "F_t = 2T_p/d_p",
            f"F_t = 2 × {input_torque:g} N·m/{pinion_diameter:g} m = {tangential_force:g} N",
            tangential_force,
            "N",
        ),
        _trace(
            "Radial force magnitude",
            "F_r = F_t tan(α)",
            f"F_r = {tangential_force:g} N × tan({spec.pressure_angle.to('degree'):g}°) = {radial_force:g} N",
            radial_force,
            "N",
        ),
    )
    return SpurGearResult(
        gear_ratio=ratio,
        pinion_pitch_diameter=_q(pinion_diameter, "m"),
        gear_pitch_diameter=_q(gear_diameter, "m"),
        center_distance=_q(center_distance, "m"),
        output_speed=_q(output_speed, "rpm"),
        input_torque=_q(input_torque, "N*m"),
        output_torque=_q(output_torque, "N*m"),
        tangential_force=_q(tangential_force, "N"),
        radial_force=_q(radial_force, "N"),
        calculation_trace=trace,
        assumptions=_SPUR_ASSUMPTIONS,
    )


def solve_helical_gear(spec: HelicalGearPairSpec) -> HelicalGearResult:
    """Solve pitch geometry, ideal transfer, and force magnitudes for a helical pair."""

    normal_module = _finite(spec.normal_module.to("m"), "normal module")
    normal_pressure_angle_deg = _finite(
        spec.normal_pressure_angle.to("degree"), "normal pressure angle"
    )
    helix_angle_deg = _finite(spec.helix_angle.to("degree"), "helix angle")
    normal_pressure_angle = radians(normal_pressure_angle_deg)
    helix_angle = radians(helix_angle_deg)
    input_power = _finite(spec.input_power.to("W"), "input power")
    pinion_speed = _finite(spec.pinion_speed.to("rpm"), "pinion speed")
    pinion_teeth = spec.pinion_teeth
    gear_teeth = spec.gear_teeth

    try:
        ratio = _finite(gear_teeth / pinion_teeth, "gear ratio")
        cosine_helix = _finite(cos(helix_angle), "helix angle cosine")
        pinion_diameter = _finite(
            normal_module * pinion_teeth / cosine_helix, "pinion pitch diameter"
        )
        gear_diameter = _finite(
            normal_module * gear_teeth / cosine_helix, "gear pitch diameter"
        )
    except OverflowError as exc:
        raise ValueError("gear geometry is outside the supported numeric range") from exc
    center_distance = _finite((pinion_diameter + gear_diameter) / 2, "center distance")
    transverse_pressure_angle = atan(tan(normal_pressure_angle) / cosine_helix)
    if min(normal_module, pinion_diameter, gear_diameter, center_distance) <= 0:
        raise ValueError("gear geometry is outside the supported numeric range")

    output_speed, input_torque, output_torque, tangential_force = _transfer_values(
        input_power, pinion_speed, ratio, pinion_diameter
    )
    radial_force = _finite(
        tangential_force * tan(normal_pressure_angle) / cosine_helix,
        "radial force",
    )
    axial_force = _finite(tangential_force * tan(helix_angle), "axial force")
    transverse_pressure_angle_deg = _finite(
        transverse_pressure_angle * 180 / pi, "transverse pressure angle"
    )

    trace = (
        _ratio_trace(pinion_teeth, gear_teeth, ratio),
        _trace(
            "Transverse pressure angle",
            "α_t = atan[tan(α_n)/cos(β)]",
            f"α_t = atan[tan({normal_pressure_angle_deg:g}°)/cos({helix_angle_deg:g}°)] = {transverse_pressure_angle_deg:g}°",
            transverse_pressure_angle_deg,
            "degree",
        ),
        _trace(
            "Pinion pitch diameter",
            "d_p = m_n z_p/cos(β)",
            f"d_p = {normal_module:g} m × {pinion_teeth}/cos({helix_angle_deg:g}°) = {pinion_diameter:g} m",
            pinion_diameter,
            "m",
        ),
        _trace(
            "Gear pitch diameter",
            "d_g = m_n z_g/cos(β)",
            f"d_g = {normal_module:g} m × {gear_teeth}/cos({helix_angle_deg:g}°) = {gear_diameter:g} m",
            gear_diameter,
            "m",
        ),
        _trace(
            "Center distance",
            "a = (d_p + d_g)/2",
            f"a = ({pinion_diameter:g} m + {gear_diameter:g} m)/2 = {center_distance:g} m",
            center_distance,
            "m",
        ),
        _trace(
            "Output speed",
            "n_g = n_p/i",
            f"n_g = {pinion_speed:g} rpm/{ratio:g} = {output_speed:g} rpm",
            output_speed,
            "rpm",
        ),
        _trace(
            "Input torque",
            "T_p = P/[2π(n_p/60)]",
            f"T_p = {input_power:g} W/[2π({pinion_speed:g} rpm/60)] = {input_torque:g} N·m",
            input_torque,
            "N*m",
        ),
        _trace(
            "Ideal output torque",
            "T_g = i T_p",
            f"T_g = {ratio:g} × {input_torque:g} N·m = {output_torque:g} N·m",
            output_torque,
            "N*m",
        ),
        _trace(
            "Tangential force magnitude",
            "F_t = 2T_p/d_p",
            f"F_t = 2 × {input_torque:g} N·m/{pinion_diameter:g} m = {tangential_force:g} N",
            tangential_force,
            "N",
        ),
        _trace(
            "Radial force magnitude",
            "F_r = F_t tan(α_n)/cos(β) = F_t tan(α_t)",
            f"F_r = {tangential_force:g} N × tan({normal_pressure_angle_deg:g}°)/cos({helix_angle_deg:g}°) = {radial_force:g} N",
            radial_force,
            "N",
        ),
        _trace(
            "Axial force magnitude",
            "F_a = F_t tan(β)",
            f"F_a = {tangential_force:g} N × tan({helix_angle_deg:g}°) = {axial_force:g} N",
            axial_force,
            "N",
        ),
    )
    return HelicalGearResult(
        gear_ratio=ratio,
        pinion_pitch_diameter=_q(pinion_diameter, "m"),
        gear_pitch_diameter=_q(gear_diameter, "m"),
        center_distance=_q(center_distance, "m"),
        output_speed=_q(output_speed, "rpm"),
        input_torque=_q(input_torque, "N*m"),
        output_torque=_q(output_torque, "N*m"),
        tangential_force=_q(tangential_force, "N"),
        radial_force=_q(radial_force, "N"),
        axial_force=_q(axial_force, "N"),
        calculation_trace=trace,
        assumptions=_HELICAL_ASSUMPTIONS,
    )
