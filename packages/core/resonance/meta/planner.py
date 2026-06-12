"""Build a prioritized refinement plan under global budget."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from resonance.meta.features import FileSignals
from resonance.meta.policy_rules import MetaAction, MetaBudget, RuleBasedPolicy


@dataclass(frozen=True)
class PlannedRefinement:
    path: Path
    passes: int
    bot: str
    reason: str
    priority: float
    signals: FileSignals


def build_refinement_plan(
    items: list[tuple[Path, float, list, FileSignals]],
    policy: RuleBasedPolicy,
    budget: MetaBudget,
) -> list[PlannedRefinement]:
    """Return refinements sorted by priority; respect global pass budget."""
    candidates: list[PlannedRefinement] = []

    for path, _phi, _diags, signals in items:
        action = policy.decide(signals, budget)
        if not action.refine or action.passes <= 0:
            continue
        bot = action.bot or signals.bot
        candidates.append(
            PlannedRefinement(
                path=path,
                passes=action.passes,
                bot=bot,
                reason=action.reason,
                priority=action.priority,
                signals=signals,
            )
        )

    candidates.sort(key=lambda p: p.priority, reverse=True)

    plan: list[PlannedRefinement] = []
    reserved_passes = 0
    for item in candidates:
        if reserved_passes + item.passes > budget.max_total_passes:
            remaining = budget.max_total_passes - reserved_passes
            if remaining <= 0:
                break
            plan.append(
                PlannedRefinement(
                    path=item.path,
                    passes=remaining,
                    bot=item.bot,
                    reason=item.reason + "_truncated",
                    priority=item.priority,
                    signals=item.signals,
                )
            )
            break
        plan.append(item)
        reserved_passes += item.passes

    return plan
