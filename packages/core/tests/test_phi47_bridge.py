from pathlib import Path
from unittest.mock import MagicMock

from resonance.phi47_bridge import (
    _bot_for_file,
    _feedback_task,
    _needs_refinement,
    analyze_directory,
)


class FakeDiag:
    def __init__(self, code, message, severity, phi_value=0.4, suggestion="fix"):
        self.code = code
        self.message = message
        self.severity = severity
        self.phi_value = phi_value
        self.suggestion = suggestion


def test_bot_for_file():
    assert _bot_for_file(Path("testbot_tests.py")) == "TestBot"
    assert _bot_for_file(Path("apibot_api.py")) == "APIBot"


def test_needs_refinement():
    assert _needs_refinement([FakeDiag("P001", "low", "warning", 0.3)], 0.3, 0.5)
    assert not _needs_refinement([FakeDiag("P004", "ok", "info", 0.8)], 0.8, 0.5)


def test_feedback_task():
    task = _feedback_task("Auth", [FakeDiag("P007", "god fn", "hint")])
    assert "P007" in task and "Auth" in task


def test_analyze_directory(tmp_path: Path):
    f = tmp_path / "codebot_code.py"
    f.write_text("def foo():\n    return 1\n", encoding="utf-8")
    linter = MagicMock()
    linter.lint_file.return_value = [FakeDiag("P001", "low", "warning", 0.35)]
    result = analyze_directory(linter, tmp_path, 0.5)
    assert result[f][2] is True
