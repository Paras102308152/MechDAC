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

## Serialization and units

`QuantityValue` serializes as a finite scalar and a Pint unit expression. Schemas validate dimensional compatibility; the solver converts to canonical SI values before arithmetic. Pydantic JSON methods can serialize the beam input and structured result. Unknown schema fields are rejected.

The CLI accepts a mapping at the document root, with beam fields matching `BeamSpec`. `.json` files use Python's standard JSON parser; `.yaml` and `.yml` use PyYAML's safe loader. CLI errors return exit code 2 and go to stderr. Default text output is for terminal reading; `--format json` writes the complete structured solver result to stdout.

## Not implemented

There is no varying distributed-load function, diagram plot renderer, beam deflection, axial force, gear force, bearing behavior, shaft torsion/stress, standards rating, CAD, optimization, or reporting. These are future decisions, not implicit behavior of the current solver.
