# Resonance

Specialized AI bots for **token-efficient** Python code generation. Uses minimal context (60–80% fewer input tokens) and parallel bot orchestration.

Works in **VS Code** and **Cursor**. Integrates with **[Phi47 Superpowers](https://marketplace.visualstudio.com/items?itemName=wcalmels.phi47-superpowers)** for structural quality analysis.

## Features

- **Generate Tests** — pytest with minimal context (signatures only)
- **Generate API Endpoint** — FastAPI from route patterns
- **Generate Module** — 4 bots in parallel (models, API, tests, utilities)
- **Resonance + Phi47 Pipeline** — generate, analyze Phi, refine weak files
- Token usage stats

## Requirements

```bash
pip install resonance
# For Phi47 pipeline integration:
pip install "resonance[phi47]"
# or: pip install phi47-superpowers
```

Set your Anthropic API key:

- VS Code Settings → `resonance.apiKey`, or
- Environment variable `ANTHROPIC_API_KEY`

## Commands

| Command | Description |
|---------|-------------|
| **Resonance + Phi47: Generate Module with Quality Pipeline** | Full synergy workflow |
| **Resonance: Generate Module** | 4 parallel bots |
| **Resonance: Generate Tests** | Tests for current file |
| **Resonance: Generate API Endpoint** | New FastAPI route |
| **Resonance: Show Token Usage Stats** | Session token savings |

## Phi47 integration

Install both extensions:

1. **Resonance** (this extension) — generates code
2. **Phi47 Superpowers** — measures structural Phi (IIT 4.0)

After generation, Resonance can auto-trigger Phi47 analysis. Use the **Pipeline** command for generate → analyze → refine.

## Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `resonance.apiKey` | — | Anthropic API key |
| `resonance.pythonPath` | auto | Python with `resonance` installed |
| `resonance.analyzeWithPhi47` | `true` | Analyze output with Phi47 after generate |
| `resonance.phiThreshold` | `0.5` | Phi threshold for pipeline refinement |

## Research

- Paper: [github.com/wcalmels/resonance/paper/PAPER.md](https://github.com/wcalmels/resonance/blob/main/paper/PAPER.md)
- DOI: [10.5281/zenodo.20648248](https://doi.org/10.5281/zenodo.20648248)

## License

MIT
