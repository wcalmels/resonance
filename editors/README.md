# Editor integrations

Resonance is **editor-agnostic**. The core lives in `packages/core` and every integration calls the same CLI.

## Quick setup (all editors)

```bash
cd resonance
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e packages/core
cp .env.example .env   # add ANTHROPIC_API_KEY
```

## By editor

| Editor | Integration |
|--------|-------------|
| **Cursor** | `.cursor/skills/resonance/SKILL.md` — agent uses minimal context automatically |
| **VS Code** | `packages/vscode` extension — Command Palette → "Resonance:" |
| **Claude Code** | `editors/CLAUDE.md` at repo root or symlink |
| **Codex / OpenAI** | `editors/AGENTS.md` |
| **Neovim / Emacs** | Shell command or `:!'python -m resonance ...'` |
| **JetBrains** | External Tool → `python -m resonance generate ...` |
| **Any terminal** | `python -m resonance --help` |

## Token savings (how it works)

1. `ContextSelector` strips file bodies and keeps signatures/imports
2. Each bot gets a **small, focused** system prompt (not a general assistant)
3. You run **one bot** per task instead of a long multi-turn chat

Check savings before calling the API:

```bash
python -m resonance context myfile.py --mode tests --compare --show
```
