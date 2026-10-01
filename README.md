# MechDAC

MechDAC is an open-source, unit-aware mechanical engineering calculation library. Its first runnable workflow solves simple, statically determinate 1D beam statics problems and returns reactions, shear and bending-moment data.

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

The command prints support reactions, maximum absolute shear and bending moment, assumptions, and warnings. JSON input is also supported. To print the complete structured result as JSON:

```bash
mechdac beam solve examples/simple_beam.yaml --format json
```

Input files may use `.yaml`, `.yml`, or `.json`. Quantities are expressed as mappings with a numeric `value` and Pint `unit`, such as `{value: 2, unit: m}`. See [examples/simple_beam.yaml](examples/simple_beam.yaml) for a complete input.

## Current model and limits

The solver accepts exactly one pin and one roller at distinct beam positions, vertical point forces, uniform distributed forces over intervals, and applied couples. Force directions are explicitly `up` or `down`; moment directions are `counterclockwise` or `clockwise`. The output uses SI units.

The model is planar and static. It does not calculate axial reactions, deflection, stress, fatigue, shaft sizing, gear/bearing behavior, or any standard-specific rating. The solver's assumptions and result fields are documented in [docs/DESIGN_NOTES.md](docs/DESIGN_NOTES.md).

## Tests

```bash
python -m pytest -q
```
