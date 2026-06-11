# Roadmap

Honest, milestone-based. No dates until v0.1 is validated.

---

## v0.1 — Core (current)

- [x] CodeBot, APIBot, DatabaseBot, TestBot
- [x] Parallel async execution
- [x] CLI interface
- [x] Benchmarks script
- [ ] Stable enough to use daily

**Success criteria:** 10 people use it for a real project and find it useful.

---

## v0.2 — Bot Factory

- [ ] Describe a new bot in plain language → system prompt generated automatically
- [ ] Save and reuse custom bots
- [ ] Basic bot quality evaluation

**Success criteria:** User creates a custom bot without editing code.

---

## v0.3 — Local persistence

- [ ] Encrypted local storage for bot configs
- [ ] Usage history
- [ ] Simple self-improvement: flag outputs as good/bad, adjust prompts

**Success criteria:** Bot quality improves after 50 uses based on feedback.

---

## v0.4 — Cloud sync (zero-knowledge)

- [ ] Design and publish sync protocol
- [ ] Independent security review
- [ ] Optional opt-in sync
- [ ] Pattern aggregation (no code, no prompts)

**Success criteria:** Protocol reviewed externally. Users can verify what is and isn't sent.

---

## v0.5 — SaaS

- [ ] Web UI
- [ ] User accounts
- [ ] Subscription billing
- [ ] Network effects pricing (price drops as subscriber count grows)

**Success criteria:** First 100 paying users.

---

## v1.0 — Public launch

- [ ] Stable API
- [ ] Editor integration (VS Code extension)
- [ ] Documentation complete
- [ ] Onboarding flow

**Success criteria:** Product Hunt launch, 1000 users in first month.

---

## Not on the roadmap

Things that were discussed but are not planned because they are either technically unsound or premature:

- "Emergent superintelligence" — not a real engineering target
- $720M ARR projections — not useful until there is revenue
- Quantum/resonance computation — metaphor, not mechanism

These may be revisited if the core product validates and the right technical path becomes clear.
