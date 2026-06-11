#!/usr/bin/env python3
"""
Reproducible offline benchmark for ContextSelector token savings.

No API key required. Produces JSON report for academic replication.

Usage:
    python benchmarks/benchmark_context.py
    python benchmarks/benchmark_context.py --output benchmarks/results/context_benchmark.json
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "packages" / "core"))

from resonance.context import ContextSelector  # noqa: E402

MODES = ["tests", "endpoint", "module", "full"]


def synthetic_module(lines: int, body_ratio: float = 0.8) -> str:
    """Generate a synthetic Python module with configurable size."""
    header = [
        '"""Synthetic module for benchmark."""',
        "from __future__ import annotations",
        "import os",
        "from typing import Optional, List",
        "",
        "class SyntheticService:",
        "    def __init__(self, connection):",
        "        self.connection = connection",
        "",
    ]
    body_lines = max(0, lines - len(header) - 5)
    body_count = int(body_lines * body_ratio)
    sig_count = body_lines - body_count

    parts = list(header)
    for i in range(sig_count // 2):
        parts.append(f"    def method_{i}(self, x: int) -> int:")
        parts.append(f'        """Method {i}."""')
        parts.append(f"        return x + {i}")
        parts.append("")

    for i in range(body_count // 3):
        parts.append(f"    def helper_{i}(self, data: List[int]) -> int:")
        parts.append(f"        total = 0")
        parts.append(f"        for item in data:")
        parts.append(f"            total += item * {i + 1}")
        parts.append(f"        return total")
        parts.append("")

    parts.extend(
        [
            "def validate_input(value: str) -> bool:",
            "    return bool(value and value.strip())",
            "",
        ]
    )
    return "\n".join(parts)


def benchmark_file(label: str, content: str) -> dict:
    results = {}
    for mode in MODES:
        comparison = ContextSelector.compare(content, mode)  # type: ignore[arg-type]
        results[mode] = {
            "full_tokens": comparison.full_tokens,
            "minimal_tokens": comparison.minimal_tokens,
            "saved_tokens": comparison.saved_tokens,
            "saved_percent": comparison.saved_percent,
        }
    return {"label": label, "lines": len(content.splitlines()), "modes": results}


def aggregate(all_results: list[dict], mode: str) -> dict:
    percents = [r["modes"][mode]["saved_percent"] for r in all_results if mode in r["modes"]]
    if not percents:
        return {}
    return {
        "mean_saved_percent": round(statistics.mean(percents), 1),
        "median_saved_percent": round(statistics.median(percents), 1),
        "stdev_saved_percent": round(statistics.stdev(percents), 1) if len(percents) > 1 else 0.0,
        "n": len(percents),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline ContextSelector benchmark")
    parser.add_argument(
        "--output",
        default=str(REPO_ROOT / "benchmarks" / "results" / "context_benchmark.json"),
    )
    args = parser.parse_args()

    corpus: list[tuple[str, str]] = []

    sample_path = REPO_ROOT / "examples" / "sample_module.py"
    if sample_path.exists():
        corpus.append(("sample_module", sample_path.read_text(encoding="utf-8")))

    for size in (50, 100, 200, 500, 1000):
        corpus.append((f"synthetic_{size}l", synthetic_module(size)))

    for ratio in (0.5, 0.7, 0.9):
        corpus.append((f"synthetic_ratio_{ratio}", synthetic_module(300, body_ratio=ratio)))

    all_results = [benchmark_file(label, content) for label, content in corpus]

    report = {
        "benchmark": "context_token_savings",
        "version": "0.2.0",
        "token_estimator": "chars/4",
        "corpus_size": len(corpus),
        "files": all_results,
        "aggregate": {mode: aggregate(all_results, mode) for mode in MODES},
        "hypothesis_tests": {
            "H1_tests_mode_saves_ge_50pct_on_sample": (
                all_results[0]["modes"]["tests"]["saved_percent"] >= 50
                if all_results
                else None
            ),
            "H1_synthetic_tests_mean_ge_50pct": (
                aggregate(all_results, "tests").get("mean_saved_percent", 0) >= 50
            ),
        },
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Context benchmark written to: {output_path}")
    print("\nAggregate savings (tests mode):")
    agg = report["aggregate"].get("tests", {})
    print(f"  mean:   {agg.get('mean_saved_percent', 'n/a')}%")
    print(f"  median: {agg.get('median_saved_percent', 'n/a')}%")
    print(f"  n:      {agg.get('n', 0)} files")

    if report["hypothesis_tests"]["H1_synthetic_tests_mean_ge_50pct"]:
        print("\nH1 (mean tests savings >= 50%): SUPPORTED")
    else:
        print("\nH1 (mean tests savings >= 50%): NOT SUPPORTED on this corpus")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
