# Benchmarks

## Offline (reproducible, no API key)

```bash
python benchmarks/benchmark_context.py
```

Output: `benchmarks/results/context_benchmark.json`

Validates token savings claims in `paper/PAPER.md` Section 8.1.

## With API (optional)

```bash
cp .env.example .env   # set ANTHROPIC_API_KEY
python benchmarks.py
```

Output: `benchmark_results.json` (gitignored)

Estimated cost: $0.10–0.20 USD per run.

## Unit tests

```bash
pytest packages/core/tests/ -v
```
