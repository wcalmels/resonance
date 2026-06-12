"""Append-only JSONL log for meta-reasoning decisions (training data for phase B)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

_DEFAULT_LOG = Path.home() / ".resonance" / "meta_runs.jsonl"


def log_meta_decision(
    *,
    output_dir: str,
    path: str,
    action: dict,
    signals: dict,
    phi_before: float,
    phi_after: float | None = None,
    refinements: int = 0,
    log_path: Path | None = None,
) -> None:
    target = log_path or _DEFAULT_LOG
    target.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "output_dir": output_dir,
        "path": path,
        "action": action,
        "signals": signals,
        "phi_before": phi_before,
        "phi_after": phi_after,
        "refinements": refinements,
    }
    with target.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
