import json
import sys

import pytest

from mechdac.cli import main


BEAM_INPUT = {
    "length": {"value": 4, "unit": "m"},
    "supports": [
        {"kind": "pin", "position": {"value": 0, "unit": "m"}},
        {"kind": "roller", "position": {"value": 4, "unit": "m"}},
    ],
    "point_loads": [
        {
            "position": {"value": 2, "unit": "m"},
            "magnitude": {"value": 2000, "unit": "N"},
            "direction": "down",
        }
    ],
}

SHAFT_INPUT = {
    "bending_moment": {"value": 100, "unit": "N*m"},
    "torque": {"value": 50, "unit": "N*m"},
    "material": {
        "name": "test material",
        "yield_strength": {"value": 250, "unit": "MPa"},
    },
    "design_requirement": {"minimum_factor_of_safety": 2},
}


def test_cli_solves_yaml_and_prints_engineering_summary(tmp_path, capsys) -> None:
    input_path = tmp_path / "beam.yaml"
    input_path.write_text(
        """length: {value: 4, unit: m}
supports:
  - kind: pin
    position: {value: 0, unit: m}
  - kind: roller
    position: {value: 4, unit: m}
point_loads:
  - position: {value: 2, unit: m}
    magnitude: {value: 2000, unit: N}
    direction: down
""",
        encoding="utf-8",
    )

    exit_code = main(["beam", "solve", str(input_path)])

    output = capsys.readouterr()
    assert exit_code == 0
    assert "Beam statics result" in output.out
    assert "pin at 0 m: +1000 N" in output.out
    assert "roller at 4 m: +1000 N" in output.out
    assert "Maximum |V|: 1000 N" in output.out
    assert "Maximum |M|: 2000 N·m at 2 m" in output.out
    assert "upward is positive" in output.out
    assert output.out.count("Assumptions:") == 1
    assert "Calculation trace:" in output.out
    assert "R_B = -M_A / (x_B - x_A)" in output.out
    assert "F_ext = (-2000 N) = -2000 N" in output.out
    assert output.err == ""


def test_cli_accepts_json_and_emits_structured_result(tmp_path, capsys) -> None:
    input_path = tmp_path / "beam.json"
    input_path.write_text(json.dumps(BEAM_INPUT), encoding="utf-8")

    exit_code = main(["beam", "solve", str(input_path), "--format", "json"])

    output = capsys.readouterr()
    result = json.loads(output.out)
    assert exit_code == 0
    assert result["support_reactions"][0]["force"] == {"value": 1000.0, "unit": "N"}
    assert result["maximum_absolute_bending_moment"] == {"value": 2000.0, "unit": "N*m"}
    assert result["maximum_bending_moment_position"] == {"value": 2.0, "unit": "m"}
    assert len(result["calculation_trace"]) == 4
    assert output.err == ""


def test_cli_reports_validation_errors_without_a_traceback(tmp_path, capsys) -> None:
    invalid_input = {**BEAM_INPUT, "unexpected": "field"}
    input_path = tmp_path / "invalid.json"
    input_path.write_text(json.dumps(invalid_input), encoding="utf-8")

    exit_code = main(["beam", "solve", str(input_path)])

    output = capsys.readouterr()
    assert exit_code == 2
    assert "Invalid beam input" in output.err
    assert "Extra inputs are not permitted" in output.err
    assert "Traceback" not in output.err


def test_cli_reports_malformed_yaml(tmp_path, capsys) -> None:
    input_path = tmp_path / "broken.yaml"
    input_path.write_text("length: [", encoding="utf-8")

    exit_code = main(["beam", "solve", str(input_path)])

    output = capsys.readouterr()
    assert exit_code == 2
    assert "Could not parse YAML input" in output.err


def test_cli_reports_missing_files_and_unknown_formats(tmp_path, capsys) -> None:
    missing_path = tmp_path / "missing.yaml"

    missing_exit_code = main(["beam", "solve", str(missing_path)])
    missing_output = capsys.readouterr()
    unknown_exit_code = main(["beam", "solve", str(tmp_path / "beam.txt")])
    unknown_output = capsys.readouterr()

    assert missing_exit_code == 2
    assert "Input file not found" in missing_output.err
    assert unknown_exit_code == 2
    assert "Input extension must be .yaml, .yml, or .json" in unknown_output.err


@pytest.mark.parametrize("payload", [None, [], "beam"])
def test_cli_rejects_non_mapping_documents(tmp_path, capsys, payload) -> None:
    input_path = tmp_path / "beam.json"
    input_path.write_text(json.dumps(payload), encoding="utf-8")

    exit_code = main(["beam", "solve", str(input_path)])

    output = capsys.readouterr()
    assert exit_code == 2
    assert "document root must be a mapping" in output.err


def test_cli_sizes_shaft_from_yaml_and_prints_assumptions(tmp_path, capsys) -> None:
    input_path = tmp_path / "shaft.yaml"
    input_path.write_text(
        """bending_moment: {value: 100, unit: N*m}
torque: {value: 50, unit: N*m}
material:
  name: test material
  yield_strength: {value: 250, unit: MPa}
design_requirement:
  minimum_factor_of_safety: 2
""",
        encoding="utf-8",
    )

    exit_code = main(["shaft", "size", str(input_path)])

    output = capsys.readouterr()
    assert exit_code == 0
    assert "Static solid-round shaft result" in output.out
    assert "Minimum required diameter:" in output.out
    assert "Equivalent von Mises stress:" in output.out
    assert "Yield factor of safety:" in output.out
    assert "this is not an ASME rating" in output.out
    assert "Calculation trace:" in output.out
    assert output.err == ""


def test_cli_sizes_shaft_from_json_and_emits_structured_result(tmp_path, capsys) -> None:
    input_path = tmp_path / "shaft.json"
    input_path.write_text(json.dumps(SHAFT_INPUT), encoding="utf-8")

    exit_code = main(["shaft", "size", str(input_path), "--format", "json"])

    output = capsys.readouterr()
    result = json.loads(output.out)
    assert exit_code == 0
    assert result["minimum_required_diameter"]["unit"] == "m"
    assert result["minimum_required_diameter"]["value"] == pytest.approx(0.020707879728, rel=1e-8)
    assert result["equivalent_stress"] == {"value": pytest.approx(125e6), "unit": "Pa"}
    assert result["factor_of_safety"] == pytest.approx(2)
    assert len(result["calculation_trace"]) == 5
    assert "not an ASME rating" in " ".join(result["assumptions"])
    assert output.err == ""


def test_cli_reports_shaft_schema_errors_without_traceback(tmp_path, capsys) -> None:
    invalid_input = {**SHAFT_INPUT, "unexpected": "field"}
    input_path = tmp_path / "invalid_shaft.json"
    input_path.write_text(json.dumps(invalid_input), encoding="utf-8")

    exit_code = main(["shaft", "size", str(input_path)])

    output = capsys.readouterr()
    assert exit_code == 2
    assert "Invalid shaft input" in output.err
    assert "Extra inputs are not permitted" in output.err
    assert "Traceback" not in output.err


def test_cli_reports_degenerate_shaft_sizing_request(tmp_path, capsys) -> None:
    zero_load_input = {
        **SHAFT_INPUT,
        "bending_moment": {"value": 0, "unit": "N*m"},
        "torque": {"value": 0, "unit": "N*m"},
    }
    input_path = tmp_path / "zero_shaft.json"
    input_path.write_text(json.dumps(zero_load_input), encoding="utf-8")

    exit_code = main(["shaft", "size", str(input_path)])

    output = capsys.readouterr()
    assert exit_code == 2
    assert "invalid shaft sizing request" in output.err
    assert "requires a nonzero bending moment or torque" in output.err
    assert "Traceback" not in output.err


def test_cli_sizes_shaft_from_beam_input_as_text_and_structured_json(tmp_path, capsys) -> None:
    input_path = tmp_path / "beam_shaft.json"
    input_path.write_text(
        json.dumps(
            {
                "beam": BEAM_INPUT,
                "torque_at_critical_section": {"value": 100, "unit": "N*m"},
                "material": {
                    "name": "generic steel",
                    "yield_strength": {"value": 250, "unit": "MPa"},
                },
                "design_requirement": {"minimum_factor_of_safety": 2},
            }
        ),
        encoding="utf-8",
    )

    text_exit_code = main(["shaft", "size-from-beam", str(input_path)])
    text_output = capsys.readouterr()
    json_exit_code = main(["shaft", "size-from-beam", str(input_path), "--format", "json"])

    output = capsys.readouterr()
    result = json.loads(output.out)
    assert text_exit_code == 0
    assert "Beam-to-shaft static sizing result" in text_output.out
    assert "Critical section: 2 m" in text_output.out
    assert "Composition assumptions:" in text_output.out
    assert text_output.err == ""
    assert json_exit_code == 0
    assert result["critical_section_position"] == {"value": 2.0, "unit": "m"}
    assert result["critical_bending_moment"] == {"value": 2000.0, "unit": "N*m"}
    assert result["shaft_design"]["minimum_required_diameter"]["value"] > 0
    assert result["beam_analysis"]["solver_name"] == "mechdac.beam_statics"
    assert len(result["shaft_design"]["calculation_trace"]) == 5
    assert output.err == ""


@pytest.mark.parametrize(
    ("suffix", "signature"),
    ((".png", b"\x89PNG\r\n\x1a\n"), (".svg", b"<svg")),
)
def test_cli_saves_beam_diagrams_to_png_or_svg(tmp_path, capsys, suffix, signature) -> None:
    input_path = tmp_path / "beam.json"
    input_path.write_text(json.dumps(BEAM_INPUT), encoding="utf-8")
    output_path = tmp_path / f"beam-diagrams{suffix}"

    exit_code = main(
        ["beam", "plot", str(input_path), "--output", str(output_path)]
    )

    output = capsys.readouterr()
    contents = output_path.read_bytes()
    assert exit_code == 0
    assert contents.startswith(signature) if suffix == ".png" else signature in contents
    assert "Saved beam diagrams" in output.out
    assert output.err == ""


def test_cli_rejects_unsupported_beam_plot_file_extension(tmp_path, capsys) -> None:
    input_path = tmp_path / "beam.json"
    input_path.write_text(json.dumps(BEAM_INPUT), encoding="utf-8")
    output_path = tmp_path / "beam-diagrams.pdf"

    exit_code = main(
        ["beam", "plot", str(input_path), "--output", str(output_path)]
    )

    output = capsys.readouterr()
    assert exit_code == 2
    assert "Plot output extension must be .png or .svg" in output.err
    assert not output_path.exists()


def test_cli_explains_how_to_install_missing_plotting_dependency(
    tmp_path, capsys, monkeypatch
) -> None:
    input_path = tmp_path / "beam.json"
    input_path.write_text(json.dumps(BEAM_INPUT), encoding="utf-8")
    output_path = tmp_path / "beam-diagrams.svg"
    for module_name in tuple(sys.modules):
        if module_name == "matplotlib" or module_name.startswith("matplotlib."):
            monkeypatch.delitem(sys.modules, module_name)
    monkeypatch.setitem(sys.modules, "matplotlib", None)
    monkeypatch.delitem(sys.modules, "mechdac.plotting.beam", raising=False)
    monkeypatch.delitem(sys.modules, "mechdac.plotting", raising=False)

    exit_code = main(
        ["beam", "plot", str(input_path), "--output", str(output_path)]
    )

    output = capsys.readouterr()
    assert exit_code == 2
    assert "pip install 'mechdac[plotting]'" in output.err
    assert not output_path.exists()
