"""Independent equation checks grounded in the supplied Bhandari chapters."""

from math import pi, sqrt

import pytest

from mechdac.core.schema import (
    DesignRequirementSpec,
    MaterialSpec,
    QuantityValue,
    ShaftLoadingSpec,
)
from mechdac.solvers.shafts import solve_shaft


def test_shaft_sizing_matches_bhandari_distortion_energy_principal_stress_route() -> None:
    """Cross-check the solver through principal stresses and the DE criterion.

    Source: Bhandari Ch. 4, §§4.13 and 4.17, Eq. (4.44), printed pp. 105, 112;
    Ch. 9, §9.2, Eqs. (9.2), (9.3), and (9.6), printed p. 332.
    The input values below are generic validation data, not textbook example data.
    """
    spec = ShaftLoadingSpec(
        bending_moment=QuantityValue(value=0.42, unit="kN*m"),
        torque=QuantityValue(value=0.09, unit="kN*m"),
        material=MaterialSpec(
            name="validation material",
            yield_strength=QuantityValue(value=310, unit="MPa"),
        ),
        design_requirement=DesignRequirementSpec(minimum_factor_of_safety=2.3),
    )

    result = solve_shaft(spec)

    # Evaluate the textbook's circular-shaft stress equations at an arbitrary
    # reference diameter, then use its principal-stress form of distortion
    # energy (σ3 = 0) to solve for the diameter by cubic stress scaling.
    reference_diameter = 0.05  # m
    bending_stress = 32 * 420 / (pi * reference_diameter**3)  # 0.42 kN·m = 420 N·m
    torsional_shear = 16 * 90 / (pi * reference_diameter**3)  # 0.09 kN·m = 90 N·m
    principal_radius = sqrt((bending_stress / 2) ** 2 + torsional_shear**2)
    principal_1 = bending_stress / 2 + principal_radius
    principal_2 = bending_stress / 2 - principal_radius
    equivalent_stress = sqrt(principal_1**2 - principal_1 * principal_2 + principal_2**2)
    expected_diameter = reference_diameter * (
        2.3 * equivalent_stress / 310e6
    ) ** (1 / 3)

    assert result.minimum_required_diameter.to("m") == pytest.approx(
        expected_diameter, rel=1e-12
    )
    assert result.bending_stress.to("Pa") == pytest.approx(
        32 * 420 / (pi * expected_diameter**3), rel=1e-12
    )
    assert result.torsional_shear_stress.to("Pa") == pytest.approx(
        16 * 90 / (pi * expected_diameter**3), rel=1e-12
    )
    assert result.equivalent_stress.to("Pa") == pytest.approx(310e6 / 2.3, rel=1e-12)
    assert result.factor_of_safety == pytest.approx(2.3, rel=1e-12)
    assert (
        "The material is assumed ductile, homogeneous, isotropic, and linear-elastic up to yield."
        in result.assumptions
    )


def test_bhandari_example_4_13_reproduces_the_documented_criterion_difference() -> None:
    """Reproduce the shaft inputs and distinguish the two yield criteria.

    Source: Bhandari Ch. 4, Ex. 4.13, pp. 115–116. The example uses
    maximum-shear (Tresca); MechDAC uses distortion energy (von Mises).
    """
    bending_moment = 250  # N·m = 250 kN·mm in the source example
    torque = 500  # N·m = 500 kN·mm in the source example
    yield_strength = 380e6  # Pa
    factor_of_safety = 2
    spec = ShaftLoadingSpec(
        bending_moment=QuantityValue(value=0.25, unit="kN*m"),
        torque=QuantityValue(value=0.5, unit="kN*m"),
        material=MaterialSpec(
            name="source-example material",
            yield_strength=QuantityValue(value=380, unit="MPa"),
        ),
        design_requirement=DesignRequirementSpec(
            minimum_factor_of_safety=factor_of_safety
        ),
    )

    result = solve_shaft(spec)

    # Independently size from the source's nominal solid-circle stresses.
    # MechDAC uses sqrt(sigma_b**2 + 3*tau**2); Example 4.13 uses maximum
    # shear = sqrt((sigma_b / 2)**2 + tau**2) with allowable shear Sy/(2*n).
    von_mises_stress_coefficient = sqrt(
        (32 * bending_moment / pi) ** 2 + 3 * (16 * torque / pi) ** 2
    )
    expected_mechdac_diameter = (
        von_mises_stress_coefficient / (yield_strength / factor_of_safety)
    ) ** (1 / 3)
    tresca_stress_coefficient = 16 * sqrt(bending_moment**2 + torque**2) / pi
    source_tresca_diameter = (
        tresca_stress_coefficient
        / (yield_strength / (2 * factor_of_safety))
    ) ** (1 / 3)

    assert result.minimum_required_diameter.to("m") == pytest.approx(
        expected_mechdac_diameter, rel=1e-12
    )
    assert source_tresca_diameter == pytest.approx(0.0310616, rel=1e-6)
    assert expected_mechdac_diameter == pytest.approx(0.0299276, rel=1e-6)
    assert source_tresca_diameter != pytest.approx(expected_mechdac_diameter)
