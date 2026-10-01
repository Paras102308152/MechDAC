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
