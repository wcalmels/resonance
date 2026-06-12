# Changelog

## [0.2.3] - 2026-06-12

### Added
- Meta-reasoning layer (`resonance/meta/`): structural signals, fractal graph dimension, rule-based refinement policy
- Global refinement budget and prioritized plan (fewer useless API calls)
- JSONL decision log at `~/.resonance/meta_runs.jsonl` for future KAN training

### Changed
- Pipeline uses `RuleBasedPolicy` by default (`use_meta=True`); set `use_meta=False` for legacy behavior

## [0.2.2] - 2026-06-12

### Fixed
- Strip markdown code fences from LLM output before saving (`output_clean.py`)
- Prevents false Phi47 P000 parse errors and unnecessary pipeline refinements

### Added
- Reproducible pipeline benchmark (`benchmarks/benchmark_pipeline.py`)

## [0.2.1] - 2026-06-12

### Added
- Resonance + Phi47 pipeline (`phi47_bridge.py`)
- VS Code extension synergy commands

## [0.2.0] - 2026-06-11

### Added
- ContextSelector, specialized bots, parallel engine, CLI
