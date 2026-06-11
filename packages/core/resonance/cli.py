"""Editor-agnostic CLI — works from any terminal or editor integration."""

from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

# asyncio used by cmd_generate, cmd_module, cmd_pipeline

from resonance.bots import BOTS
from resonance.context import ContextMode, ContextSelector
from resonance.engine import (
    ProjectSpec,
    generate,
    get_client,
    run_bot,
    run_parallel,
    save_results,
)
from resonance.phi47_bridge import print_pipeline_report, run_pipeline


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def cmd_context(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 1

    content = _read_text(path)
    mode: ContextMode = args.mode

    if args.compare:
        comparison = ContextSelector.compare(content, mode)
        print(f"mode:          {comparison.mode}")
        print(f"full tokens:   {comparison.full_tokens}")
        print(f"minimal tokens: {comparison.minimal_tokens}")
        print(f"saved:         {comparison.saved_tokens} ({comparison.saved_percent}%)")
        if args.show:
            print("\n--- minimal context ---\n")
            print(comparison.minimal_context)
        return 0

    extracted = ContextSelector.extract(content, mode, error_line=args.line)
    if args.json:
        comparison = ContextSelector.compare(content, mode)
        import json

        print(
            json.dumps(
                {
                    "mode": mode,
                    "full_tokens": comparison.full_tokens,
                    "minimal_tokens": comparison.minimal_tokens,
                    "saved_percent": comparison.saved_percent,
                    "context": extracted,
                },
                indent=2,
            )
        )
    else:
        print(extracted)
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    try:
        client = get_client()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    context = ""
    if args.context_file:
        context_path = Path(args.context_file)
        if context_path.exists():
            context = _read_text(context_path)
    elif args.file:
        content = _read_text(Path(args.file))
        mode: ContextMode = args.mode or ContextSelector.default_mode_for_bot(args.bot)
        context = ContextSelector.extract(content, mode, error_line=args.line)

    output_path = Path(args.output)
    t0 = time.time()

    if args.bot == "ALL":
        output_dir = str(output_path.parent)
        base_task = args.task
        tasks = {
            "DatabaseBot": f"Create SQLAlchemy models for: {base_task}",
            "APIBot": f"Create FastAPI endpoints for: {base_task}",
            "TestBot": f"Create pytest tests for: {base_task}",
            "CodeBot": f"Create helper utilities for: {base_task}",
        }
        results = asyncio.run(run_parallel(tasks, context=context, client=client))
        save_results(results, output_dir)
        total_in = sum(r.input_tokens for r in results)
        total_out = sum(r.output_tokens for r in results)
        print(f"\nTotal tokens: {total_in} input, {total_out} output")
    else:
        if args.bot not in BOTS:
            print(
                f"ERROR: unknown bot '{args.bot}'. Valid: {list(BOTS.keys())} or ALL",
                file=sys.stderr,
            )
            return 1

        result = run_bot(args.bot, args.task, context, client=client)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result.output, encoding="utf-8")

        elapsed = round(time.time() - t0, 2)
        cost = result.input_tokens * 0.000003 + result.output_tokens * 0.000015
        print(f"Output: {output_path}")
        print(f"Tokens: {result.input_tokens} input, {result.output_tokens} output")
        print(f"Cost:   ~${cost:.4f}")
        print(f"Time:   {elapsed}s")

        if args.file and not args.quiet:
            full = _read_text(Path(args.file))
            mode = args.mode or ContextSelector.default_mode_for_bot(args.bot)
            comparison = ContextSelector.compare(full, mode)
            print(
                f"Context savings: {comparison.saved_tokens} tokens "
                f"({comparison.saved_percent}%) vs full file"
            )

    return 0


def cmd_pipeline(args: argparse.Namespace) -> int:
    spec = ProjectSpec(
        name=args.name or "Generated Module",
        description=args.description,
        requirements=args.requirement or [],
        output_dir=args.output_dir,
    )

    try:
        report = asyncio.run(
            run_pipeline(
                spec,
                phi_threshold=args.phi_threshold,
                max_refinements=args.max_refinements,
                style_file=args.file,
            )
        )
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        import json

        print(json.dumps(report.to_dict(), indent=2))
    else:
        print_pipeline_report(report)

    if report.system_phi_after < args.phi_threshold:
        print(
            f"WARNING: system Phi {report.system_phi_after:.3f} still below "
            f"threshold {args.phi_threshold}",
            file=sys.stderr,
        )
        return 2 if args.strict else 0

    return 0


def cmd_module(args: argparse.Namespace) -> int:
    spec = ProjectSpec(
        name=args.name or "Generated Module",
        description=args.description,
        requirements=args.requirement or [],
        output_dir=args.output_dir,
    )

    context = ""
    if args.file:
        context = ContextSelector.for_module(_read_text(Path(args.file)))

    asyncio.run(generate(spec, context=context))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resonance",
        description="Resonance — specialized bots with minimal token context",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    context_parser = sub.add_parser(
        "context", help="Extract minimal context or compare token savings"
    )
    context_parser.add_argument("file", help="Source file path")
    context_parser.add_argument(
        "--mode",
        choices=["tests", "endpoint", "module", "bugfix", "full"],
        default="tests",
        help="Extraction strategy (default: tests)",
    )
    context_parser.add_argument("--line", type=int, help="Error line for bugfix mode")
    context_parser.add_argument(
        "--compare", action="store_true", help="Show token comparison stats"
    )
    context_parser.add_argument(
        "--show", action="store_true", help="With --compare, print extracted context"
    )
    context_parser.add_argument(
        "--json", action="store_true", help="Output JSON with stats and context"
    )
    context_parser.set_defaults(func=cmd_context)

    generate_parser = sub.add_parser("generate", help="Run a bot with optional context")
    generate_parser.add_argument(
        "--bot", required=True, help="Bot name or ALL for parallel module generation"
    )
    generate_parser.add_argument("--task", required=True, help="Task description")
    generate_parser.add_argument("--file", help="Source file for automatic context extraction")
    generate_parser.add_argument(
        "--mode",
        choices=["tests", "endpoint", "module", "bugfix", "full"],
        help="Context mode when using --file",
    )
    generate_parser.add_argument("--line", type=int, help="Error line for bugfix mode")
    generate_parser.add_argument("--context-file", help="Pre-extracted context file")
    generate_parser.add_argument("--output", required=True, help="Output file path")
    generate_parser.add_argument(
        "--quiet", action="store_true", help="Hide context savings summary"
    )
    generate_parser.set_defaults(func=cmd_generate)

    module_parser = sub.add_parser("module", help="Generate a full module in parallel")
    module_parser.add_argument("--description", required=True, help="Module description")
    module_parser.add_argument("--name", default="Generated Module")
    module_parser.add_argument(
        "--requirement", action="append", dest="requirement", default=[]
    )
    module_parser.add_argument("--output-dir", default="output/module")
    module_parser.add_argument(
        "--file", help="Optional style reference file (minimal context only)"
    )
    module_parser.set_defaults(func=cmd_module)

    pipeline_parser = sub.add_parser(
        "pipeline",
        help="Resonance + Phi47: generate module, analyze Phi, refine weak files",
    )
    pipeline_parser.add_argument("--description", required=True, help="Module description")
    pipeline_parser.add_argument("--name", default="Generated Module")
    pipeline_parser.add_argument(
        "--requirement", action="append", dest="requirement", default=[]
    )
    pipeline_parser.add_argument("--output-dir", default="output/module")
    pipeline_parser.add_argument(
        "--file", help="Optional style reference file (minimal context)"
    )
    pipeline_parser.add_argument(
        "--phi-threshold",
        type=float,
        default=0.5,
        help="Minimum Phi; files below get refined (default: 0.5)",
    )
    pipeline_parser.add_argument(
        "--max-refinements",
        type=int,
        default=2,
        help="Max refinement passes per weak file (default: 2)",
    )
    pipeline_parser.add_argument("--json", action="store_true", help="Output JSON report")
    pipeline_parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit code 2 if system Phi below threshold after pipeline",
    )
    pipeline_parser.set_defaults(func=cmd_pipeline)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
