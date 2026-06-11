# Architecture

## Monorepo layout (v0.2)

```
packages/core/resonance/   # bots, context, engine, CLI
packages/vscode/           # VS Code extension (calls CLI)
.cursor/skills/resonance/  # Cursor agent skill
editors/                   # AGENTS.md, CLAUDE.md for other tools
```

`ContextSelector` in `packages/core/resonance/context.py` is the **single source of truth** for token-saving context extraction. All editors use it via the CLI.

## Current state (v0.2)

The system is simple by design. No magic, no emergent behavior — just structured LLM calls with minimal context.

```
User request
    ↓
Task router (decides which bots to activate)
    ↓
Bot pool (specialized system prompts + Claude API)
    ↓ parallel async calls
Result combiner
    ↓
Files written to disk
```

### Components

**Task Router**
Parses the user request and selects which bots are relevant. Currently rule-based (keyword matching). Planned: use an LLM to route.

**Bot Pool**
Each bot is a system prompt + a call to Claude API. The "specialization" is entirely in the system prompt. This is simpler than it sounds but works well in practice.

**Result Combiner**
Takes outputs from multiple bots and merges them into coherent files. Currently simple concatenation with headers. Planned: LLM-based synthesis.

---

## Planned architecture (v0.4+)

```
Your computer
├── Bot engine (local Python process)
├── Encrypted bot configs (AES-256, your key)
├── Output directory
└── Sync agent
        ↓ HTTPS, zero-knowledge
Resonance cloud
├── Pattern aggregator (no code, no prompts — only stats)
└── Model improvement pipeline
```

### Zero-knowledge sync

The goal: bots improve over time using collective data without exposing your code or prompts.

What gets synced (planned):
- Task category (e.g. "generated REST endpoint")
- Success/failure signal (did the user accept or discard the output)
- Latency

What never leaves your machine:
- Your code
- Your prompts
- Your API key
- Bot configurations

This is not built yet. It requires careful design to verify the zero-knowledge property. We will publish the sync protocol for independent review before shipping it.

---

## What "Bot Factory" means

Bot Factory is a planned feature (v0.2) that lets you describe a new bot and generates its system prompt automatically. Essentially: use an LLM to write system prompts for other LLMs.

This is useful, not magical. The generated prompts need review. The value is speed, not quality beyond what you'd write yourself.

---

## What this is NOT

- Not a neural network architecture
- Not "resonance" in any physical sense
- Not emergent intelligence
- Not self-aware

It is: a well-structured wrapper around parallel LLM API calls with specialized prompts. That is genuinely useful. No need to oversell it.
