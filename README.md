# Resonance

[![CI](https://github.com/wcalmels/resonance/actions/workflows/ci.yml/badge.svg)](https://github.com/wcalmels/resonance/actions/workflows/ci.yml)
[![VS Marketplace](https://img.shields.io/visual-studio-marketplace/v/wcalmels.resonance?label=VS%20Marketplace)](https://marketplace.visualstudio.com/items?itemName=wcalmels.resonance)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20648248.svg)](https://doi.org/10.5281/zenodo.20648248)

**Task-specialized LLM orchestration with minimal context for token-efficient code generation.**

Research preprint: **[paper/PAPER.md](paper/PAPER.md)** · Reproducibility: **[docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md)** · Cite: **[CITATION.cff](CITATION.cff)**

**Synergy quick start (Resonance + Phi47):** **[docs/QUICKSTART.md](docs/QUICKSTART.md)** — both extensions on [VS Marketplace](https://marketplace.visualstudio.com/search?term=wcalmels&target=VSCode&category=All%20categories&sortBy=Relevance).

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
| **VS Code / Cursor extension** | [Marketplace](https://marketplace.visualstudio.com/items?itemName=wcalmels.resonance) · [packages/vscode](packages/vscode) |
| **Phi47 synergy** | [docs/SYNERGY.md](docs/SYNERGY.md) |
| Any terminal | `python -m resonance` |
| Cursor skill | `.cursor/skills/resonance/SKILL.md` |
| Claude Code | `CLAUDE.md` |
| Other AI agents | `AGENTS.md` |

### VS Code / Cursor

**[Install from Marketplace](https://marketplace.visualstudio.com/items?itemName=wcalmels.resonance)** — search **Resonance** in Extensions (`Ctrl+Shift+X`).

```bash
pip install resonance phi47-superpowers
```

Pair with **[Phi47 Superpowers](https://marketplace.visualstudio.com/items?itemName=wcalmels.phi47-superpowers)** for the quality pipeline.

Commands: **Resonance + Phi47: Generate Module with Quality Pipeline**, Generate Tests, Generate Module.

Details: [docs/SYNERGY.md](docs/SYNERGY.md) · [editors/README.md](editors/README.md)

---

## Documentation

| Document | Purpose |
|----------|---------|
| [paper/PAPER.md](paper/PAPER.md) | Full research paper |
| [docs/METHODOLOGY.md](docs/METHODOLOGY.md) | Evaluation protocol |
| [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) | Replication guide |
| [docs/ETHICS.md](docs/ETHICS.md) | Responsible use |
| [docs/ZENODO.md](docs/ZENODO.md) | Zenodo archive ([DOI](https://doi.org/10.5281/zenodo.20648248)) |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |

---

## Citation

```bibtex
@software{resonance2026,
  author  = {Calmels, W. and Resonance Contributors},
  title   = {Resonance: Task-Specialized LLM Orchestration with Minimal Context},
  year    = {2026},
  doi     = {10.5281/zenodo.20648248},
  url     = {https://github.com/wcalmels/resonance},
  version = {0.2.3},
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
