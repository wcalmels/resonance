# Contributing to Resonance

Thank you for contributing to a reproducible research artifact. This project follows academic software engineering practices.

## Before you start

1. Read [paper/PAPER.md](paper/PAPER.md) for scope and claims
2. Read [docs/METHODOLOGY.md](docs/METHODOLOGY.md) for evaluation standards
3. Read [docs/ETHICS.md](docs/ETHICS.md) for responsible use

## Development setup

```bash
git clone https://github.com/wcalmels/resonance.git
cd resonance
python -m venv .venv && source .venv/bin/activate
pip install -e "packages/core[dev]"
```

## Quality gates

All pull requests must pass:

```bash
pytest packages/core/tests/ -v
python benchmarks/benchmark_context.py
```

CI runs on Python 3.10, 3.11, and 3.12 (see `.github/workflows/ci.yml`).

## Contribution types

| Type | Requirements |
|------|--------------|
| Bug fix | Test covering the fix |
| New context mode | Unit tests + update `docs/METHODOLOGY.md` |
| New bot | Entry in `bots.py` + tests + paper appendix if claim changes |
| Benchmark change | Document in `docs/METHODOLOGY.md`; do not inflate claims |
| Documentation | Accurate, conservative language |

## Claims and honesty

- Do not claim physical resonance, emergent intelligence, or unmeasured speedups
- Report token savings with the offline benchmark or API token counts
- Label human time estimates as estimates
- Update `paper/PAPER.md` if methodology or results change materially

## Code style

- Python: PEP 8, type hints on public functions
- Match existing patterns in `packages/core/resonance/`
- Keep changes focused — minimal diffs

## Pull request checklist

- [ ] Tests pass locally
- [ ] Offline benchmark runs without API key
- [ ] No secrets in commits (`.env`, API keys)
- [ ] Claims in README/paper remain accurate
- [ ] New features documented

## Code of conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
