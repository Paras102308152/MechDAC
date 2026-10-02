"""Physical problem schemas for the beam statics foundation."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from mechdac.core.units import DomainModel, QuantityValue

Direction = Literal["up", "down"]
MomentDirection = Literal["counterclockwise", "clockwise"]
SupportKind = Literal["pin", "roller"]


def _require_dimension(quantity: QuantityValue, unit: str, field: str) -> float:
    try:
        return quantity.to(unit)
    except ValueError as exc:
        raise ValueError(f"{field} must have units compatible with {unit}") from exc


class MaterialSpec(DomainModel):
    """Material property input for a static strength assessment."""

    name: str = Field(min_length=1)
    yield_strength: QuantityValue

    @model_validator(mode="after")
    def yield_strength_is_positive_stress(self) -> MaterialSpec:
        strength = _require_dimension(self.yield_strength, "Pa", "yield strength")
        if strength <= 0:
            raise ValueError("yield strength must be positive")
        return self


class DesignRequirementSpec(DomainModel):
    """A requested minimum dimensionless factor of safety."""

    minimum_factor_of_safety: float = Field(gt=0, allow_inf_nan=False)


class ShaftLoadingSpec(DomainModel):
    """Signed bending moment and torque at one shaft section, plus design inputs."""

    bending_moment: QuantityValue
    torque: QuantityValue
    material: MaterialSpec
    design_requirement: DesignRequirementSpec

    @model_validator(mode="after")
    def loads_are_moments(self) -> ShaftLoadingSpec:
        _require_dimension(self.bending_moment, "N*m", "bending moment")
        _require_dimension(self.torque, "N*m", "torque")
        return self


class SupportSpec(DomainModel):
    """An ideal vertical support located along the beam axis."""

    kind: SupportKind
    position: QuantityValue

    @model_validator(mode="after")
    def position_is_length(self) -> SupportSpec:
        _require_dimension(self.position, "m", "support position")
        return self


class PointLoad(DomainModel):
    """A transverse point force; magnitude is positive and direction is explicit."""

    position: QuantityValue
    magnitude: QuantityValue
    direction: Direction

    @model_validator(mode="after")
    def values_have_expected_dimensions(self) -> PointLoad:
        _require_dimension(self.position, "m", "point-load position")
        magnitude = _require_dimension(self.magnitude, "N", "point-load magnitude")
        if magnitude <= 0:
            raise ValueError("point-load magnitude must be positive")
        return self


class DistributedLoad(DomainModel):
    """A uniformly distributed transverse load over a beam interval."""

    start: QuantityValue
    end: QuantityValue
    intensity: QuantityValue
    direction: Direction

    @model_validator(mode="after")
    def interval_and_intensity_are_valid(self) -> DistributedLoad:
        start = _require_dimension(self.start, "m", "distributed-load start")
        end = _require_dimension(self.end, "m", "distributed-load end")
        intensity = _require_dimension(self.intensity, "N/m", "distributed-load intensity")
        if start >= end:
            raise ValueError("distributed-load start must be before its end")
        if intensity <= 0:
            raise ValueError("distributed-load intensity must be positive")
        return self


class AppliedMoment(DomainModel):
    """A concentrated couple; magnitude is positive and rotation direction is explicit."""

    position: QuantityValue
    magnitude: QuantityValue
    direction: MomentDirection

    @model_validator(mode="after")
    def values_have_expected_dimensions(self) -> AppliedMoment:
        _require_dimension(self.position, "m", "moment position")
        magnitude = _require_dimension(self.magnitude, "N*m", "moment magnitude")
        if magnitude <= 0:
            raise ValueError("applied-moment magnitude must be positive")
        return self


class BeamSpec(DomainModel):
    """A 1D beam with two statically determinate simple supports and applied loads."""

    length: QuantityValue
    supports: tuple[SupportSpec, ...] = Field(min_length=2, max_length=2)
    point_loads: tuple[PointLoad, ...] = ()
    distributed_loads: tuple[DistributedLoad, ...] = ()
    applied_moments: tuple[AppliedMoment, ...] = ()

    @model_validator(mode="after")
    def configuration_is_physically_valid(self) -> BeamSpec:
        length = _require_dimension(self.length, "m", "beam length")
        if length <= 0:
            raise ValueError("beam length must be positive")

        kinds = [support.kind for support in self.supports]
        if kinds.count("pin") != 1 or kinds.count("roller") != 1:
            raise ValueError("supports must contain exactly one pin and one roller")

        support_positions = [support.position.to("m") for support in self.supports]
        if support_positions[0] == support_positions[1]:
            raise ValueError("supports must be at distinct positions")

        positions = [*support_positions]
        positions.extend(load.position.to("m") for load in self.point_loads)
        positions.extend(moment.position.to("m") for moment in self.applied_moments)

        if any(position < 0 or position > length for position in positions):
            raise ValueError("supports and load positions must be within the beam")

        for load in self.distributed_loads:
            if load.start.to("m") < 0 or load.end.to("m") > length:
                raise ValueError("distributed loads must be within the beam")
        return self


class BeamShaftLoadingSpec(DomainModel):
    """Beam loads plus torque and material data for one selected shaft section."""

    beam: BeamSpec
    torque_at_critical_section: QuantityValue
    material: MaterialSpec
    design_requirement: DesignRequirementSpec

    @model_validator(mode="after")
    def torque_is_moment(self) -> BeamShaftLoadingSpec:
        _require_dimension(
            self.torque_at_critical_section,
            "N*m",
            "torque at critical section",
        )
        return self


class SpurGearPairSpec(DomainModel):
    """Geometry and operating point for one external spur gear pair."""

    module: QuantityValue
    pinion_teeth: int = Field(gt=0)
    gear_teeth: int = Field(gt=0)
    pressure_angle: QuantityValue
    input_power: QuantityValue
    pinion_speed: QuantityValue

    @model_validator(mode="after")
    def values_are_physically_valid(self) -> SpurGearPairSpec:
        module = _require_dimension(self.module, "m", "module")
        angle = _require_dimension(self.pressure_angle, "degree", "pressure angle")
        power = _require_dimension(self.input_power, "W", "input power")
        speed = _require_dimension(self.pinion_speed, "rpm", "pinion speed")
        if module <= 0 or power <= 0 or speed <= 0:
            raise ValueError("module, input power, and pinion speed must be positive")
        if not 0 < angle < 90:
            raise ValueError("pressure angle must be between 0 and 90 degrees")
        return self


class HelicalGearPairSpec(DomainModel):
    """Geometry and operating point for one external helical gear pair."""

    normal_module: QuantityValue
    pinion_teeth: int = Field(gt=0)
    gear_teeth: int = Field(gt=0)
    normal_pressure_angle: QuantityValue
    helix_angle: QuantityValue
    input_power: QuantityValue
    pinion_speed: QuantityValue

    @model_validator(mode="after")
    def values_are_physically_valid(self) -> HelicalGearPairSpec:
        module = _require_dimension(self.normal_module, "m", "normal module")
        pressure = _require_dimension(
            self.normal_pressure_angle, "degree", "normal pressure angle"
        )
        helix = _require_dimension(self.helix_angle, "degree", "helix angle")
        power = _require_dimension(self.input_power, "W", "input power")
        speed = _require_dimension(self.pinion_speed, "rpm", "pinion speed")
        if module <= 0 or power <= 0 or speed <= 0:
            raise ValueError("normal module, input power, and pinion speed must be positive")
        if not 0 < pressure < 90:
            raise ValueError("normal pressure angle must be between 0 and 90 degrees")
        if not 0 < helix < 90:
            raise ValueError("helix angle must be between 0 and 90 degrees")
        return self


class CompressionSpringSpec(DomainModel):
    """Input for a static, round-wire compression spring check."""

    load: QuantityValue
    wire_diameter: QuantityValue
    mean_coil_diameter: QuantityValue
    active_coils: int = Field(gt=0)
    shear_modulus: QuantityValue
    allowable_shear_stress: QuantityValue

    @model_validator(mode="after")
    def values_are_physically_valid(self) -> CompressionSpringSpec:
        load = _require_dimension(self.load, "N", "spring load")
        wire = _require_dimension(self.wire_diameter, "m", "wire diameter")
        mean = _require_dimension(self.mean_coil_diameter, "m", "mean coil diameter")
        modulus = _require_dimension(self.shear_modulus, "Pa", "shear modulus")
        allowable = _require_dimension(
            self.allowable_shear_stress, "Pa", "allowable shear stress"
        )
        if min(load, wire, mean, modulus, allowable) <= 0:
            raise ValueError("spring load, dimensions, modulus, and allowable stress must be positive")
        if mean <= wire:
            raise ValueError("mean coil diameter must exceed wire diameter")
        return self


class ShaftKeySpec(DomainModel):
    """Input for a rectangular sunk-key torque-transfer strength check."""

    torque: QuantityValue
    shaft_diameter: QuantityValue
    key_width: QuantityValue
    key_height: QuantityValue
    key_length: QuantityValue
    material: MaterialSpec
    design_requirement: DesignRequirementSpec

    @model_validator(mode="after")
    def values_are_physically_valid(self) -> ShaftKeySpec:
        torque = _require_dimension(self.torque, "N*m", "torque")
        diameter = _require_dimension(self.shaft_diameter, "m", "shaft diameter")
        width = _require_dimension(self.key_width, "m", "key width")
        height = _require_dimension(self.key_height, "m", "key height")
        length = _require_dimension(self.key_length, "m", "key length")
        if min(torque, diameter, width, height, length) <= 0:
            raise ValueError("torque and key/shaft dimensions must be positive")
        if width >= diameter or height >= diameter:
            raise ValueError("key width and height must each be less than shaft diameter")
        return self
