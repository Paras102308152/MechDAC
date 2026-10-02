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
        │
        └── optional mechdac.plotting.beam → PNG/SVG diagrams

ShaftLoadingSpec + material/design inputs
        │
        ▼
solve_shaft (generic static solid-round bending/torsion yield sizing)
        ▼
ShaftDesignResult (diameter, nominal stresses, factor of safety, trace)

BeamShaftLoadingSpec (beam + torque at selected section + material/design inputs)
        │
        ├── solve_beam → maximum absolute bending moment and location
        └── solve_shaft → static section sizing at that location
        ▼
BeamShaftDesignResult (both source and derived results)
```

The current modules are:

- `mechdac.core.units`: `QuantityValue`, one Pint registry, and common Pydantic configuration (`extra="forbid"`, assignment validation).
- `mechdac.core.schema`: physical beam, support, point-load, distributed-load, applied-moment, material, design requirement, and shaft-load inputs. The composed beam/shaft input makes torque-at-selected-section explicit. It validates units and physical bounds; it contains no engineering equations.
- `mechdac.solvers.beam`: equilibrium reactions plus piecewise shear and bending moment calculations. It owns the sign conventions used by this solver.
- `mechdac.solvers.shafts`: generic static solid-round-shaft sizing from bending moment, torque, yield strength, and requested factor of safety. Its composition entry point solves the beam, selects its reported maximum absolute moment, and passes that plus the explicitly supplied section torque to the shaft solver. It does not claim a standard-specific rating.
- `mechdac.core.results`: Pydantic output models with beam reactions, diagram data, shaft diameter and stresses, both nested results for the composed workflow, calculation traces, assumptions, warnings, and solver metadata.
- `mechdac.cli`: argparse-based `mechdac beam solve`, `mechdac beam plot`, `mechdac shaft size`, and `mechdac shaft size-from-beam` commands. It reads JSON with the standard library and YAML with `yaml.safe_load`, validates through the relevant schema, then calls the solver API. Text is the default output; `--format json` serializes the complete result. Beam plots save PNG/SVG output.
- `mechdac.plotting.beam`: optional Matplotlib adapter that evaluates the existing result segment polynomials and uses event-side values to draw force and couple jumps. It does not recalculate statics.
- `docs/sources/bhandari`: page-aware maps for the supplied Chapters 4 and 9 and a ledger that records equation references, validation evidence, method differences, and future capability boundaries. This is documentation/test provenance; no solver is coupled to a textbook.

Packaging uses a `src/` layout. Pydantic v2 and Pint are runtime dependencies; pytest is a development extra; Matplotlib is isolated in the optional `plotting` extra. The supported Python version is 3.12 or later.

## Current modeling and calculation boundary

Schemas hold physical values with units and explicit directions. At the solver boundary, lengths convert to metres, forces to newtons, line loads to newtons per metre, and couples to newton-metres. The deterministic solver then applies static equilibrium and integrates the piecewise shear/moment behavior. Result models hold canonical units and plotting-relevant event/segment information; the optional renderer samples those polynomials and preserves discontinuities without changing the calculation result.

The beam model is determinate by construction: exactly two distinct supports, one pin and one roller, with only vertical forces and couples. Pin/roller behavior is represented at the vertical-beam level; axial support reactions are out of scope. The standalone shaft model accepts a supplied single-section bending moment and torque. The composed workflow uses the beam's maximum absolute bending moment and its reported position, then applies the torque supplied for that section. It models one bending plane and one selected section; tied moment maxima or varying torque elsewhere are not examined. Both shaft paths assume a solid circular section and a static von Mises yield criterion. The equations are verified against the supplied generic stress and distortion-energy relationships in Bhandari Chapter 4. Bhandari Chapter 9 §9.2 gives the same nominal stress formulas but sizes ductile shafts using maximum shear; that criterion difference is documented in the source ledger. No standard-specific or textbook-specific rating is implied.

## Intended growth path

The file-input and CLI layer sits over the schemas and solvers. Parsing and command behavior stay outside the calculation equations. Structured results serialize for downstream use. The beam trace records equilibrium equations and numeric substitutions; the shaft trace records its sizing and stress equations. The composed result preserves each complete result and the selected section location. Future solvers should retain this result/trace boundary.

As new engineering methods are introduced, preserve these boundaries:

```text
physical problem schemas → units → engineering solver(s)
→ structured results/checks → CLI/reporting → eventually CAD
```

Standards-specific equations belong in explicitly named solver methods, not physical input schemas. The beam and shaft workflows have CLI input and output, including optional SFD/BMD plotting. There is no gear/bearing calculation, calculation report generator, CAD layer, or general-purpose verification framework yet; add these only with a concrete, testable use. Textbook traceability for this mission lives in the source maps, ledger, and source-derived regression test rather than in solver runtime metadata.
