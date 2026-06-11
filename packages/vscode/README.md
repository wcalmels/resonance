# Resonance VS Code Extension

Thin wrapper around the shared `resonance` CLI in `packages/core`.

## Prerequisites

```bash
pip install -e ../core
export ANTHROPIC_API_KEY=sk-ant-...
```

## Install (development)

1. Open `packages/vscode` in VS Code
2. Press F5 to launch Extension Development Host
3. Or package: `npx @vscode/vsce package`

## Commands

- **Resonance: Generate Tests** — minimal context (`tests` mode)
- **Resonance: Generate API Endpoint**
- **Resonance: Generate Module** — all 4 bots in parallel
- **Resonance: Show Token Usage Stats**

## Settings

| Setting | Description |
|---------|-------------|
| `resonance.apiKey` | Anthropic API key |
| `resonance.pythonPath` | Python with `resonance` installed (default: `python`) |
| `resonance.showTokenStats` | Show savings notification after generation |
