# Architecture Decisions

## 2026-10-02 — Freeze additive Monday MVP contracts before component solvers

**Decision:** Add four strict Pydantic input/output pairs to the existing `core.schema` and `core.results` modules before parallel component work: `SpurGearPairSpec`/`SpurGearResult`, `HelicalGearPairSpec`/`HelicalGearResult`, `CompressionSpringSpec`/`CompressionSpringResult`, and `ShaftKeySpec`/`ShaftKeyResult`. Inputs carry `QuantityValue`s, reject extra fields, validate dimensional compatibility and basic physical ranges, and contain no engineering equations. Results use unit-bearing values and the existing `CalculationTraceEntry`, `assumptions`, `warnings`, `solver_name`, and `solver_version` conventions.

**Reason:** Workers can implement separate calculation modules against stable shared model shapes while the established beam and shaft workflows remain unchanged. Component calculations, CLI dispatch, and shared documentation still require separate coordinator integration/review.

**Frozen input conventions:** JSON/YAML objects mirror Pydantic field names; physical quantities are `{ "value": number, "unit": "Pint unit" }`; values are finite and use dimensionally compatible units. Unknown fields are errors. Inputs describe one external gear pair, one static round-wire compression spring, or one rectangular sunk key. Gear mesh forces are magnitudes; direction/vector resolution is outside these contracts.

**Frozen result fields:** `SpurGearResult` exposes gear ratio, both pitch diameters, center distance, output speed, input/output torque, tangential force, and radial force. `HelicalGearResult` has the same fields plus axial force. `CompressionSpringResult` exposes spring index, Wahl factor, maximum and allowable shear stress, load deflection, spring rate, and shear-stress utilization (actual/allowable). `ShaftKeyResult` exposes key shear and bearing stresses, required length for each mode, the governing required length, and shear/bearing factors of safety. All result models include shared trace, assumptions, warnings, solver name, and solver version fields. No generic report/check abstraction is added.

**Frozen trace and limits:** Each `CalculationTraceEntry` names a step and supplies a readable equation, numeric substitution, and unit-bearing result. Results state idealizations and exclusions in `assumptions`; `warnings` report cautionary conditions, with an empty tuple serialized as `[]`. These are method-specific numerical checks, not standards-compliance certificates.

**Frozen presentation/errors:** `--format text` is the default and presents a workflow title, solver/version, primary outputs with units, each trace equation/substitution, assumptions, and warnings (`none` when empty). `--format json` emits the complete result model as indented JSON, preserving numeric values and unit strings. YAML/JSON parse, Pydantic validation, and solver-domain errors use the existing concise `mechdac: error:` stderr path and exit status 2, without tracebacks for expected input errors.

**Frozen CLI names:** `mechdac gear spur INPUT`, `mechdac gear helical INPUT`, `mechdac spring compression INPUT`, and `mechdac key check INPUT`; each accepts the existing `--format text|json` output option. These names are contracts only until coordinator wiring is integrated.

**Source-validation convention:** Each component's tests use a generic numerical worked example from the supplied source, state the book chapter/section/example and printed page in a nearby test comment, and independently assert the published intermediate/final values with tolerances. Reference cases: spur gear Bhandari Ex. 17.2 (pp. 660–661); helical gear Ex. 18.2 (pp. 699–700); compression spring Ex. 10.1 (pp. 407–408); rectangular key Ex. 9.14 (p. 352). Keep source maps and the shared source ledger coordinator-owned; do not copy textbook prose or pages into the repository. Passing a worked-example regression is evidence for that case, not broad certification.

**Worker ownership:** Gear owns `src/mechdac/solvers/gears.py`, `tests/test_gears.py`, and `docs/sources/bhandari/ch17/SOURCE_MAP.md`; spring owns `src/mechdac/solvers/springs.py`, `tests/test_springs.py`, and `docs/sources/bhandari/ch10/SOURCE_MAP.md`; key owns `src/mechdac/solvers/keys.py` and `tests/test_keys.py` (Chapter 9 source map is read-only). Workers must not edit the shared schemas/results/units, CLI, package metadata, existing beam/shaft code/tests/examples, README, status/roadmap/decision/architecture/design docs, or shared source ledger. The coordinator owns CLI and shared documentation/ledger integration.

**Alternatives considered:** Have each worker define its own Pydantic inputs/results; introduce generic calculation/check/report frameworks; allow workers to edit the CLI and shared source registry.

**Consequences:** The first gear slice covers external spur/helical pitch geometry, ideal speed/torque transfer, and mesh-force magnitudes only; the spring slice covers static compression load, corrected shear stress, deflection, rate, and allowable-stress utilization; the key slice covers a rectangular sunk key's shear/bearing strength and required length. For the key check, use the textbook maximum-shear basis for key shear yield (yield strength divided by two) and yield strength for bearing; apply the requested factor of safety to both. The spring's active coil count is the effective count; end shape and solid-height geometry are not modeled. The result fields capture these useful outputs without claiming a standard-specific rating. Text reports present inputs/outputs, trace, assumptions, and warnings; JSON is the full Pydantic result document. Validation and solver errors use the existing CLI's concise error path and nonzero status. No plot route is frozen for these workflows.

## 2026-10-02 — Keep beam plotting optional and downstream of structured results

**Decision:** Provide `mechdac beam plot` through a separate plotting adapter that consumes `BeamAnalysisResult`; install Matplotlib only through the `plotting` extra. The adapter evaluates returned segment polynomials and event-side values, leaving statics in the solver.

**Reason:** SFD/BMD plots make the existing beam results easier to inspect without making Matplotlib a requirement for calculation or package imports, and without duplicating engineering calculations.

**Alternatives considered:** Make Matplotlib a core dependency; recalculate diagram values in the plotting layer; defer all visual output.

**Consequences:** PNG and SVG diagrams are available when the optional extra is installed. The default package import and non-plot CLI commands do not import Matplotlib. Segment curves are sampled for rendering, while event-side values preserve discontinuities at concentrated forces and couples.

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

## 2026-10-02 — Record textbook provenance in source maps and a ledger

**Decision:** Keep page-aware textbook method maps and validation statuses in `docs/sources/`; do not add a runtime provenance framework for this first source-validation mission. Verify the existing static shaft implementation against the generic distortion-energy equations in Bhandari Chapter 4, and explicitly record that Bhandari Chapter 9's worked shaft sizing uses maximum shear (Tresca).

**Reason:** Source evidence and equation selection need to be durable and reviewable. The current solver already exposes its method name, assumptions, and calculation trace; a ledger is enough to record book/page provenance without coupling the solver to one textbook.

**Alternatives considered:** Rename the generic method as Bhandari/ASME; implement a second failure criterion or a broad source registry in the same mission; copy textbook pages or lengthy text into the repository.

**Consequences:** The generic von Mises calculation remains unchanged. The source ledger distinguishes verified equations, documented criterion differences, and future Chapter 9 capabilities. Future source-specific methods can be added as separate solver behavior only under a bounded, validated mission.
