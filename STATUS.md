# Current Status

## Current phase

Phase 5 — the initial static beam/shaft workflow is complete for one vertical bending plane and one selected shaft section. Standalone shaft loading is supported, and the composed route uses the beam's reported maximum absolute bending moment with torque supplied at that same section.

## Completed

- Git repository is on `main`, with `origin` set to `https://github.com/Paras102308152/MechDAC`.
- Python package metadata targets Python 3.12+ and declares Pydantic v2 and Pint; pytest is a development dependency.
- `QuantityValue` stores finite scalars plus Pint-compatible unit strings. Pydantic domain models reject unknown fields and validate assignment.
- Beam schemas support one pin and one roller, point forces, uniform distributed forces, and applied couples, with dimensional and position validation.
- The beam solver calculates determinate vertical reactions, shear behavior, sagging-positive bending moments, exact diagram segments, extrema, and an auditable equilibrium trace.
- `mechdac beam solve INPUT` accepts YAML/YML/JSON and emits text or structured JSON. `examples/simple_beam.yaml` is generic and runnable.
- `MaterialSpec`, `DesignRequirementSpec`, `ShaftLoadingSpec`, and `BeamShaftLoadingSpec` validate material yield strength, positive finite target factor of safety, moment units, and nested beam data.
- `solve_shaft` sizes a solid circular section for static bending and torsion using nominal elastic stresses and the generic von Mises yield criterion. Its structured result includes diameter, stresses, actual/required factors of safety, assumptions, solver metadata, and five trace entries. It is not an ASME rating.
- `solve_shaft_from_beam` uses the beam's maximum absolute bending moment and reported position, combines it with torque explicitly supplied at that section, and preserves both full results.
- `mechdac shaft size INPUT` and `mechdac shaft size-from-beam INPUT` accept YAML/YML/JSON and emit text or structured JSON. `examples/shaft_basic.yaml` and `examples/shaft_from_beam.yaml` are generic runnable inputs.
- Tests cover unit conversion, invalid physical values, unknown fields, serialization round-trips, analytical beam and shaft cases, combined beam/shaft results, and CLI input/output and error paths. The formerly empty unit/schema tests and shaft example are populated.

## In progress / deferred

- Plotting is deferred. Beam JSON already includes exact piecewise diagram data; no plotting dependency is currently needed by the calculation workflows.
- Broader Phase 1 models (gear pair, bearing load, load case, and reusable check/solver result models) remain unimplemented until a concrete workflow requires them.

## Next

- Evaluate an SFD/BMD plotting path using the existing exact diagram results. Keep plotting separate from calculation code and add a dependency only if the implementation needs it.

## Known limitations

- The beam solver is planar and static, with one pin and one roller, point forces, uniform distributed loads, and applied couples. It does not calculate axial effects, deflection, or stresses.
- The shaft solver assumes a solid circular section, one critical section, static bending and torsion only, nominal stresses, and a generic von Mises yield screen. It omits stress concentrations, fatigue, axial load, deflection, and standard diameter selection.
- Finite values outside the supported floating-point calculation range are rejected; the model does not clamp or approximate extreme magnitudes.
- The composed workflow uses one bending plane and one beam-reported maximum-moment location. Torque must be supplied for that location. Tied maxima, torque elsewhere, and multiple bending planes are not evaluated.
- There is no SFD/BMD plot renderer or report generator. The beam result reports one critical absolute-moment location; tied maxima may occur at multiple locations.

## Last verification

- Date: 2026-10-01. Environment: Python 3.12.14, Pydantic 2.13.5, Pint 0.26.1, PyYAML 6.0.3, pytest 9.1.1.
- Full suite: `.venv/bin/python -m pytest -q` — **45 passed in 0.40s** after reinstalling the built package. Source-tree run also passed: 45 passed in 0.42s.
- Package: `.venv/bin/python -m pip install '.[dev]'` — wheel built and installed successfully.
- Import: `import mechdac`; imports of `solve_beam`, `solve_shaft`, and `solve_shaft_from_beam` — passed.
- Beam, standalone shaft, and beam-to-shaft CLI examples — passed in text mode.
- Beam and beam-to-shaft CLI JSON outputs — parsed successfully; composed output identified the 2 m section and retained the nested shaft result.
- Extreme finite shaft load — CLI returned exit code 2 with an explanatory range error and no traceback.
- `git diff HEAD --check` — passed on the final follow-up changes.
