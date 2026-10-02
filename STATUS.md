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
- The existing solid-shaft equations have been source-checked against supplied Bhandari Ch. 4 §§4.2, 4.5–4.6, 4.13, and 4.17–4.18. Source-validation tests independently compute plane-stress principal values and distortion-energy stress, and reproduce Example 4.13's documented Tresca/von-Mises criterion difference.
- The shaft result assumptions now explicitly state that the material is ductile, homogeneous, isotropic, and linear-elastic up to yield; those properties cannot be inferred from a material name.
- Bhandari Ch. 9 §9.2 nominal bending/torsion stresses agree with MechDAC; its shaft-sizing examples use maximum shear (Tresca), while MechDAC deliberately uses distortion energy (von Mises). This difference is documented; MechDAC is not presented as a Bhandari or ASME design.
- Page-aware maps and a source ledger were added for the supplied Bhandari Chapters 4 and 9. Example 4.13 and the final strength-sizing step of Example 9.1 were independently reproduced and recorded with their method boundaries.
- `mechdac shaft size INPUT` and `mechdac shaft size-from-beam INPUT` accept YAML/YML/JSON and emit text or structured JSON. `examples/shaft_basic.yaml` and `examples/shaft_from_beam.yaml` are generic runnable inputs.
- Tests cover unit conversion, invalid physical values, unknown fields, serialization round-trips, analytical beam and shaft cases, combined beam/shaft results, and CLI input/output and error paths. The formerly empty unit/schema tests and shaft example are populated.

## In progress / deferred

- Plotting is deferred. Beam JSON already includes exact piecewise diagram data; no plotting dependency is currently needed by the calculation workflows.
- Broader Phase 1 models (gear pair, bearing load, load case, and reusable check/solver result models) remain unimplemented until a concrete workflow requires them.

## Next

- Evaluate an SFD/BMD plotting path using the existing exact diagram results. Keep plotting separate from calculation code and add a dependency only if the implementation needs it.
- Keep future source-derived shaft work separate: Ch. 9 torsional rigidity, ASME design, hollow shafts, keys, splines, couplings, lateral deflection, and critical speed are mapped but not implemented.

## Known limitations

- The beam solver is planar and static, with one pin and one roller, point forces, uniform distributed loads, and applied couples. It does not calculate axial effects, deflection, or stresses.
- The shaft solver assumes a solid circular section, one critical section, static bending and torsion only, nominal stresses, and a generic von Mises yield screen. It omits stress concentrations, fatigue, axial load, deflection, and standard diameter selection.
- Finite values outside the supported floating-point calculation range are rejected; the model does not clamp or approximate extreme magnitudes.
- The composed workflow uses one bending plane and one beam-reported maximum-moment location. Torque must be supplied for that location. Tied maxima, torque elsewhere, and multiple bending planes are not evaluated.
- There is no SFD/BMD plot renderer or report generator. The beam result reports one critical absolute-moment location; tied maxima may occur at multiple locations.

## Last verification

- Baseline before this mission, 2026-10-02: `.venv/bin/python -m pytest -q` — **45 passed in 0.42s**.
- Final environment: Python 3.12.14, Pydantic 2.13.5, Pint 0.26.1, PyYAML 6.0.3, pytest 9.1.1.
- Package refresh after changing the solver assumptions: `.venv/bin/python -m pip install '.[dev]'` — wheel built and local package reinstalled successfully.
- Focused source validation: `.venv/bin/python -m pytest -q tests/test_source_validation.py` — **2 passed in 0.32s**.
- Full suite: `.venv/bin/python -m pytest -q` — **47 passed in 0.42s**.
- Import check: `mechdac`, `solve_beam`, `solve_shaft`, and `solve_shaft_from_beam` — passed.
- CLI checks: generic beam text example, standalone shaft JSON example, and composed beam-to-shaft JSON example — passed.
- Independent source arithmetic: Ch. 4 Example 4.13 reproduced at 31.06 mm by maximum shear; the same loads give 29.93 mm through the actual MechDAC von Mises solver. Ch. 9 Example 9.1 final sizing step reproduced at 45.474 mm (printed 45.47 mm) using its maximum-shear equation.
