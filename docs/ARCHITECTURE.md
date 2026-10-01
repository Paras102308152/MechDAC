# Architecture

## Current dependency flow

```text
BeamSpec and load/support schemas
        │
        ├── use QuantityValue and Pint dimensional checks
        ▼
solve_beam (deterministic statics equations)
        ▼
BeamAnalysisResult (reactions, diagram points/segments, extrema, assumptions)
```

The current modules are:

- `mechdac.core.units`: `QuantityValue`, one Pint registry, and common Pydantic configuration (`extra="forbid"`, assignment validation).
- `mechdac.core.schema`: physical beam, support, point-load, distributed-load, and applied-moment inputs. It validates unit dimensions, directions, positive magnitudes, support count/type, and beam bounds. It contains no engineering equations.
- `mechdac.solvers.beam`: equilibrium reactions plus piecewise shear and bending moment calculations. It owns the sign conventions used by this solver.
- `mechdac.core.results`: Pydantic output models with reactions, left/right event values, polynomial segment coefficients, extrema, assumptions, warnings, and solver metadata.

Packaging uses a `src/` layout. Pydantic v2 and Pint are runtime dependencies; pytest is a development extra. The supported Python version is 3.12 or later.

## Current modeling and calculation boundary

Schemas hold physical values with units and explicit directions. At the solver boundary, lengths convert to metres, forces to newtons, line loads to newtons per metre, and couples to newton-metres. The deterministic solver then applies static equilibrium and integrates the piecewise shear/moment behavior. Result models hold canonical units and plotting-relevant event/segment information.

The first model is determinate by construction: exactly two distinct supports, one pin and one roller, with only vertical forces and couples. Pin/roller behavior is represented at the vertical-beam level; axial support reactions are out of scope.

## Intended growth path

The next layer should be a small file-input and CLI workflow over these existing schemas and solver. Keep parsing/command behavior outside the calculation equations. Structured results should be serializable for future plotting, trace, and report features.

As new engineering methods are introduced, preserve these boundaries:

```text
physical problem schemas → units → engineering solver(s)
→ structured results/checks → CLI/reporting → eventually CAD
```

Standards-specific equations belong in explicitly named solver methods, not physical input schemas. There is no CLI, reporting module, CAD layer, or general material/gear/bearing schema implemented now; do not create empty placeholders for them.
