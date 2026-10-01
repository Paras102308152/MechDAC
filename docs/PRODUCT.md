# Product

## What MechDAC is

MechDAC is an open-source Mechanical Design-as-Code toolkit for making mechanical engineering calculations reproducible, inspectable, and programmable. It should behave like engineering software: explicit inputs, units, assumptions, deterministic methods, and structured outputs.

The long-term user flow is:

```text
structured physical inputs
  → validation and units
  → deterministic engineering calculations
  → checks and transparent results
  → plots and documentation
  → eventually parametric CAD
```

## Who it serves

- Second- and third-year mechanical engineering students
- Students completing machine-design assignments and projects
- Early-career mechanical engineers
- Engineers who want reproducible calculation workflows

## Product principles

- Engineering correctness before feature count
- No LLM decisions in numerical engineering results
- Visible equations, assumptions, intermediate values, and provenance as the product matures
- Unit safety and reproducible deterministic behavior
- Analytical verification for engineering equations
- Physical schemas kept separate from solver equations and standards
- Small complete workflows rather than an incomplete catalog of components
- No invented assumptions, arbitrary coefficients, or benchmark project inputs embedded in the software

## Current capability

The current engine solves a limited 1D vertical beam statics problem and a separate static solid-round-shaft sizing problem. YAML or JSON inputs define the beam geometry and loads, one shaft section's bending moment and torque, or a composition of a beam plus torque at its maximum-moment section. The CLI validates the input, runs the appropriate deterministic solver, and displays results and calculation traces as readable text or structured JSON. The beam solver calculates piecewise shear/bending-moment behavior; the shaft solver applies a generic von Mises static yield criterion to nominal bending and torsion stresses. See [DESIGN_NOTES.md](DESIGN_NOTES.md) for assumptions and limitations.

There is not yet a plot, report generator, or CAD workflow. Both solver APIs are usable from Python and covered by analytical and CLI tests.

## MVP direction

The first user-runnable beam and shaft workflows are in place, including a limited one-plane beam-to-shaft composition. Evaluate plotting of the existing exact SFD/BMD result data as the next user-facing extension; keep calculation changes separate from rendering.
