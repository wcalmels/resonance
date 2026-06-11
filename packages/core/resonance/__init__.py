"""Resonance — specialized AI bots with minimal token context."""

from resonance.bots import BOTS, MODEL
from resonance.context import ContextComparison, ContextSelector
from resonance.engine import BotResult, ProjectSpec, generate, run_bot

__all__ = [
    "BOTS",
    "MODEL",
    "BotResult",
    "ContextComparison",
    "ContextSelector",
    "ProjectSpec",
    "generate",
    "run_bot",
]

__version__ = "0.2.0"
