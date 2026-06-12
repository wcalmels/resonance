from pathlib import Path

from resonance.meta.features import extract_file_signals
from resonance.meta.planner import build_refinement_plan
from resonance.meta.policy_rules import MetaBudget, RuleBasedPolicy


class FakeDiag:
    def __init__(self, code, message, severity, phi_value=0.4, suggestion="fix"):
        self.code = code
        self.message = message
        self.severity = severity
        self.phi_value = phi_value
        self.suggestion = suggestion


def test_phi_ok_skips_refinement(tmp_path: Path):
    f = tmp_path / "codebot_code.py"
    f.write_text(
        "def a(x):\n    return b(x)\n\ndef b(x):\n    return x + 1\n",
        encoding="utf-8",
    )
    diags = [FakeDiag("P004", "ok", "info", 0.7)]
    signals = extract_file_signals(f, diags, phi=0.7, bot="CodeBot")
    action = RuleBasedPolicy(0.5).decide(signals, MetaBudget())
    assert not action.refine
    assert action.reason == "phi_ok"


def test_syntax_refines(tmp_path: Path):
    f = tmp_path / "apibot_api.py"
    f.write_text("def broken(:\n    pass\n", encoding="utf-8")
    diags = [FakeDiag("P000", "Syntax", "error", 0.0)]
    signals = extract_file_signals(f, diags, phi=0.0, bot="APIBot")
    action = RuleBasedPolicy(0.5).decide(signals, MetaBudget())
    assert action.refine
    assert action.reason == "syntax"


def test_plan_respects_global_budget(tmp_path: Path):
    files = []
    for i in range(3):
        p = tmp_path / f"codebot_{i}.py"
        p.write_text(f"def f{i}():\n    return {i}\n", encoding="utf-8")
        diags = [FakeDiag("P001", "low", "warning", 0.2)]
        signals = extract_file_signals(p, diags, phi=0.2, bot="CodeBot")
        files.append((p, 0.2, diags, signals))

    policy = RuleBasedPolicy(0.5)
    budget = MetaBudget(max_total_passes=2)
    plan = build_refinement_plan(files, policy, budget)
    assert sum(p.passes for p in plan) <= 2


def test_high_phi_with_only_warnings_skipped(tmp_path: Path):
    f = tmp_path / "testbot_tests.py"
    f.write_text("def a():\n    return b()\n\ndef b():\n    return 1\n", encoding="utf-8")
    diags = [FakeDiag("P001", "below", "warning", 0.55)]
    signals = extract_file_signals(f, diags, phi=0.65, bot="TestBot")
    action = RuleBasedPolicy(0.5).decide(signals, MetaBudget())
    assert not action.refine
