# Resonance + Phi47 Synergy

Generate code with minimal tokens (Resonance), validate structure with IIT/Phi (Phi47).

> **New here?** Start with **[QUICKSTART.md](QUICKSTART.md)** — install, editor commands, CLI, and troubleshooting in one page.

## Install (Python)

```bash
pip install resonance phi47-superpowers
# or editable dev install:
pip install -e "packages/core[phi47]"
```

Set `ANTHROPIC_API_KEY` for generation.

## Install (VS Code / Cursor extensions)

| Extension | Marketplace | Role |
|-----------|-------------|------|
| [Phi47 Superpowers](https://marketplace.visualstudio.com/items?itemName=wcalmels.phi47-superpowers) | Published | Analyze Phi, inline diagnostics |
| [Resonance](https://marketplace.visualstudio.com/items?itemName=wcalmels.resonance) | Published | Generate code, pipeline |

Both extensions recommend each other when installed.

## Commands in the editor

| Palette command | Extension |
|-----------------|-----------|
| **Resonance + Phi47: Generate Module with Quality Pipeline** | Resonance |
| **Phi47 + Resonance: Generate Module with Quality Pipeline** | Phi47 |
| **Resonance: Generate Tests** | Resonance |
| **Phi47: Analyze Current File** | Phi47 |

## CLI pipeline

```bash
python -m resonance pipeline \
  --description "User authentication with JWT" \
  --output-dir output/auth \
  --phi-threshold 0.5
```

Or from Phi47:

```bash
phi47 pipeline "User authentication with JWT" -o output/auth
```

### Workflow

1. **Resonance** — 4 bots in parallel (minimal context)
2. **Phi47** — analyzes each file locally (~ms, no API cost)
3. **Resonance** — refines only files with low Phi (0–2 passes)

## Meta-reasoning (v0.2.3+)

The Python pipeline uses a **rule-based meta-policy** over Phi47 signals (Phi, fractal graph dimension, diagnostics) to decide **when** and **how much** to refine — skipping files that are already good and capping total refinement passes.

Logs: `~/.resonance/meta_runs.jsonl`

## Settings

| Setting | Extension | Default |
|---------|-----------|---------|
| `resonance.analyzeWithPhi47` | Resonance | `true` |
| `resonance.phiThreshold` | Resonance | `0.5` |
| `phi47.phiWarningThreshold` | Phi47 | `0.5` |
