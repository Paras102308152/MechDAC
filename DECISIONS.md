# Architecture Decisions

## 2026-10-01 — Keep physical schemas independent of engineering equations

**Decision:** Beam and load models describe geometry, directions, magnitudes, and support types. Equilibrium and diagram calculations live in solver modules.

**Reason:** The same physical problem should be reusable with different future methods, and validation should not encode an engineering standard.

**Alternatives considered:** Put equations or standard-specific checks on the Pydantic schemas; use a single model for input and calculation output.

**Consequences:** `BeamSpec` is validated before `solve_beam` runs. Future AGMA/ASME/ISO/DIN methods belong in separate solvers or checks, not in these schemas.

## 2026-10-01 — Store quantities as finite values plus unit expressions

**Decision:** `QuantityValue` stores a numeric value and Pint-compatible unit string; calculations convert inputs to SI units at the solver boundary and results use metres, newtons, and newton-metres.

**Reason:** Pydantic models serialize cleanly while Pint provides dimensional compatibility and conversion.

**Alternatives considered:** Store Pint `Quantity` objects directly in models; require users to enter SI only.

**Consequences:** Unit values round-trip through JSON. Dimensional validation is part of physical schemas; internal solver arithmetic uses canonical floats after conversion.

## 2026-10-01 — Start with one pin and one roller for determinate vertical statics

**Decision:** Accept exactly two distinct supports, one pin and one roller. This first solver resolves vertical reactions only and accepts explicit up/down forces and clockwise/counterclockwise couples.

**Reason:** This is a small, general determinate model that is enough to establish verified beam statics without creating a full support/redundancy framework.

**Alternatives considered:** Support arbitrary support counts/types now; add beam deflection and compatibility equations; model axial reaction behavior.

**Consequences:** The solver does not handle overconstrained supports or axial loading. Support location need not be at a beam endpoint, but must be distinct and within the beam.

## 2026-10-01 — Return plot-ready piecewise diagram data

**Decision:** Return event positions with left/right shear and moment values plus segment polynomial coefficients.

**Reason:** Concentrated loads and couples create jumps, while uniform loads create linear shear and quadratic moment between events. A single value per position would lose jump information; a plotter should not have to recalculate statics.

**Alternatives considered:** Return only a dense sampled array; return only reactions and let each plotting feature recompute diagrams.

**Consequences:** Results contain canonical-unit coefficients and enough data to evaluate each interval. Plot rendering itself remains deferred.

## 2026-10-01 — Keep file parsing and presentation in a small CLI layer

**Decision:** Provide `mechdac beam solve INPUT`, accept JSON with the standard library and YAML with PyYAML safe loading, and support readable text plus `--format json` output. The CLI validates through `BeamSpec` and calls the existing solver.

**Reason:** This completes a usable workflow without moving engineering calculations into command code or adding a web/UI framework.

**Alternatives considered:** Require Python callers only; use a different command structure; add a report or plotting dependency as part of the first CLI.

**Consequences:** PyYAML is the only new runtime dependency. Parsing, validation, solving, and display have separate boundaries. CLI output includes a numeric reaction trace; plotting remains deferred.

## 2026-10-01 — Include equilibrium substitutions in beam results

**Decision:** Store the external force resultant, moment about support A, and both support-reaction equations/substitutions as structured trace entries. Show them in text CLI output and include them in JSON results.

**Reason:** Reactions are the first consequential derived values in a beam calculation. Showing their signed load contributions helps students audit the result while keeping presentation separate from solver math.

**Alternatives considered:** Return only final reactions; emit unstructured log text from the solver; introduce a symbolic algebra dependency.

**Consequences:** Trace entries have an equation, numeric substitution, and unit-bearing result. Piecewise diagram coefficients expose the remaining shear/moment behavior. This is a numerical trace, not a symbolic equation engine or standards-compliance report.

## 2026-10-01 — Keep initial shaft yield sizing standalone and generic

**Decision:** Add a separate one-section solid circular shaft solver taking bending moment, torque, yield strength, and a minimum static factor of safety. Use nominal elastic bending/torsion stresses and the von Mises distortion-energy criterion to solve for minimum diameter. Keep these equations in `solvers/shafts.py`; Pydantic schemas contain only physical and design inputs.

**Reason:** This creates a useful, testable static shaft capability without implying a complete shaft-system designer or a standard-specific rating. Explicit moments avoid guessing how beam bending planes or torque distributions map to a rotating shaft.

**Alternatives considered:** Embed equations in schemas; label the method as an ASME shaft design; infer shaft loads from beam output before a section mapping is defined.

**Consequences:** CLI inputs provide moments at one critical section. The result trace shows sizing and stress substitutions. This generic static screen omits fatigue, stress concentrations, axial loading, deflection, and standard diameters. Beam-to-shaft composition is a separate input and result path.

## 2026-10-01 — Compose one-plane beam bending with explicit section torque

**Decision:** Add a separate input for a beam plus torque specified at the beam solver's reported maximum-absolute-moment section. Return both full solver results and the selected location. Keep the standalone shaft-loading workflow available.

**Reason:** This creates an end-to-end beam-to-shaft statics path without inferring torque distribution, bending in another plane, or shaft geometry from a one-plane beam model.

**Alternatives considered:** Automatically infer shaft torque; combine beam moments from multiple planes without a physical model; silently select a section and omit the beam result from outputs.

**Consequences:** The composition reports that torque is taken at the selected beam section. Only one reported maximum section is sized; tied peaks, other sections, and multiple bending planes are not evaluated. Both component results remain available in structured output.
