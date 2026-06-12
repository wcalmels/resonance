# Benchmarks

## Offline (reproducible, no API key)

### Context token savings

```bash
python benchmarks/benchmark_context.py
```

Output: `benchmarks/results/context_benchmark.json`

Validates token savings claims in `paper/PAPER.md` Section 8.1.

### Resonance + Phi47 pipeline

Requires `phi47-superpowers` installed (`pip install phi47-superpowers`).

```bash
pip install phi47-superpowers
python benchmarks/benchmark_pipeline.py
python benchmarks/benchmark_pipeline.py --runs 10
```

Output: `benchmarks/results/pipeline_benchmark.json`

Measures Phi47 analysis latency on 4-file fixtures, simulates refinement with curated files, and validates that system Phi improves. No API key required.

Optional live run (API cost ~$0.10–0.30):

```bash
python benchmarks/benchmark_pipeline.py --live --description "JWT auth module"
```

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
