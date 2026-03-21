#!/usr/bin/env python3
"""Shared runtime/tool discovery for repo-local release and verification scripts."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_PROJECT_ROOT = ROOT / "python"


def _script_dir_name() -> str:
    return "Scripts" if os.name == "nt" else "bin"


def _python_names() -> tuple[str, ...]:
    return ("python.exe", "python") if os.name == "nt" else ("python3", "python")


def _tool_names(name: str) -> tuple[str, ...]:
    return (f"{name}.exe", name) if os.name == "nt" else (name,)


def _dedupe(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in paths:
        resolved = path.expanduser()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def candidate_python_paths() -> list[Path]:
    candidates: list[Path] = []

    override = os.environ.get("ZPE_IOT_PYTHON")
    if override:
        candidates.append(Path(override))

    if sys.executable:
        candidates.append(Path(sys.executable))

    script_dir = _script_dir_name()
    for base in (PYTHON_PROJECT_ROOT / ".venv", ROOT / ".venv"):
        for name in _python_names():
            candidates.append(base / script_dir / name)

    for name in _python_names():
        discovered = shutil.which(name)
        if discovered:
            candidates.append(Path(discovered))

    return _dedupe(candidates)


def python_executable() -> Path:
    for candidate in candidate_python_paths():
        if candidate.exists():
            return candidate
    raise RuntimeError("no usable Python interpreter found for the ZPE-IoT release surface")


def environment_root() -> Path:
    prefix = Path(sys.prefix)
    if prefix.exists():
        return prefix
    return python_executable().parent.parent


def tool_path(name: str) -> Path | None:
    candidates: list[Path] = []
    script_dir = _script_dir_name()
    python_bin_dir = python_executable().parent

    for variant in _tool_names(name):
        candidates.append(python_bin_dir / variant)
        candidates.append(environment_root() / script_dir / variant)
        discovered = shutil.which(variant)
        if discovered:
            candidates.append(Path(discovered))

    for candidate in _dedupe(candidates):
        if candidate.exists():
            return candidate
    return None


def tool_command(name: str) -> str:
    path = tool_path(name)
    return str(path) if path is not None else name
