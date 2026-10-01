# MechDAC Roadmap

Roadmap status reflects code that exists and has been verified, not planned architecture.

## Phase 0 — Understand and document

**Complete.** Repository structure and current implementation have been inspected; project memory documents are being established.

## Phase 1 — Repository and domain foundation

**Partially complete.** Python packaging, Pydantic/Pint quantity support, beam-specific physical schemas/results, and tests are in place. The broader reusable models (material, design requirements, shaft loading, gear pair, bearing load, load case, checks, and general solver results) remain deferred until a concrete use requires them.

## Phase 2 — Beam/shaft statics foundation

**Complete for the initial determinate beam scope.** Supports one pin and one roller, vertical point loads, uniform distributed loads, and applied couples. Calculates reactions and structured shear/moment diagrams and extrema. No shaft stress or design equations are included.

## Phase 3 — First end-to-end workflow

**Next.** Build a narrow workflow that accepts a documented YAML or JSON beam input, validates it, runs the solver, and prints a useful summary with structured result serialization. Add a CLI entry point, actionable errors, and a generic textbook-style example. Verify parsing and displayed numerical results with tests.

## Phase 4 — Calculation transparency

Add auditable input/assumption provenance and calculation trace details if they improve inspection of the beam results. Plot SFD/BMD only after the result model can supply plotting without repeating physics.

## Phase 5 — Shaft design

Extend the beam foundation with torque and a critical shaft section, then add stress and sizing methods with explicit standards/criteria, assumptions, analytical verification, and design checks. Keep those equations in solver modules.

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
