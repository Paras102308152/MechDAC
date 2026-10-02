# Engineering and Design Notes

## Beam sign convention

- Beam axis coordinate `x` increases from the left end toward the right.
- Upward vertical forces and support reactions are positive.
- Downward forces are negative in equilibrium and diagram calculations.
- Counterclockwise applied couples are positive; clockwise couples are negative.
- Positive internal bending moment is sagging.
- Input magnitudes must be positive; a separate direction field carries the sign.

## Current beam assumptions

- The model is a one-dimensional beam in a single vertical plane.
- Supports consist of exactly one pin and one roller at distinct positions.
- Both supports contribute vertical reactions. Horizontal reaction behavior is not modeled because axial loads are out of scope.
- Loads are static. The solver models point forces, uniform distributed forces on intervals, and concentrated applied couples.
- Overlapping uniform loads superpose.
- Beam self-weight is not inferred; include it as a distributed load if needed.
- No deflection, material response, stress, fatigue, safety factor, or sizing calculation is performed.

## Diagram result interpretation

`ShearForcePoint` and `BendingMomentPoint` expose left and right values at event positions, preserving discontinuities from point forces and couples. Each `DiagramSegment` describes an interval using local distance `s = x - start` in metres:

```text
V(s) = shear_start + shear_slope*s
M(s) = moment_start + moment_slope*s + shear_slope*s²/2
```

The segment coefficients use canonical units: shear in N, shear slope in N/m, moment in N·m, moment slope in N, and positions in m. A plotter can evaluate the returned piecewise functions without recomputing support reactions.

The solver searches event-side values and interval endpoints for peak shear/moment. Under a uniform load, it also checks the internal location where shear is zero, which is a stationary bending-moment point. Only one location is reported for a tied absolute maximum.

## Reaction calculation trace

The result records four auditable steps: total external vertical force, external moment about the left support A, right support reaction from moment equilibrium, and left support reaction from vertical force equilibrium. Distributed loads are reduced to their signed resultant at the interval centroid for this equilibrium trace. Applied couples enter the moment sum directly. Each step carries the equation, substituted values, and unit-bearing result. Shear/moment interval polynomials then expose how those reactions and loads continue through the beam.

## Static solid-shaft sizing assumptions

The separate `shaft size` calculation accepts bending moment and torque at one critical section, material yield strength, and a requested minimum static factor of safety. It assumes a solid, circular, prismatic shaft under static bending and torsion only. It uses nominal elastic stresses, `σ_b = 32|M|/(πd³)` and `τ = 16|T|/(πd³)`, and a von Mises yield screen, `σ_vm = sqrt(σ_b² + 3τ²)`. The minimum diameter is solved by setting `σ_vm = S_y/n_min`. Inputs are converted to N·m and Pa, and the result reports metres, Pa, the achieved factor of safety, and each calculation step.

This is a generic textbook static yield screen, not an ASME shaft rating or a fatigue design. The standalone solver takes its section moments directly. A separate `size-from-beam` path uses the beam's maximum absolute moment at its reported location, as described below. The shaft model omits stress concentrations, keyways, shoulders, axial stress, deflection, fatigue, transient loads, and standard diameter selection. Finite input values outside the representable calculation range are rejected with a value error rather than producing a non-finite result.

### Source verification boundary

The supplied Bhandari Chapter 4 gives the general flexure and torsion relations and a biaxial distortion-energy criterion. Reducing its circular-section properties yields the nominal stress formulas above; using its principal-stress form for `σ₃ = 0` is algebraically equivalent to `σ_vm = sqrt(σ_b² + 3τ²)`. `tests/test_source_validation.py` checks the solver through that independent principal-stress route with unit-converted inputs. Factor of safety is compared as `S_y / σ_vm` against the requested minimum.

The source flexure derivation assumes a straight, uniform member, transverse planar loading, homogeneous isotropic Hookean material, and plane sections remaining plane. Its torsion derivation assumes a straight circular shaft, homogeneous isotropic Hookean material, and plane sections remaining plane after twist. MechDAC's shaft is solid, circular, and prismatic and uses nominal elastic stresses. The selected von Mises yield screen further assumes ductile yielding. The result now states these material assumptions; Pydantic cannot establish them from `MaterialSpec.name`, so they remain caller responsibilities.

Bhandari Chapter 9 §9.2 uses the same nominal bending/torsion stresses but develops shaft sizing with maximum shear (Tresca). Its Example 9.1 also uses a multi-plane pulley load model. Example 4.13 is independently reproduced in the source ledger: its Tresca diameter is 31.06 mm; the same moments, material, and factor produce 29.93 mm under MechDAC's von Mises criterion. This is an expected criterion difference, not a like-for-like regression. The method must not be described as a Bhandari §9.2 or ASME design. Source locations and further boundaries are recorded in `docs/sources/bhandari/SOURCE_LEDGER.md`.

## Beam-to-shaft composition

`shaft size-from-beam` runs the beam solver and uses its reported maximum absolute bending moment and position. The input torque is explicitly defined at that reported section, after which the static shaft sizing solver runs. This is a single-plane, single-selected-section mapping. If equal maximum moments occur at multiple positions, only the beam result's reported position is used; torque at other sections is not considered. The composition does not derive a torsion distribution or combine bending from multiple planes.

## Serialization and units

`QuantityValue` serializes as a finite scalar and a Pint unit expression. Schemas validate dimensional compatibility; the solvers convert to canonical SI values before arithmetic. Pydantic JSON methods serialize beam and shaft inputs and structured results, including both nested results from the composed workflow. Unknown schema fields are rejected.

The CLI accepts a mapping at the document root, with fields matching `BeamSpec`, `ShaftLoadingSpec`, or `BeamShaftLoadingSpec` according to the command. `.json` files use Python's standard JSON parser; `.yaml` and `.yml` use PyYAML's safe loader. CLI errors return exit code 2 and go to stderr. Default text output is for terminal reading; `--format json` writes the complete structured solver result to stdout.

## Not implemented

There is no varying distributed-load function, diagram plot renderer, beam deflection, axial force, gear force, bearing behavior, general beam/shaft load-transfer model beyond the described one-section composition, fatigue, standards rating, CAD, optimization, or reporting. These are future decisions, not implicit behavior of the current solvers.
