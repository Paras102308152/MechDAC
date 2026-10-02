"""Contract tests for the Monday MVP input and result models."""

import pytest
from pydantic import ValidationError

from mechdac.core.results import (
    CompressionSpringResult,
    HelicalGearResult,
    ShaftKeyResult,
    SpurGearResult,
)
from mechdac.core.schema import (
    CompressionSpringSpec,
    HelicalGearPairSpec,
    ShaftKeySpec,
    SpurGearPairSpec,
)
from mechdac.core.units import QuantityValue


def q(value: float, unit: str) -> QuantityValue:
    return QuantityValue(value=value, unit=unit)


def test_spur_gear_contract_accepts_unit_bearing_input_and_json_round_trip() -> None:
    spec = SpurGearPairSpec(
        module=q(5, "mm"),
        pinion_teeth=20,
        gear_teeth=60,
        pressure_angle=q(20, "degree"),
        input_power=q(3.5, "kW"),
        pinion_speed=q(700, "rpm"),
    )
    assert SpurGearPairSpec.model_validate_json(spec.model_dump_json()) == spec


def test_helical_gear_contract_accepts_explicit_hand_and_rotation() -> None:
    spec = HelicalGearPairSpec(
        normal_module=q(5, "mm"),
        pinion_teeth=20,
        gear_teeth=60,
        normal_pressure_angle=q(20, "degree"),
        helix_angle=q(30, "degree"),
        input_power=q(5, "kW"),
        pinion_speed=q(720, "rpm"),
    )
    assert HelicalGearPairSpec.model_validate_json(spec.model_dump_json()) == spec


def test_compression_spring_contract_accepts_dimensions_and_material_property() -> None:
    spec = CompressionSpringSpec(
        load=q(1250, "N"),
        wire_diameter=q(7, "mm"),
        mean_coil_diameter=q(42, "mm"),
        active_coils=8,
        shear_modulus=q(81370, "MPa"),
        allowable_shear_stress=q(545, "MPa"),
    )
    assert CompressionSpringSpec.model_validate_json(spec.model_dump_json()) == spec


def test_shaft_key_contract_accepts_rectangular_key_and_strength_requirement() -> None:
    spec = ShaftKeySpec(
        torque=q(475, "N*m"),
        shaft_diameter=q(50, "mm"),
        key_width=q(16, "mm"),
        key_height=q(10, "mm"),
        key_length=q(50, "mm"),
        material={"name": "test material", "yield_strength": q(230, "MPa")},
        design_requirement={"minimum_factor_of_safety": 3},
    )
    assert ShaftKeySpec.model_validate_json(spec.model_dump_json()) == spec


@pytest.mark.parametrize(
    ("model", "data"),
    [
        (SpurGearPairSpec, {"module": {"value": 5, "unit": "mm"}, "pinion_teeth": 0,
                            "gear_teeth": 60, "pressure_angle": {"value": 20, "unit": "degree"},
                            "input_power": {"value": 3.5, "unit": "kW"},
                            "pinion_speed": {"value": 700, "unit": "rpm"}}),
        (HelicalGearPairSpec, {"normal_module": {"value": 5, "unit": "mm"}, "pinion_teeth": 20,
                               "gear_teeth": 60, "normal_pressure_angle": {"value": 20, "unit": "degree"},
                               "helix_angle": {"value": 90, "unit": "degree"},
                               "input_power": {"value": 5, "unit": "kW"},
                               "pinion_speed": {"value": 720, "unit": "rpm"}}),
        (CompressionSpringSpec, {"load": {"value": 1250, "unit": "N"},
                                 "wire_diameter": {"value": 7, "unit": "mm"},
                                 "mean_coil_diameter": {"value": 5, "unit": "mm"}, "active_coils": 8,
                                 "shear_modulus": {"value": 81370, "unit": "MPa"},
                                 "allowable_shear_stress": {"value": 545, "unit": "MPa"}}),
        (ShaftKeySpec, {"torque": {"value": 475, "unit": "N*m"},
                        "shaft_diameter": {"value": 50, "unit": "mm"},
                        "key_width": {"value": 50, "unit": "mm"}, "key_height": {"value": 10, "unit": "mm"},
                        "key_length": {"value": 50, "unit": "mm"},
                        "material": {"name": "test", "yield_strength": {"value": 230, "unit": "MPa"}},
                        "design_requirement": {"minimum_factor_of_safety": 3}}),
    ],
)
def test_input_contracts_reject_impossible_values(model, data) -> None:
    with pytest.raises(ValidationError):
        model.model_validate(data)


@pytest.mark.parametrize(
    ("model", "payload"),
    [
        (SpurGearPairSpec, {"module": {"value": 5, "unit": "mm"}, "pinion_teeth": 20,
                            "gear_teeth": 60, "pressure_angle": {"value": 20, "unit": "degree"},
                            "input_power": {"value": 3.5, "unit": "kW"},
                            "pinion_speed": {"value": 700, "unit": "rpm"}, "extra": 1}),
        (HelicalGearPairSpec, {"normal_module": {"value": 5, "unit": "mm"}, "pinion_teeth": 20,
                               "gear_teeth": 60, "normal_pressure_angle": {"value": 20, "unit": "degree"},
                               "helix_angle": {"value": 30, "unit": "degree"},
                               "input_power": {"value": 5, "unit": "kW"},
                               "pinion_speed": {"value": 720, "unit": "rpm"}, "extra": 1}),
        (CompressionSpringSpec, {"load": {"value": 1250, "unit": "N"},
                                 "wire_diameter": {"value": 7, "unit": "mm"},
                                 "mean_coil_diameter": {"value": 42, "unit": "mm"}, "active_coils": 8,
                                 "shear_modulus": {"value": 81370, "unit": "MPa"},
                                 "allowable_shear_stress": {"value": 545, "unit": "MPa"}, "extra": 1}),
        (ShaftKeySpec, {"torque": {"value": 475, "unit": "N*m"},
                        "shaft_diameter": {"value": 50, "unit": "mm"},
                        "key_width": {"value": 16, "unit": "mm"}, "key_height": {"value": 10, "unit": "mm"},
                        "key_length": {"value": 50, "unit": "mm"},
                        "material": {"name": "test", "yield_strength": {"value": 230, "unit": "MPa"}},
                        "design_requirement": {"minimum_factor_of_safety": 3}, "extra": 1}),
    ],
)
def test_input_contracts_reject_unknown_fields(model, payload) -> None:
    with pytest.raises(ValidationError):
        model.model_validate(payload)


def test_input_contracts_reject_incompatible_quantity_units() -> None:
    with pytest.raises(ValidationError, match="compatible"):
        SpurGearPairSpec(
            module=q(5, "N"), pinion_teeth=20, gear_teeth=60,
            pressure_angle=q(20, "degree"), input_power=q(3.5, "kW"),
            pinion_speed=q(700, "rpm"),
        )


def test_result_contracts_share_trace_assumption_warning_and_metadata_conventions() -> None:
    common = {
        "calculation_trace": [{"name": "example", "equation": "x = a", "substitution": "x = 1",
                               "result": {"value": 1, "unit": "dimensionless"}}],
        "assumptions": ["documented assumption"],
        "warnings": [],
    }
    results = [
        SpurGearResult.model_validate({"gear_ratio": 3, "pinion_pitch_diameter": {"value": 0.1, "unit": "m"},
                                       "gear_pitch_diameter": {"value": 0.3, "unit": "m"},
                                       "center_distance": {"value": 0.2, "unit": "m"},
                                       "output_speed": {"value": 700/3, "unit": "rpm"},
                                       "input_torque": {"value": 47.7, "unit": "N*m"},
                                       "output_torque": {"value": 143.1, "unit": "N*m"},
                                       "tangential_force": {"value": 954, "unit": "N"},
                                       "radial_force": {"value": 347, "unit": "N"}, **common}),
        HelicalGearResult.model_validate({"gear_ratio": 3, "pinion_pitch_diameter": {"value": 0.115, "unit": "m"},
                                          "gear_pitch_diameter": {"value": 0.345, "unit": "m"},
                                          "center_distance": {"value": 0.23, "unit": "m"},
                                          "output_speed": {"value": 240, "unit": "rpm"},
                                          "input_torque": {"value": 66.3, "unit": "N*m"},
                                          "output_torque": {"value": 198.9, "unit": "N*m"},
                                          "tangential_force": {"value": 1150, "unit": "N"},
                                          "radial_force": {"value": 483, "unit": "N"},
                                          "axial_force": {"value": 663, "unit": "N"}, **common}),
        CompressionSpringResult.model_validate({"spring_index": 6, "wahl_factor": 1.25,
                                                "maximum_shear_stress": {"value": 400, "unit": "MPa"},
                                                "allowable_shear_stress": {"value": 545, "unit": "MPa"},
                                                "deflection": {"value": 0.03, "unit": "m"},
                                                "spring_rate": {"value": 41600, "unit": "N/m"},
                                                "shear_stress_utilization": 0.74, **common}),
        ShaftKeyResult.model_validate({"key_shear_stress": {"value": 23.75, "unit": "MPa"},
                                       "key_bearing_stress": {"value": 76, "unit": "MPa"},
                                       "required_length_in_shear": {"value": 0.05, "unit": "m"},
                                       "required_length_in_bearing": {"value": 0.04956, "unit": "m"},
                                       "required_key_length": {"value": 0.05, "unit": "m"},
                                       "shear_factor_of_safety": 4.84, "bearing_factor_of_safety": 3.03,
                                       **common}),
    ]
    for result in results:
        assert result.model_validate_json(result.model_dump_json()) == result
