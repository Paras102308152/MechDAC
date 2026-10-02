"""Command-line interface for deterministic MechDAC calculations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

import yaml
from pydantic import ValidationError

from mechdac.core.results import BeamAnalysisResult, BeamShaftDesignResult, ShaftDesignResult
from mechdac.core.schema import BeamShaftLoadingSpec, BeamSpec, ShaftLoadingSpec
from mechdac.solvers.beam import solve_beam
from mechdac.solvers.shafts import solve_shaft, solve_shaft_from_beam


class InputFileError(Exception):
    """An input file could not be read, parsed, or validated."""


def _load_document(path: Path) -> dict[str, object]:
    suffix = path.suffix.lower()
    if suffix not in {".yaml", ".yml", ".json"}:
        raise InputFileError("Input extension must be .yaml, .yml, or .json")

    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise InputFileError(f"Input file not found: {path}") from exc
    except OSError as exc:
        raise InputFileError(f"Could not read input file {path}: {exc.strerror or exc}") from exc

    try:
        document = json.loads(text) if suffix == ".json" else yaml.safe_load(text)
    except json.JSONDecodeError as exc:
        raise InputFileError(
            f"Could not parse JSON input at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    except yaml.YAMLError as exc:
        raise InputFileError(f"Could not parse YAML input: {exc}") from exc

    if not isinstance(document, dict):
        raise InputFileError("Input document root must be a mapping/object")
    return document


def _load_beam(path: Path) -> BeamSpec:
    try:
        return BeamSpec.model_validate(_load_document(path))
    except ValidationError as exc:
        raise InputFileError(f"Invalid beam input:\n{exc}") from exc


def _load_shaft(path: Path) -> ShaftLoadingSpec:
    try:
        return ShaftLoadingSpec.model_validate(_load_document(path))
    except ValidationError as exc:
        raise InputFileError(f"Invalid shaft input:\n{exc}") from exc


def _load_beam_shaft(path: Path) -> BeamShaftLoadingSpec:
    try:
        return BeamShaftLoadingSpec.model_validate(_load_document(path))
    except ValidationError as exc:
        raise InputFileError(f"Invalid beam-to-shaft input:\n{exc}") from exc


def _format_text(result: BeamAnalysisResult) -> str:
    lines = [
        "Beam statics result",
        f"Solver: {result.solver_name} {result.solver_version}",
        "Sign convention: upward is positive for forces/reactions; counterclockwise is positive for applied moments; sagging is positive for bending moments.",
        "",
        "Support reactions:",
    ]
    for reaction in result.support_reactions:
        position = reaction.position.to("m")
        force = reaction.force.to("N")
        lines.append(f"  {reaction.kind} at {position:g} m: {force:+g} N")

    lines.extend(
        (
            "",
            "Extrema:",
            f"  Maximum |V|: {result.maximum_absolute_shear.to('N'):g} N",
            "  Maximum |M|: "
            f"{result.maximum_absolute_bending_moment.to('N*m'):g} N·m at "
            f"{result.maximum_bending_moment_position.to('m'):g} m",
        )
    )
    lines.append("Calculation trace:")
    for step in result.calculation_trace:
        lines.extend(
            (
                f"  {step.name}:",
                f"    {step.equation}",
                f"    {step.substitution}",
            )
        )
    lines.append("")
    lines.append("Assumptions:")
    lines.extend(f"  - {assumption}" for assumption in result.assumptions)
    lines.append("Warnings:")
    if result.warnings:
        lines.extend(f"  - {warning}" for warning in result.warnings)
    else:
        lines.append("  - none")
    return "\n".join(lines)


def _format_shaft_text(result: ShaftDesignResult) -> str:
    lines = [
        "Static solid-round shaft result",
        f"Solver: {result.solver_name} {result.solver_version}",
        f"Minimum required diameter: {result.minimum_required_diameter.to('mm'):g} mm",
        f"Nominal bending stress: {result.bending_stress.to('MPa'):g} MPa",
        f"Nominal torsional shear stress: {result.torsional_shear_stress.to('MPa'):g} MPa",
        f"Equivalent von Mises stress: {result.equivalent_stress.to('MPa'):g} MPa",
        f"Yield strength: {result.yield_strength.to('MPa'):g} MPa",
        f"Yield factor of safety: {result.factor_of_safety:g} "
        f"(minimum requested: {result.minimum_factor_of_safety:g})",
        "Calculation trace:",
    ]
    for step in result.calculation_trace:
        lines.extend((f"  {step.name}:", f"    {step.equation}", f"    {step.substitution}"))
    lines.append("")
    lines.append("Assumptions:")
    lines.extend(f"  - {assumption}" for assumption in result.assumptions)
    lines.append("Warnings:")
    if result.warnings:
        lines.extend(f"  - {warning}" for warning in result.warnings)
    else:
        lines.append("  - none")
    return "\n".join(lines)


def _format_beam_shaft_text(result: BeamShaftDesignResult) -> str:
    lines = [
        "Beam-to-shaft static sizing result",
        f"Critical section: {result.critical_section_position.to('m'):g} m",
        f"Bending moment used: {result.critical_bending_moment.to('N*m'):g} N·m",
        "",
        _format_text(result.beam_analysis),
        "",
        _format_shaft_text(result.shaft_design),
        "",
        "Composition assumptions:",
    ]
    lines.extend(f"  - {assumption}" for assumption in result.assumptions)
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mechdac", description="Mechanical design calculations")
    commands = parser.add_subparsers(dest="command", required=True)
    beam_parser = commands.add_parser("beam", help="beam statics calculations")
    beam_commands = beam_parser.add_subparsers(dest="beam_command", required=True)
    solve_parser = beam_commands.add_parser("solve", help="solve a statically determinate beam")
    solve_parser.add_argument("input", type=Path, help="beam input file (.yaml, .yml, or .json)")
    solve_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format (default: text)",
    )
    plot_parser = beam_commands.add_parser(
        "plot", help="plot shear-force and bending-moment diagrams"
    )
    plot_parser.add_argument("input", type=Path, help="beam input file (.yaml, .yml, or .json)")
    plot_parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="output image path (.png or .svg)",
    )
    shaft_parser = commands.add_parser("shaft", help="shaft design calculations")
    shaft_commands = shaft_parser.add_subparsers(dest="shaft_command", required=True)
    size_parser = shaft_commands.add_parser(
        "size", help="size a solid round shaft for static bending and torsion"
    )
    size_parser.add_argument("input", type=Path, help="shaft input file (.yaml, .yml, or .json)")
    size_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format (default: text)",
    )
    from_beam_parser = shaft_commands.add_parser(
        "size-from-beam", help="size a shaft using a beam result's maximum bending moment"
    )
    from_beam_parser.add_argument(
        "input", type=Path, help="combined beam/shaft input file (.yaml, .yml, or .json)"
    )
    from_beam_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format (default: text)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the MechDAC CLI and return a process exit code."""

    args = _build_parser().parse_args(argv)
    try:
        if args.command == "beam":
            beam = _load_beam(args.input)
            if args.beam_command == "solve":
                result = solve_beam(beam)
            else:
                output_format = args.output.suffix.lower()
                if output_format not in {".png", ".svg"}:
                    print(
                        "mechdac: error: Plot output extension must be .png or .svg",
                        file=sys.stderr,
                    )
                    return 2
                analysis = solve_beam(beam)
                try:
                    from mechdac.plotting.beam import plot_beam_diagrams
                except ModuleNotFoundError as exc:
                    if exc.name == "matplotlib" or (
                        exc.name is not None and exc.name.startswith("matplotlib.")
                    ):
                        print(
                            "mechdac: error: Beam plotting requires the optional dependency; "
                            "install it with `pip install 'mechdac[plotting]'`",
                            file=sys.stderr,
                        )
                        return 2
                    raise
                figure = plot_beam_diagrams(analysis)
                try:
                    figure.savefig(
                        args.output,
                        format=output_format[1:],
                        metadata={"Date": None} if output_format == ".svg" else None,
                    )
                except OSError as exc:
                    print(
                        f"mechdac: error: Could not save beam diagrams to {args.output}: {exc}",
                        file=sys.stderr,
                    )
                    return 2
                print(f"Saved beam diagrams to {args.output}")
                return 0
        elif args.shaft_command == "size":
            shaft = _load_shaft(args.input)
            try:
                result = solve_shaft(shaft)
            except ValueError as exc:
                print(f"mechdac: error: invalid shaft sizing request: {exc}", file=sys.stderr)
                return 2
        else:
            beam_shaft = _load_beam_shaft(args.input)
            try:
                result = solve_shaft_from_beam(beam_shaft)
            except ValueError as exc:
                print(f"mechdac: error: invalid beam-to-shaft sizing request: {exc}", file=sys.stderr)
                return 2
    except InputFileError as exc:
        print(f"mechdac: error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(result.model_dump_json(indent=2))
    elif isinstance(result, BeamShaftDesignResult):
        print(_format_beam_shaft_text(result))
    elif isinstance(result, ShaftDesignResult):
        print(_format_shaft_text(result))
    else:
        print(_format_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
