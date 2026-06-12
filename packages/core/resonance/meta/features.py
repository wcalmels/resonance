"""Extract structural signals per file for meta-reasoning."""

from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from resonance.meta.fractal import fractal_dimension


@dataclass
class FileSignals:
    path: str
    phi: float
    fractal_dim: float
    n_functions: int
    n_edges: int
    causal_density: float
    p000: bool
    p001_severity: str
    p002_count: int
    p003_max_complexity: int
    p007: bool
    error_count: int
    warning_count: int
    lines: int
    bot: str

    @property
    def has_errors(self) -> bool:
        return self.error_count > 0

    def to_dict(self) -> dict:
        return asdict(self)


def _extract_functions(tree: ast.AST) -> dict:
    funcs: dict = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        calls: list[str] = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        complexity = 1 + sum(
            1
            for n in ast.walk(node)
            if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler))
        )
        end = getattr(node, "end_lineno", node.lineno)
        funcs[node.name] = {
            "calls": list(set(calls)),
            "complexity": complexity,
            "lines": end - node.lineno,
        }
    return funcs


def _build_dep_matrix(funcs: dict) -> np.ndarray:
    names = list(funcs.keys())
    n = len(names)
    if n < 2:
        return np.zeros((2, 2))
    idx = {name: i for i, name in enumerate(names)}
    matrix = np.zeros((n, n), dtype=float)
    for name, data in funcs.items():
        i = idx[name]
        for callee in data["calls"]:
            if callee in idx:
                matrix[i, idx[callee]] = 1.0
    return matrix


def _p001_severity(diags) -> str:
    for d in diags:
        if d.code == "P001":
            return d.severity
    return "none"


def extract_file_signals(
    path: Path,
    diags,
    phi: float,
    bot: str,
) -> FileSignals:
    """Build signal vector from Phi47 diagnostics and local AST graph."""
    p000 = any(d.code == "P000" for d in diags)
    p002 = sum(1 for d in diags if d.code == "P002")
    p003 = 0
    for d in diags:
        if d.code != "P003":
            continue
        if "complexity=" in d.message:
            try:
                part = d.message.split("complexity=")[1].split()[0].rstrip(">")
                p003 = max(p003, int(part))
            except (IndexError, ValueError):
                p003 = max(p003, 1)
        else:
            p003 = max(p003, 1)
    p007 = any(d.code == "P007" for d in diags)
    errors = sum(1 for d in diags if d.severity == "error")
    warnings = sum(1 for d in diags if d.severity == "warning")

    lines = 0
    fractal_dim = 1.0
    n_functions = 0
    n_edges = 0
    causal_density = 0.0

    try:
        source = path.read_text(encoding="utf-8")
        lines = len(source.splitlines())
        tree = ast.parse(source, filename=str(path))
        funcs = _extract_functions(tree)
        matrix = _build_dep_matrix(funcs)
        n_functions = len(funcs)
        n_edges = int(np.sum(matrix > 0))
        n = matrix.shape[0]
        if n >= 2:
            causal_density = round(float(n_edges / (n * (n - 1) + 1e-10)), 4)
        fractal_dim = fractal_dimension(matrix)
    except (OSError, SyntaxError):
        p000 = True

    return FileSignals(
        path=str(path),
        phi=round(phi, 4),
        fractal_dim=fractal_dim,
        n_functions=n_functions,
        n_edges=n_edges,
        causal_density=causal_density,
        p000=p000,
        p001_severity=_p001_severity(diags),
        p002_count=p002,
        p003_max_complexity=p003,
        p007=p007,
        error_count=errors,
        warning_count=warnings,
        lines=lines,
        bot=bot,
    )
