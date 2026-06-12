"""Resonance + Phi47: generate with bots, analyze Phi locally, refine weak files."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from resonance.context import ContextSelector
from resonance.engine import ProjectSpec, generate, get_client, run_bot
from resonance.meta.features import extract_file_signals
from resonance.meta.logger import log_meta_decision
from resonance.meta.planner import PlannedRefinement, build_refinement_plan
from resonance.meta.policy_rules import MetaBudget, RuleBasedPolicy

BOT_FOR_PREFIX = {
    "codebot": "CodeBot",
    "apibot": "APIBot",
    "databasebot": "DatabaseBot",
    "testbot": "TestBot",
}


@dataclass
class FileReport:
    path: str
    phi_before: float
    phi_after: float
    refinements: int
    diagnostics: list[dict] = field(default_factory=list)
    meta_reason: str = ""


@dataclass
class PipelineReport:
    output_dir: str
    system_phi_before: float
    system_phi_after: float
    files: list[FileReport]
    total_refinements: int
    generation_seconds: float
    analysis_seconds: float
    refinement_seconds: float
    input_tokens: int
    output_tokens: int
    meta_skipped: int = 0

    def to_dict(self) -> dict:
        return {
            "output_dir": self.output_dir,
            "system_phi_before": round(self.system_phi_before, 4),
            "system_phi_after": round(self.system_phi_after, 4),
            "total_refinements": self.total_refinements,
            "meta_skipped": self.meta_skipped,
            "generation_seconds": round(self.generation_seconds, 2),
            "analysis_seconds": round(self.analysis_seconds, 4),
            "refinement_seconds": round(self.refinement_seconds, 2),
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "files": [
                {
                    "path": f.path,
                    "phi_before": round(f.phi_before, 4),
                    "phi_after": round(f.phi_after, 4),
                    "refinements": f.refinements,
                    "meta_reason": f.meta_reason,
                    "diagnostics": f.diagnostics,
                }
                for f in self.files
            ],
        }


def _require_phi47():
    try:
        from phi47 import Phi47Linter

        return Phi47Linter
    except ImportError as exc:
        raise RuntimeError(
            "Phi47 not installed. Run: pip install phi47-superpowers"
        ) from exc


def _phi_from_diags(diags) -> float:
    for d in diags:
        if d.code == "P001":
            return float(d.phi_value)
    return 0.65


def _needs_refinement(diags, phi: float, threshold: float) -> bool:
    """Legacy threshold check (pre-meta)."""
    if phi < threshold:
        return True
    return any(d.severity == "error" for d in diags)


def _bot_for_file(path: Path) -> str:
    prefix = path.stem.lower().split("_")[0]
    return BOT_FOR_PREFIX.get(prefix, "CodeBot")


def _feedback_task(description: str, diags) -> str:
    lines = [
        f"- [{d.code}] {d.message}. Suggestion: {d.suggestion}" for d in diags[:4]
    ]
    issues = "\n".join(lines) if lines else "- Improve structural integration (Phi)."
    return (
        f"Refactor this Python module for higher structural integration (IIT / Phi).\n\n"
        f"Project: {description}\n\n"
        f"Phi47 issues:\n{issues}\n\n"
        f"Rules: improve cohesion, remove zombies, split god functions; "
        f"keep types and behavior. Return only Python code."
    )


def analyze_directory(linter, output_dir: Path, threshold: float):
    reports = {}
    policy = RuleBasedPolicy(phi_threshold=threshold)
    budget = MetaBudget(max_total_passes=99)
    for path in sorted(output_dir.glob("*.py")):
        diags = linter.lint_file(str(path))
        phi = _phi_from_diags(diags)
        signals = extract_file_signals(path, diags, phi, _bot_for_file(path))
        needs = policy.decide(signals, budget).refine
        reports[path] = (phi, diags, needs)
    return reports


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _legacy_plan(
    raw_analysis: list[tuple[Path, float, list, object]],
    phi_threshold: float,
    max_refinements: int,
) -> dict[Path, PlannedRefinement]:
    plan: dict[Path, PlannedRefinement] = {}
    for path, phi, diags, signals in raw_analysis:
        if _needs_refinement(diags, phi, phi_threshold):
            plan[path] = PlannedRefinement(
                path=path,
                passes=max_refinements,
                bot=_bot_for_file(path),
                reason="legacy",
                priority=0.0,
                signals=signals,
            )
    return plan


async def run_pipeline(
    spec: ProjectSpec,
    *,
    phi_threshold: float = 0.5,
    max_refinements: int = 2,
    style_file: str | None = None,
    use_meta: bool = True,
) -> PipelineReport:
    linter = _require_phi47()(phi_warning=phi_threshold)
    client = get_client()
    policy = RuleBasedPolicy(phi_threshold=phi_threshold)
    budget = MetaBudget(max_total_passes=max_refinements * 4)

    context = ""
    if style_file:
        context = ContextSelector.for_module(Path(style_file).read_text(encoding="utf-8"))

    t0 = time.time()
    await generate(spec, context=context)
    gen_seconds = time.time() - t0

    output_dir = Path(spec.output_dir)
    t1 = time.time()
    raw_analysis: list[tuple[Path, float, list, object]] = []
    for path in sorted(output_dir.glob("*.py")):
        diags = linter.lint_file(str(path))
        phi = _phi_from_diags(diags)
        signals = extract_file_signals(path, diags, phi, _bot_for_file(path))
        raw_analysis.append((path, phi, diags, signals))
    analysis_seconds = time.time() - t1

    if use_meta:
        plan_list = build_refinement_plan(raw_analysis, policy, budget)
    else:
        plan_list = list(_legacy_plan(raw_analysis, phi_threshold, max_refinements).values())
    plan_map = {item.path: item for item in plan_list}

    file_reports: list[FileReport] = []
    total_in = total_out = total_refs = 0
    meta_skipped = 0
    refine_seconds = 0.0

    for path, phi_start, diags, signals in raw_analysis:
        phi_current = phi_start
        refs = 0
        diag_dicts = [
            {"code": d.code, "message": d.message, "severity": d.severity}
            for d in diags[:6]
        ]

        planned = plan_map.get(path)
        if planned is None:
            skip_reason = policy.decide(signals, budget).reason
            meta_skipped += 1
            log_meta_decision(
                output_dir=str(output_dir),
                path=str(path),
                action={"refine": False, "reason": skip_reason},
                signals=signals.to_dict(),
                phi_before=phi_start,
            )
            file_reports.append(
                FileReport(
                    path=str(path),
                    phi_before=phi_start,
                    phi_after=phi_current,
                    refinements=0,
                    diagnostics=diag_dicts,
                    meta_reason=skip_reason,
                )
            )
            continue

        bot = planned.bot
        for _ in range(planned.passes):
            if not budget.can_spend_passes():
                break
            task = _feedback_task(spec.description, diags)
            ctx = ContextSelector.for_module(path.read_text(encoding="utf-8"))
            t2 = time.time()
            result = run_bot(bot, task, ctx, client=client)
            refine_seconds += time.time() - t2
            total_in += result.input_tokens
            total_out += result.output_tokens
            budget.charge(tokens=result.input_tokens + result.output_tokens)
            if result.success:
                path.write_text(result.output, encoding="utf-8")
            refs += 1
            budget.charge()
            diags = linter.lint_file(str(path))
            phi_current = _phi_from_diags(diags)
            signals_after = extract_file_signals(path, diags, phi_current, bot)
            if policy.should_stop_after_pass(signals_after, phi_start, phi_current):
                break

        log_meta_decision(
            output_dir=str(output_dir),
            path=str(path),
            action={"refine": True, "reason": planned.reason, "passes": refs},
            signals=signals.to_dict(),
            phi_before=phi_start,
            phi_after=phi_current,
            refinements=refs,
        )
        total_refs += refs
        file_reports.append(
            FileReport(
                path=str(path),
                phi_before=phi_start,
                phi_after=phi_current,
                refinements=refs,
                diagnostics=diag_dicts,
                meta_reason=planned.reason,
            )
        )

    phis_before = [f.phi_before for f in file_reports]
    phis_after = [f.phi_after for f in file_reports]

    return PipelineReport(
        output_dir=str(output_dir),
        system_phi_before=_mean(phis_before),
        system_phi_after=_mean(phis_after),
        files=file_reports,
        total_refinements=total_refs,
        meta_skipped=meta_skipped,
        generation_seconds=gen_seconds,
        analysis_seconds=analysis_seconds,
        refinement_seconds=refine_seconds,
        input_tokens=total_in,
        output_tokens=total_out,
    )


def run_pipeline_sync(spec: ProjectSpec, **kwargs) -> PipelineReport:
    import asyncio

    return asyncio.run(run_pipeline(spec, **kwargs))


def print_pipeline_report(report: PipelineReport) -> None:
    print(f"\n{'=' * 60}")
    print("  Resonance + Phi47 Pipeline")
    print(f"{'=' * 60}")
    print(f"  Output:            {report.output_dir}")
    print(
        f"  System Phi:        {report.system_phi_before:.3f} -> "
        f"{report.system_phi_after:.3f}"
    )
    print(f"  Refinements:       {report.total_refinements}")
    if report.meta_skipped:
        print(f"  Meta skipped:      {report.meta_skipped} files")
    print(
        f"  Time gen/an/ref:   {report.generation_seconds:.1f}s / "
        f"{report.analysis_seconds:.3f}s / {report.refinement_seconds:.1f}s"
    )
    if report.input_tokens:
        print(
            f"  Refine tokens:     {report.input_tokens} in / "
            f"{report.output_tokens} out"
        )
    print()
    for f in report.files:
        delta = f.phi_after - f.phi_before
        sign = "+" if delta >= 0 else ""
        name = Path(f.path).name
        print(
            f"  {name:<28} Phi {f.phi_before:.3f} -> {f.phi_after:.3f} "
            f"({sign}{delta:.3f})  refs={f.refinements}  meta={f.meta_reason}"
        )
    print(f"{'=' * 60}\n")
