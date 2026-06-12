#!/usr/bin/env python3
"""
Reproducible benchmark for Resonance + Phi47 pipeline performance.

Offline mode (default, no API key):
  - Measures Phi47 analysis latency on fixed 4-file module fixtures
  - Simulates refinement decisions and Phi improvement with curated refined files
  - Reports gen/an/ref time breakdown (generation = 0 in offline mode)

Live mode (optional, requires ANTHROPIC_API_KEY):
  - Runs the full generate -> analyze -> refine pipeline via API

Usage:
    python benchmarks/benchmark_pipeline.py
    python benchmarks/benchmark_pipeline.py --runs 10
    python benchmarks/benchmark_pipeline.py --live --description "JWT auth module"
"""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import statistics
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "packages" / "core"))

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "pipeline"
REFINED_DIR = FIXTURES_DIR / "refined"
BOT_FILES = (
    "codebot_helpers.py",
    "databasebot_models.py",
    "apibot_routes.py",
    "testbot_tests.py",
)
REFINABLE = ("databasebot_models.py", "apibot_routes.py")


def _require_phi47():
    try:
        from phi47 import Phi47Linter

        return Phi47Linter
    except ImportError:
        print(
            "Phi47 not installed. Run: pip install phi47-superpowers\n"
            "  or: pip install -e ../phi47-superpowers",
            file=sys.stderr,
        )
        raise SystemExit(1) from None


def _median_ms(times: list[float]) -> float:
    return round(statistics.median(times), 4) if times else 0.0


def _mean(values: list[float]) -> float:
    return round(statistics.mean(values), 4) if values else 0.0


def _count_zero_phi(files: list[dict]) -> int:
    return sum(1 for f in files if f["phi"] < 0.01)


def _copy_fixtures(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for name in BOT_FILES:
        shutil.copy2(FIXTURES_DIR / name, dest / name)


def _apply_refined_fixtures(dest: Path, names: tuple[str, ...]) -> None:
    for name in names:
        shutil.copy2(REFINED_DIR / name, dest / name)


def benchmark_analysis(
    linter,
    output_dir: Path,
    threshold: float,
    runs: int,
) -> dict:
    from resonance.phi47_bridge import analyze_directory

    timings: list[float] = []
    last_analysis = None
    for _ in range(runs):
        t0 = time.perf_counter()
        last_analysis = analyze_directory(linter, output_dir, threshold)
        timings.append((time.perf_counter() - t0) * 1000)

    files = []
    weak_count = 0
    if last_analysis:
        for path, (phi, diags, needs) in last_analysis.items():
            if needs:
                weak_count += 1
            files.append(
                {
                    "path": path.name,
                    "phi": round(phi, 4),
                    "needs_refinement": needs,
                    "diagnostics": len(diags),
                }
            )

    phis = [f["phi"] for f in files]
    return {
        "runs": runs,
        "files_analyzed": len(files),
        "weak_files": weak_count,
        "system_phi": _mean(phis),
        "analysis_median_ms": _median_ms(timings),
        "analysis_mean_ms": round(statistics.mean(timings), 4) if timings else 0.0,
        "per_file_median_ms": round(_median_ms(timings) / max(len(files), 1), 4),
        "files": files,
    }


def benchmark_offline(
    *,
    runs: int,
    threshold: float,
    max_refinements: int,
) -> dict:
    from resonance.phi47_bridge import analyze_directory

    linter = _require_phi47()(phi_warning=threshold)

    with tempfile.TemporaryDirectory(prefix="resonance_pipeline_bench_") as tmp:
        work = Path(tmp) / "module"
        _copy_fixtures(work)

        before = benchmark_analysis(linter, work, threshold, runs)
        phi_before = before["system_phi"]

        refine_timings: list[float] = []
        refinements_applied = 0
        for name in REFINABLE:
            if refinements_applied >= max_refinements * len(REFINABLE):
                break
            t0 = time.perf_counter()
            _apply_refined_fixtures(work, (name,))
            analyze_directory(linter, work, threshold)
            refine_timings.append((time.perf_counter() - t0) * 1000)
            refinements_applied += 1

        after = benchmark_analysis(linter, work, threshold, runs)
        phi_after = after["system_phi"]

    return {
        "mode": "offline",
        "phi_threshold": threshold,
        "max_refinements": max_refinements,
        "timing": {
            "generation_seconds": 0.0,
            "analysis_seconds": round(before["analysis_median_ms"] / 1000, 6),
            "refinement_seconds": round(sum(refine_timings) / 1000, 6),
            "analysis_median_ms": before["analysis_median_ms"],
            "refinement_simulated_steps": refinements_applied,
            "refinement_step_median_ms": _median_ms(refine_timings),
        },
        "quality": {
            "system_phi_before": phi_before,
            "system_phi_after": phi_after,
            "phi_delta": round(phi_after - phi_before, 4),
            "weak_files_before": before["weak_files"],
            "weak_files_after": after["weak_files"],
        },
        "before_analysis": before,
        "after_analysis": after,
        "hypothesis_tests": {
            "H1_analysis_under_50ms_for_4_files": before["analysis_median_ms"] < 50,
            "H2_system_phi_improves_after_refinement": phi_after > phi_before,
            "H3_zero_phi_files_decrease": _count_zero_phi(after["files"])
            < _count_zero_phi(before["files"]),
        },
    }


def benchmark_live(
    *,
    description: str,
    output_dir: str,
    threshold: float,
    max_refinements: int,
) -> dict:
    from resonance.engine import ProjectSpec
    from resonance.phi47_bridge import run_pipeline_sync

    _require_phi47()

    spec = ProjectSpec(
        name="Benchmark Module",
        description=description,
        requirements=["JWT", "pytest"],
        output_dir=output_dir,
    )

    report = run_pipeline_sync(
        spec,
        phi_threshold=threshold,
        max_refinements=max_refinements,
    )

    total_seconds = (
        report.generation_seconds
        + report.analysis_seconds
        + report.refinement_seconds
    )
    phi_overhead_pct = (
        round(100 * report.analysis_seconds / total_seconds, 2)
        if total_seconds > 0
        else 0.0
    )

    return {
        "mode": "live",
        "description": description,
        "output_dir": report.output_dir,
        "phi_threshold": threshold,
        "timing": {
            "generation_seconds": round(report.generation_seconds, 2),
            "analysis_seconds": round(report.analysis_seconds, 4),
            "refinement_seconds": round(report.refinement_seconds, 2),
            "total_seconds": round(total_seconds, 2),
            "phi_overhead_percent": phi_overhead_pct,
        },
        "quality": {
            "system_phi_before": round(report.system_phi_before, 4),
            "system_phi_after": round(report.system_phi_after, 4),
            "phi_delta": round(report.system_phi_after - report.system_phi_before, 4),
            "total_refinements": report.total_refinements,
        },
        "tokens": {
            "refinement_input": report.input_tokens,
            "refinement_output": report.output_tokens,
        },
        "files": [
            {
                "path": Path(f.path).name,
                "phi_before": round(f.phi_before, 4),
                "phi_after": round(f.phi_after, 4),
                "refinements": f.refinements,
            }
            for f in report.files
        ],
    }


def system_info() -> dict:
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor() or "unknown",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resonance + Phi47 pipeline benchmark")
    parser.add_argument(
        "--output",
        default=str(REPO_ROOT / "benchmarks" / "results" / "pipeline_benchmark.json"),
    )
    parser.add_argument("--runs", type=int, default=5, help="Analysis timing repetitions")
    parser.add_argument("--phi-threshold", type=float, default=0.5)
    parser.add_argument("--max-refinements", type=int, default=2)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run full API pipeline (requires ANTHROPIC_API_KEY)",
    )
    parser.add_argument(
        "--description",
        default="User authentication with JWT tokens",
    )
    parser.add_argument(
        "--output-dir",
        default=str(REPO_ROOT / "benchmarks" / "results" / "live_pipeline_output"),
    )
    args = parser.parse_args()

    if args.live:
        result = benchmark_live(
            description=args.description,
            output_dir=args.output_dir,
            threshold=args.phi_threshold,
            max_refinements=args.max_refinements,
        )
    else:
        result = benchmark_offline(
            runs=args.runs,
            threshold=args.phi_threshold,
            max_refinements=args.max_refinements,
        )

    report = {
        "benchmark": "resonance_phi47_pipeline",
        "version": "0.2.1",
        "system": system_info(),
        **result,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Pipeline benchmark written to: {output_path}\n")

    if report["mode"] == "offline":
        t = report["timing"]
        q = report["quality"]
        print("Offline pipeline simulation (fixtures, no API)")
        print(f"  Analysis (median):  {t['analysis_median_ms']} ms for 4 files")
        print(f"  Per file (median):  {report['before_analysis']['per_file_median_ms']} ms")
        print(
            f"  System Phi:         {q['system_phi_before']} -> {q['system_phi_after']} "
            f"(delta {q['phi_delta']:+.4f})"
        )
        zero_before = _count_zero_phi(report["before_analysis"]["files"])
        zero_after = _count_zero_phi(report["after_analysis"]["files"])
        print(f"  Zero-Phi files:     {zero_before} -> {zero_after}")
        print(
            f"  Below threshold:    {q['weak_files_before']} -> {q['weak_files_after']}"
        )
        print()
        for key, ok in report["hypothesis_tests"].items():
            print(f"  {key}: {'PASS' if ok else 'FAIL'}")
    else:
        t = report["timing"]
        q = report["quality"]
        print("Live pipeline (API)")
        print(
            f"  Time gen/an/ref:    {t['generation_seconds']}s / "
            f"{t['analysis_seconds']}s / {t['refinement_seconds']}s"
        )
        print(f"  Phi overhead:       {t['phi_overhead_percent']}% of total time")
        print(
            f"  System Phi:         {q['system_phi_before']} -> {q['system_phi_after']}"
        )
        print(f"  Refinements:        {q['total_refinements']}")
        if report["tokens"]["refinement_input"]:
            tok = report["tokens"]
            print(
                f"  Refine tokens:      {tok['refinement_input']} in / "
                f"{tok['refinement_output']} out"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
