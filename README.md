# MechDAC

MechDAC is an open-source, unit-aware mechanical engineering calculation library. Its first runnable workflows solve determinate 1D beam statics and perform a generic static yield screen for a solid round shaft under bending and torsion.

## Install

Requires Python 3.12 or later.

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install '.[dev]'
```

## Solve the example beam

```bash
mechdac beam solve examples/simple_beam.yaml
```

The command prints support reactions, maximum absolute shear and bending moment, the reaction calculation trace, assumptions, and warnings. JSON input is also supported. To print the complete structured result as JSON:

```bash
mechdac beam solve examples/simple_beam.yaml --format json
```

Input files may use `.yaml`, `.yml`, or `.json`. Quantities are expressed as mappings with a numeric `value` and Pint `unit`, such as `{value: 2, unit: m}`. See [examples/simple_beam.yaml](examples/simple_beam.yaml) for a complete input.

## Static solid-shaft screen

```bash
mechdac shaft size examples/shaft_basic.yaml
mechdac shaft size examples/shaft_basic.yaml --format json
mechdac shaft size-from-beam examples/shaft_from_beam.yaml
```

This generic calculation sizes a solid circular section for a requested static yield factor of safety using nominal elastic bending and torsion stresses and the von Mises criterion. It is not an ASME rating. See [examples/shaft_basic.yaml](examples/shaft_basic.yaml) for the input structure.

The `size-from-beam` workflow takes the beam solver's maximum absolute bending moment and combines it with the supplied torque at that reported section. The beam model represents one bending plane; the input and output preserve both calculations and state this assumption. See [examples/shaft_from_beam.yaml](examples/shaft_from_beam.yaml).

## Current model and limits

The beam solver accepts exactly one pin and one roller at distinct beam positions, vertical point forces, uniform distributed forces over intervals, and applied couples. Force directions are explicitly `up` or `down`; moment directions are `counterclockwise` or `clockwise`. The output uses SI units.

The beam model is planar and static. The standalone shaft screen accepts bending moment, torque, yield strength, and a requested factor of safety at one section. The composed workflow uses the maximum absolute beam moment and requires torque at that same section. It does not evaluate multiple bending planes, tied critical sections, varying torque, stress concentrations, fatigue, axial stress, deflection, standard-specific ratings, gears, or bearings. Solver assumptions are documented in [docs/DESIGN_NOTES.md](docs/DESIGN_NOTES.md).

## Tests

```bash
python -m pytest -q
```
