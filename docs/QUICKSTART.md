# Resonance + Phi47 — Quick Start

Unified guide for the **generate → analyze → refine** stack. Works in VS Code, Cursor, or any terminal.

| Component | Role | Marketplace |
|-----------|------|-------------|
| [Resonance](https://github.com/wcalmels/resonance) | Token-efficient code generation (4 parallel bots) | [wcalmels.resonance](https://marketplace.visualstudio.com/items?itemName=wcalmels.resonance) |
| [Phi47 Superpowers](https://github.com/wcalmels/phi47-superpowers) | Structural quality via Phi (IIT 4.0), local, no API | [wcalmels.phi47-superpowers](https://marketplace.visualstudio.com/items?itemName=wcalmels.phi47-superpowers) |

---

## 1. Install (5 minutes)

### Extensions (VS Code / Cursor)

1. `Ctrl+Shift+X` → install **Resonance** and **Phi47 Superpowers**
2. Both extensions recommend each other automatically

### Python packages

```bash
pip install resonance phi47-superpowers
```

Windows if `python` is not on PATH:

```bash
py -3 -m pip install resonance phi47-superpowers
```

### API key (generation only)

Phi47 analysis is **fully local**. Resonance generation needs one LLM provider:

```bash
# .env or environment
export ANTHROPIC_API_KEY=sk-ant-...
```

---

## 2. Editor workflow

1. Open a Python workspace
2. `Ctrl+Shift+P` → run either command:
   - **Resonance + Phi47: Generate Module with Quality Pipeline**
   - **Phi47 + Resonance: Generate Module with Quality Pipeline**
3. Enter a module description (e.g. `User authentication with JWT`)
4. Choose an output folder

### What happens

```
Resonance (4 bots, minimal context)
        ↓
Phi47 (Phi analysis, ~ms per file, no API cost)
        ↓
Resonance (refine only low-Phi files, 0–2 passes)
```

### Other useful commands

| Command | Extension |
|---------|-----------|
| Resonance: Generate Tests | Resonance |
| Resonance: Generate Module | Resonance |
| Phi47: Analyze Current File | Phi47 |
| Phi47: Analyze Workspace | Phi47 |
| Phi47: Show Phi Report | Phi47 |

---

## 3. CLI workflow

### Full pipeline

```bash
# Resonance entry point
python -m resonance pipeline \
  --description "User authentication with JWT" \
  --output-dir output/auth \
  --phi-threshold 0.5

# Phi47 entry point (same workflow)
phi47 pipeline "User authentication with JWT" -o output/auth
```

### Phi47 only (no generation)

```bash
phi47 analyze mycode.py
phi47 analyze .
```

### Resonance only (no Phi refinement)

```bash
python -m resonance generate \
  --bot TestBot \
  --task "pytest suite for public functions" \
  --file examples/sample_module.py \
  --output output/test_sample.py
```

---

## 4. Settings

| Setting | Extension | Default | Purpose |
|---------|-----------|---------|---------|
| `resonance.analyzeWithPhi47` | Resonance | `true` | Run Phi after generation |
| `resonance.phiThreshold` | Resonance | `0.5` | Refine files below this Phi |
| `phi47.pythonPath` | Phi47 | auto | Python with packages installed |
| `phi47.phiWarningThreshold` | Phi47 | `0.5` | Editor warning threshold |
| `phi47.enableOnSave` | Phi47 | `true` | Analyze on save |

---

## 5. Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named phi47` | `pip install phi47-superpowers` |
| `No module named resonance` | `pip install resonance` |
| Phi47 command not found in palette | Update extension to **v0.1.3+** from Marketplace |
| Pipeline command missing | Install **both** extensions from Marketplace |
| Wrong Python | Set `phi47.pythonPath` to your venv Python |

---

## 6. Learn more

| Resource | Link |
|----------|------|
| Resonance paper & DOI | [paper/PAPER.md](../paper/PAPER.md) · [10.5281/zenodo.20648248](https://doi.org/10.5281/zenodo.20648248) |
| Phi47 paper | [phi47-superpowers/paper](https://github.com/wcalmels/phi47-superpowers/tree/main/paper) |
| Synergy details | [docs/SYNERGY.md](SYNERGY.md) |
| Offline token benchmark | `python benchmarks/benchmark_context.py` |
| Pipeline performance benchmark | `pip install phi47-superpowers && python benchmarks/benchmark_pipeline.py` |

---

**Release:** Phi47 v0.1.3 + Resonance v0.2.2 (Python) / v0.2.1 (Marketplace extension).
