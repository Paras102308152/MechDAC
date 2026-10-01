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

The current engine solves a limited 1D vertical beam statics problem. Inputs define beam length, one pin, one roller, point forces, uniform distributed forces, and applied moments. The solver calculates reactions and piecewise shear/bending-moment behavior, including critical absolute values and explicit sign conventions. See [DESIGN_NOTES.md](DESIGN_NOTES.md) for assumptions and limitations.

There is not yet a user-facing CLI, YAML/JSON file workflow, plot, calculation trace, report generator, or CAD workflow. The current solver API is usable from Python and covered by analytical tests.

## MVP direction

The next useful vertical slice is a user-runnable beam workflow: read a small documented YAML/JSON input, validate it, solve it, and display understandable engineering results with a structured result available for downstream use. Once that is reliable, add transparent calculation traces and then decide whether shaft sizing is the highest-value next calculation.
