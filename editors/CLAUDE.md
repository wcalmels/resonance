# Resonance — instructions for Claude Code

## Project summary

Resonance orchestrates specialized code-generation bots with **minimal context** to reduce API token usage by 60–80%.

Core package: `packages/core/resonance/`

## Commands you can run

```bash
# Compare token savings before generating
python -m resonance context path/to/file.py --mode tests --compare

# Generate with auto-extracted context
python -m resonance generate --bot TestBot --task "..." --file path/to/file.py --output tests/test_file.py

# Full module (4 bots in parallel)
python -m resonance module --description "..." --output-dir output/name
```

## Context modes

| Mode | When |
|------|------|
| `tests` | Generating pytest from existing module |
| `endpoint` | Adding FastAPI route matching project style |
| `module` | New code matching import/class patterns |
| `bugfix` | Fix at line N — sends ±30 lines only |

## Bot selection

Pick **one** bot per task. Prompts are in `packages/core/resonance/bots.py`.

When editing directly (without CLI), follow the same bot rules and minimal-context table in `.cursor/skills/resonance/SKILL.md`.

## Do not

- Send entire files when signatures suffice
- Mix bot responsibilities in one response
- Add markdown fences inside `.py` output files
