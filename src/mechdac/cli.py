"""Command-line interface for deterministic MechDAC calculations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

import yaml
from pydantic import ValidationError

from mechdac.core.results import BeamAnalysisResult
from mechdac.core.schema import BeamSpec
from mechdac.solvers.beam import solve_beam


class InputFileError(Exception):
    """An input file could not be read, parsed, or validated."""


def _load_beam(path: Path) -> BeamSpec:
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
    try:
        return BeamSpec.model_validate(document)
    except ValidationError as exc:
        raise InputFileError(f"Invalid beam input:\n{exc}") from exc


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
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the MechDAC CLI and return a process exit code."""

    args = _build_parser().parse_args(argv)
    try:
        beam = _load_beam(args.input)
    except InputFileError as exc:
        print(f"mechdac: error: {exc}", file=sys.stderr)
        return 2

    result = solve_beam(beam)
    if args.format == "json":
        print(result.model_dump_json(indent=2))
    else:
        print(_format_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
