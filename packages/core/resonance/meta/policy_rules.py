"""Rule-based meta-policy: decide if refinement is worth the cost."""

from __future__ import annotations

from dataclasses import dataclass

from resonance.meta.features import FileSignals


@dataclass
class MetaBudget:
    max_total_passes: int = 4
    max_tokens: int = 8000
    passes_used: int = 0
    tokens_used: int = 0

    def can_spend_passes(self, n: int = 1) -> bool:
        return self.passes_used + n <= self.max_total_passes

    def charge(self, passes: int = 1, tokens: int = 0) -> None:
        self.passes_used += passes
        self.tokens_used += tokens


@dataclass(frozen=True)
class MetaAction:
    refine: bool
    passes: int = 0
    bot: str | None = None
    reason: str = ""
    priority: float = 0.0


class RuleBasedPolicy:
    """Deterministic meta-reasoning over Phi47 + graph signals."""

    def __init__(self, phi_threshold: float = 0.5):
        self.phi_threshold = phi_threshold

    def decide(self, signals: FileSignals, budget: MetaBudget) -> MetaAction:
        if not budget.can_spend_passes():
            return MetaAction(False, reason="budget_passes")

        if budget.tokens_used >= budget.max_tokens:
            return MetaAction(False, reason="budget_tokens")

        priority = self._priority(signals)

        if signals.p000:
            return MetaAction(
                True,
                passes=1,
                bot=signals.bot,
                reason="syntax",
                priority=priority + 10.0,
            )

        if signals.phi >= self.phi_threshold and not signals.has_errors:
            return MetaAction(False, reason="phi_ok", priority=priority)

        if signals.p002_count >= 2 and signals.fractal_dim < 1.35:
            return MetaAction(
                True,
                passes=1,
                bot="CodeBot",
                reason="zombie_flat",
                priority=priority + 5.0,
            )

        if signals.has_errors:
            passes = 1 if signals.phi >= self.phi_threshold else 2
            return MetaAction(
                True,
                passes=min(passes, 2),
                bot=signals.bot,
                reason="errors",
                priority=priority + 3.0,
            )

        if signals.phi < self.phi_threshold:
            passes = 2 if signals.phi < 0.35 and signals.n_functions >= 6 else 1
            return MetaAction(
                True,
                passes=passes,
                bot=signals.bot,
                reason="low_phi",
                priority=priority + 1.0,
            )

        return MetaAction(False, reason="default", priority=priority)

    def should_stop_after_pass(
        self,
        signals: FileSignals,
        phi_before: float,
        phi_after: float,
    ) -> bool:
        if signals.p000 and phi_after > phi_before:
            return True
        if phi_after >= self.phi_threshold and not signals.has_errors:
            return True
        if phi_after <= phi_before + 0.01:
            return True
        return False

    def _priority(self, signals: FileSignals) -> float:
        score = (self.phi_threshold - signals.phi) * 10.0
        score += signals.error_count * 3.0
        score += signals.p002_count * 1.5
        score += max(0.0, 1.4 - signals.fractal_dim)
        return score
