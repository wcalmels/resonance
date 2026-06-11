# Resonance + Phi47 Synergy

## Install both

```bash
pip install -e "packages/core[phi47]"
# or separately:
pip install -e packages/core
pip install phi47-superpowers
```

## Pipeline command

```bash
py -3 -m resonance pipeline \
  --description "User authentication with JWT — register, login, me" \
  --requirement "bcrypt passwords" \
  --output-dir output/auth \
  --phi-threshold 0.5
```

### What it does

1. **Resonance** — 4 bots in parallel (minimal context, fast)
2. **Phi47** — analyzes each file locally (milliseconds, no API cost)
3. **Resonance** — refines only files with low Phi or errors (0–2 passes)

### Options

| Flag | Default | Meaning |
|------|---------|---------|
| `--phi-threshold` | 0.5 | Minimum Phi per file |
| `--max-refinements` | 2 | Max API refine passes per weak file |
| `--strict` | off | Exit code 2 if system Phi still below threshold |
| `--json` | off | Machine-readable report |

### From Phi47

```bash
phi47 analyze output/auth/
```

Use as pre-commit gate after generation.
