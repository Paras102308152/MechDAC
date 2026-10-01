# MechDAC Roadmap

Roadmap status reflects code that exists and has been verified, not planned architecture.

## Phase 0 — Understand and document

**Complete.** Repository structure and current implementation have been inspected; persistent project memory is established in the root and `docs/` files.

## Phase 1 — Repository and domain foundation

**Partially complete.** Python packaging, Pydantic/Pint quantity support, beam-specific physical schemas/results, and tests are in place. The broader reusable models (material, design requirements, shaft loading, gear pair, bearing load, load case, checks, and general solver results) remain deferred until a concrete use requires them.

## Phase 2 — Beam/shaft statics foundation

**Complete for the initial determinate beam scope.** Supports one pin and one roller, vertical point loads, uniform distributed loads, and applied couples. Calculates reactions and structured shear/moment diagrams and extrema. No shaft stress or design equations are included.

## Phase 3 — First end-to-end workflow

**Complete.** `mechdac beam solve INPUT` accepts YAML/YML and JSON; Pydantic validates the physical schema, the deterministic solver runs, and output is readable text or structured JSON. The CLI has actionable input errors, tests, a generic example, and README instructions.

## Phase 4 — Calculation transparency

**Complete for calculation transparency.** Results contain the signed external force resultant, moment about support A, reaction equations/substitutions, and numerical results with units. CLI text prints the trace and JSON includes it with piecewise SFD/BMD data. A plot renderer is deferred; output already provides exact segment coefficients without introducing a plotting dependency.

## Phase 5 — Shaft design

**Next.** Begin with a clearly scoped solid-round-shaft static bending/torsion screen, separate material/design inputs from equations, document the chosen generic yield criterion, and verify against analytical cases. Do not represent a generic criterion as ASME/AGMA/ISO compliance. Defer fatigue, stress concentrations, standard-diameter tables, and broader shaft-system coupling until justified.

## Phase 6 — Additional mechanical primitives

Choose keys, bearings, gears, fasteners, springs, pressure vessels, or another component only when there is a clear user need. Do not implement a breadth-first catalog.

## Phase 7 — Parametric CAD

Evaluate a CAD dependency only after calculation models are stable. Any geometry workflow should validate geometry and preserve links to calculation inputs/results.

## Phase 8 — Reporting

Consider calculation reports, plots, assumptions, and BOM output after traceable calculations and stable structured results exist.

## Phase 9 — Polish and release readiness

Improve documentation, examples, public API, CLI UX, error handling, packaging, and release process based on the completed vertical slice.

## Deferred

- Gear/bearing/shaft calculations and standards equations
- Fatigue, stress, shaft sizing, and safety-factor checks
- CAD, optimization, report/PDF generation, and AI functionality
- Web services, databases, GUI frameworks, and complex plugin systems
