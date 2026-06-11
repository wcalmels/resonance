"""Resonance — specialized AI bots with minimal token context."""

from resonance.bots import BOTS, MODEL
from resonance.context import ContextComparison, ContextSelector
from resonance.engine import BotResult, ProjectSpec, generate, run_bot
from resonance.phi47_bridge import PipelineReport, run_pipeline, run_pipeline_sync

__all__ = [
    "BOTS",
    "MODEL",
    "BotResult",
    "ContextComparison",
    "ContextSelector",
    "ProjectSpec",
    "PipelineReport",
    "generate",
    "run_bot",
    "run_pipeline",
    "run_pipeline_sync",
]

__version__ = "0.2.0"
