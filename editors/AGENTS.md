# Resonance — instructions for AI agents (Codex, Copilot Workspace, etc.)

This repository uses **Resonance**: specialized bots with minimal token context.

## Before writing code

1. Read `packages/core/resonance/bots.py` for bot-specific rules
2. If working from an existing file, extract minimal context per task type:
   - Tests → signatures + imports only
   - API → route decorators + signatures only
   - Module → imports + class names from sample files
3. Run `python -m resonance context <file> --mode <mode> --compare` to verify token savings

## Bots

- **TestBot** — pytest, happy path + errors, no unnecessary mocks
- **APIBot** — FastAPI, Pydantic, HTTPException, type hints
- **DatabaseBot** — SQLAlchemy declarative models, indexes on FKs
- **CodeBot** — PEP 8 Python utilities with type hints

## Output format

- Return only executable Python code
- No markdown code fences in generated files
- No `TODO: implement` placeholders

## CLI (preferred for generation)

```bash
pip install -e packages/core
python -m resonance generate --bot TestBot --task "..." --file src/x.py --output tests/test_x.py
python -m resonance module --description "..." --output-dir output/feature
```

## Full documentation

- Architecture: `docs/ARCHITECTURE.md`
- Editor setup: `editors/README.md`
