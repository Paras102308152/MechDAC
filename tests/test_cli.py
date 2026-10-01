import json

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
