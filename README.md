# Resonance

[![CI](https://github.com/wcalmels/resonance/actions/workflows/ci.yml/badge.svg)](https://github.com/wcalmels/resonance/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://img.shields.io/badge/DOI-pending-Zenodo-blue)](https://zenodo.org/)

**Task-specialized LLM orchestration with minimal context for token-efficient code generation.**

Research preprint: **[paper/PAPER.md](paper/PAPER.md)** · Reproducibility: **[docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md)** · Cite: **[CITATION.cff](CITATION.cff)**

---

## Abstract

Resonance is an editor-agnostic research artifact that combines specialized LLM bots, deterministic context extraction (*ContextSelector*), and parallel orchestration. Offline benchmarks demonstrate **60–85% input token reduction** on standard Python boilerplate tasks. The framework ships with reproducible evaluation scripts, unit tests, multi-editor integrations, and an academic methodology document.

> **Epistemic note:** Resonance is structured LLM orchestration — not a physical resonance mechanism. See Section 1.3 of the paper.

---

## Research contributions

| ID | Contribution | Artifact |
|----|--------------|----------|
| C1 | Minimal-context policy per task mode | `packages/core/resonance/context.py` |
| C2 | Reproducible specialized bot prompts | `packages/core/resonance/bots.py` |
| C3 | Parallel orchestration engine + CLI | `packages/core/resonance/engine.py` |
| C4 | Offline token benchmark (no API) | `benchmarks/benchmark_context.py` |
| C5 | API benchmarks with conservative interpretation | `benchmarks.py` |

---

## Repository structure

```
resonance/
├── paper/                  # Academic preprint + references.bib
├── packages/
│   ├── core/               # Installable Python package
│   └── vscode/             # VS Code extension (CLI wrapper)
├── benchmarks/             # Reproducible evaluation
├── docs/                   # Methodology, reproducibility, ethics
├── .cursor/skills/         # Cursor agent skill
├── editors/                # AGENTS.md, CLAUDE.md
├── examples/
└── CITATION.cff            # Machine-readable citation
```

---

## Quick start

```bash
git clone https://github.com/wcalmels/resonance.git
cd resonance
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Unix:     source .venv/bin/activate
pip install -e "packages/core[dev]"
```

### Reproduce token savings (no API key)

```bash
python benchmarks/benchmark_context.py
pytest packages/core/tests/ -v
python -m resonance context examples/sample_module.py --mode tests --compare
```

### Generate code (requires API key)

```bash
cp .env.example .env   # set ANTHROPIC_API_KEY
python -m resonance generate \
  --bot TestBot \
  --task "pytest suite for public functions" \
  --file examples/sample_module.py \
  --output output/test_sample.py
```

---

## Editor integrations

| Environment | Entry point |
|-------------|-------------|
| Any terminal | `python -m resonance` |
| Cursor | `.cursor/skills/resonance/SKILL.md` |
| VS Code | `packages/vscode` |
| Claude Code | `CLAUDE.md` |
| Other AI agents | `AGENTS.md` |

Details: [editors/README.md](editors/README.md)

---

## Documentation

| Document | Purpose |
|----------|---------|
| [paper/PAPER.md](paper/PAPER.md) | Full research paper |
| [docs/METHODOLOGY.md](docs/METHODOLOGY.md) | Evaluation protocol |
| [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) | Replication guide |
| [docs/ETHICS.md](docs/ETHICS.md) | Responsible use |
| [docs/ZENODO.md](docs/ZENODO.md) | DOI registration (Zenodo) |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |

---

## Citation

```bibtex
@software{resonance2026,
  author  = {Calmels, W. and Resonance Contributors},
  title   = {Resonance: Task-Specialized LLM Orchestration with Minimal Context},
  year    = {2026},
  url     = {https://github.com/wcalmels/resonance},
  version = {0.2.0},
  license = {MIT}
}
```

---

## License

- **Software:** MIT — [LICENSE](LICENSE)
- **Paper:** CC BY 4.0 — see [paper/PAPER.md](paper/PAPER.md)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
