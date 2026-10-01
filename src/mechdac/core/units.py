"""Unit-aware values used by MechDAC's physical domain models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pint import DimensionalityError, UnitRegistry
from pint.errors import UndefinedUnitError

ureg = UnitRegistry()


class DomainModel(BaseModel):
    """Shared strict configuration for serializable engineering models."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class QuantityValue(DomainModel):
    """A finite scalar paired with a Pint unit expression."""

    value: float = Field(allow_inf_nan=False)
    unit: str = Field(min_length=1)

    @field_validator("unit")
    @classmethod
    def unit_must_be_known(cls, unit: str) -> str:
        try:
            ureg.Unit(unit)
        except (UndefinedUnitError, ValueError, TypeError) as exc:
            raise ValueError(f"unknown unit: {unit}") from exc
        return unit

    def to(self, unit: str) -> float:
        """Return the value expressed in ``unit``, rejecting incompatible dimensions."""

        try:
            return float((self.value * ureg(self.unit)).to(unit).magnitude)
        except DimensionalityError as exc:
            raise ValueError(f"{self.unit!r} is not compatible with {unit!r}") from exc
