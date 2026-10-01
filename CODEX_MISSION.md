# MechDAC Mission

## Project

MechDAC is an open-source, unit-safe Mechanical Design-as-Code Python toolkit. Its purpose is to make mechanical calculations reproducible, inspectable, and programmable for mechanical engineering students and early-career engineers.

The long-term product flow is:

```text
physical inputs → validation → deterministic engineering solvers
→ structured results and verification → transparent traces and reports
→ eventually parametric CAD
```

The current repository is the existing local project at `/Users/parasbadhran/Desktop/MechDAC`, connected to `https://github.com/Paras102308152/MechDAC`. Work in this folder; do not clone another copy.

## Mission and priorities

1. Engineering correctness comes before feature breadth.
2. Numerical results come from deterministic solvers, never an LLM.
3. Keep physical problem schemas separate from equations and standards.
4. Carry units with physical values and make assumptions visible.
5. Verify engineering results against analytical cases.
6. Prefer one small, complete workflow to several incomplete subsystems.
7. Do not add infrastructure, dependencies, or abstractions without a concrete need.
8. Do not encode benchmark assignment/report data into application behavior.

## Current scope

The repository contains a deterministic, planar 1D beam statics solver for vertical point forces, uniform distributed forces, and applied couples on one pin and one roller. It returns reactions, a numeric equilibrium trace, shear and moment event values, polynomial diagram segments, extrema, assumptions, and solver metadata. A CLI reads YAML or JSON inputs and displays text or structured JSON results. A separate solver sizes a solid circular shaft section under static bending and torsion using nominal stresses and a generic von Mises yield criterion. A composed workflow can use the beam's maximum absolute moment with an explicit torque at that section. These are not a full shaft designer or a standard-specific rating.

The beam-to-shaft mapping is verified for the current one-plane static model. Next evaluate a plotting path for the already structured SFD/BMD output. Do not add fatigue, stress concentrations, CAD, optimization, or standards-specific ratings without a separate, verified scope. See [STATUS.md](STATUS.md), [ROADMAP.md](ROADMAP.md), and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Working rules for future development

- Inspect the current repository and Git state before editing.
- Make the smallest complete change consistent with the product and architecture.
- For new solver behavior, write analytical tests first, observe them fail for the intended reason, then implement and rerun the complete suite.
- After meaningful changes, inspect the diff, run the full test suite and package/import checks, update `STATUS.md`, and record lasting architecture choices in `DECISIONS.md`.
- Keep `ROADMAP.md` aligned with implemented behavior; mark work complete only when verified.
- Keep engineering assumptions and solver limitations explicit in `docs/DESIGN_NOTES.md` or the relevant solver documentation.
- Use focused commits at meaningful milestones. Never force-push or rewrite shared history. Do not push unless the user asks.
- Do not commit credentials, virtual environments, build products, or machine-specific files.
- Do not add gear/bearing equations, fatigue methods, CAD, optimization, reporting, web services, databases, GUI frameworks, or AI APIs until a later task calls for them.

## Useful local commands

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install '.[dev]'
python -m pytest -q
python -c 'from mechdac.solvers.beam import solve_beam; print("beam solver import OK")'
mechdac beam solve examples/simple_beam.yaml
mechdac beam solve examples/simple_beam.yaml --format json
mechdac shaft size examples/shaft_basic.yaml
mechdac shaft size examples/shaft_basic.yaml --format json
mechdac shaft size-from-beam examples/shaft_from_beam.yaml
```

For source-tree development after changing package code, reinstall with `python -m pip install '.[dev]'` before exercising the installed CLI entry point.
