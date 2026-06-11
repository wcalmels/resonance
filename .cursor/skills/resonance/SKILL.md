---
name: resonance
description: >-
  Runs specialized code-generation bots (TestBot, APIBot, DatabaseBot, CodeBot)
  with minimal token context. Use when generating tests, API endpoints, database
  models, or full modules; when the user mentions Resonance, token savings, or
  wants boilerplate without sending entire files to the model.
---

# Resonance

## Token-saving rule (always apply)

Before generating code from an existing file, extract **minimal context** instead of sending the full file:

| Task | Send | Skip |
|------|------|------|
| Tests | `def`/`class` signatures, imports | Function bodies |
| API endpoint | Imports, `@app`/`@router` decorators, route signatures | Business logic bodies |
| New module | Imports and class names from 1–2 sample files | Everything else |
| Bug fix | ±30 lines around the error | Rest of file |

CLI to measure savings:

```bash
python -m resonance context path/to/file.py --mode tests --compare
```

Typical savings: **60–80% fewer input tokens** vs full-file context.

## Bots

Use the bot that matches the task. Each bot has a focused system prompt in `packages/core/resonance/bots.py`.

| Bot | Use for |
|-----|---------|
| TestBot | pytest suites for existing code |
| APIBot | FastAPI endpoints, Pydantic models |
| DatabaseBot | SQLAlchemy models and migrations |
| CodeBot | Helper utilities, pure Python logic |

Output rules for all bots:
- Production-ready Python only
- Type hints and docstrings
- Return **only code**, no markdown fences
- No placeholder `TODO` comments

## Workflows

### Single bot (terminal, any editor)

```bash
pip install -e packages/core
python -m resonance generate \
  --bot TestBot \
  --task "Generate pytest tests for each public function" \
  --file src/my_module.py \
  --output tests/test_my_module.py
```

`--file` auto-selects the right context mode. Override with `--mode tests|endpoint|module|bugfix`.

### Full module (parallel)

```bash
python -m resonance module \
  --description "User auth with JWT — register, login, me endpoint" \
  --requirement "bcrypt passwords" \
  --requirement "JWT access tokens" \
  --output-dir output/auth
```

Runs DatabaseBot, APIBot, TestBot, and CodeBot in parallel.

### Inside Cursor (no API key needed)

When the user pays for Cursor (not per-token API):

1. Read only minimal context using the table above
2. Apply the matching bot's rules from `bots.py`
3. Write output directly to the requested file
4. Mention estimated token savings if you skipped file bodies

### Other editors

- **VS Code**: install extension from `packages/vscode` (calls the same CLI)
- **Neovim / Emacs / JetBrains**: run the CLI from a terminal or task
- **Codex / Claude Code / Windsurf**: read `editors/AGENTS.md` or `editors/CLAUDE.md`

## When NOT to use minimal context

- Refactoring that requires reading full implementations
- Debugging subtle logic bugs (use `--mode bugfix --line N` or full file)
- Security-sensitive code review

## Reference

- Bot prompts: `packages/core/resonance/bots.py`
- Context logic: `packages/core/resonance/context.py`
- Architecture: `docs/ARCHITECTURE.md`
