import math

import pytest
from pydantic import ValidationError

from mechdac.core.units import QuantityValue


def test_quantity_value_converts_between_compatible_units() -> None:
    length = QuantityValue(value=12, unit="inch")

    assert length.to("m") == pytest.approx(0.3048)


def test_quantity_value_rejects_unknown_units_and_nonfinite_values() -> None:
    with pytest.raises(ValidationError, match="unknown unit"):
        QuantityValue(value=1, unit="made_up_unit")

    for value in (math.inf, -math.inf, math.nan):
        with pytest.raises(ValidationError):
            QuantityValue(value=value, unit="m")


def test_quantity_value_rejects_incompatible_conversion_and_unknown_fields() -> None:
    force = QuantityValue(value=10, unit="N")

    with pytest.raises(ValueError, match="not compatible"):
        force.to("m")
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        QuantityValue(value=10, unit="N", description="extra")


def test_quantity_value_json_round_trip_and_assignment_validation() -> None:
    quantity = QuantityValue(value=2.5, unit="kN")
    restored = QuantityValue.model_validate_json(quantity.model_dump_json())

    assert restored == quantity
    with pytest.raises(ValidationError):
        quantity.value = math.inf
