# Reproducibility Guide

This document describes how to reproduce all claims in `paper/PAPER.md` without relying on undocumented steps.

## Artifact overview

| Artifact | Path | API key required |
|----------|------|------------------|
| Core package | `packages/core/` | No (except generation) |
| Unit tests | `packages/core/tests/` | No |
| Context benchmark | `benchmarks/benchmark_context.py` | **No** |
| API benchmarks | `benchmarks.py` | Yes |
| Sample module | `examples/sample_module.py` | No |

## Environment

- Python ≥ 3.9 (tested on 3.14)
- OS: Windows, macOS, Linux
- Optional: `ANTHROPIC_API_KEY` for live generation benchmarks

### Fixed setup

```bash
git clone https://github.com/wcalmels/resonance.git
cd resonance
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix:    source .venv/bin/activate
pip install -e "packages/core[dev]"
```

On Windows without `python` in PATH, use `py -3` instead of `python`.

## Claim 1: Token reduction (60–85%)

**Reproduce:**

```bash
python benchmarks/benchmark_context.py
```

**Expected:** JSON report at `benchmarks/results/context_benchmark.json` with `saved_percent` ≥ 50 for `tests` mode on modules with long function bodies.

**Verify manually:**

```bash
python -m resonance context examples/sample_module.py --mode tests --compare
```

## Claim 2: Unit test suite passes

```bash
pytest packages/core/tests/ -v --tb=short
```

**Expected:** 9+ tests, 0 failures.

## Claim 3: API speedup and parallelism

Requires `ANTHROPIC_API_KEY` in `.env`:

```bash
cp .env.example .env
python benchmarks.py
```

**Output:** `benchmark_results.json` at repository root.

**Cost:** approximately $0.10–0.20 USD per full run.

## Determinism

| Component | Deterministic? |
|-----------|----------------|
| ContextSelector | Yes — same file + mode → same output |
| Bot system prompts | Yes — fixed in `bots.py` |
| LLM generation | No — stochastic sampling |

## Reporting issues

If results diverge significantly, open an issue with:

1. Python version (`python --version`)
2. OS
3. Output of `benchmarks/benchmark_context.py`
4. Model name (for API benchmarks)
