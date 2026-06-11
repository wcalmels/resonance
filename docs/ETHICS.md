# Ethics and Responsible Use

## Intended use

Resonance is a research and engineering tool for:

- Accelerating repetitive software development tasks
- Studying token-efficient LLM orchestration
- Teaching multi-agent LLM system design

## Prohibited use

Do not use Resonance to:

- Generate malware, exploits, or tools for unauthorized access
- Produce code that intentionally violates software licenses
- Automate decisions in safety-critical systems without human review
- Misrepresent AI-generated code as human-authored in academic submissions without disclosure

## Human oversight

All generated code must be reviewed by a qualified developer before deployment. Resonance outputs are **drafts**, not certified artifacts.

## Data and privacy

- Source code processed locally stays on the user's machine except for API payloads sent to the LLM provider.
- Users are responsible for compliance with organizational data policies before sending context to external APIs.
- Do not commit `.env` files or API keys to version control.

## Research integrity

When publishing results:

- Distinguish offline token estimates from API-reported token counts
- Report model name and version
- Disclose estimated API cost for benchmarks
- Do not claim physical "resonance" mechanisms — the name is branding only

## Reporting

Report security vulnerabilities via GitHub Security Advisories or repository issues marked `security`.
