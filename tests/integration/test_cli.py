"""
test_cli.py

Phase 7 unit tests — CLI (`humanoid run`, `humanoid check`).
"""

from main import main


def test_check_valid_file_returns_zero(tmp_path, capsys):
    file_path = tmp_path / "valid.hum"
    file_path.write_text('print("hello")')

    exit_code = main(["check", str(file_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "syntax OK" in captured.out


def test_check_invalid_syntax_returns_nonzero(tmp_path, capsys):
    file_path = tmp_path / "invalid.hum"
    file_path.write_text("walk banana 2m")

    exit_code = main(["check", str(file_path)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "PARSE ERROR" in captured.out


def test_run_valid_program_returns_zero(tmp_path, capsys):
    file_path = tmp_path / "program.hum"
    file_path.write_text('print("hello")')

    exit_code = main(["run", str(file_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "hello" in captured.out


def test_run_missing_file_returns_nonzero(capsys):
    exit_code = main(["run", "does_not_exist.hum"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "not found" in captured.out.lower()


def test_run_robotics_error_returns_nonzero(tmp_path, capsys):
    file_path = tmp_path / "program.hum"
    file_path.write_text("robot H1\nwalk forward 2m")  # walk before stand

    exit_code = main(["run", str(file_path)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "ROBOTICS ERROR" in captured.out


def test_run_unreachable_target_returns_nonzero(tmp_path, capsys):
    file_path = tmp_path / "program.hum"
    file_path.write_text(
        "robot H1\n"
        "object target at (10.0, 10.0)\n"
        "stand\n"
        "reach right_hand to target\n"
    )

    exit_code = main(["run", str(file_path)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "ROBOTICS ERROR" in captured.out