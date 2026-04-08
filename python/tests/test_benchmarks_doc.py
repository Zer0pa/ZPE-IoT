from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARKS_PATH = REPO_ROOT / "BENCHMARKS.md"


def test_root_benchmarks_doc_has_methodology_and_commands() -> None:
    text = BENCHMARKS_PATH.read_text()

    assert "# ZPE-IoT Benchmarks" in text
    assert "## Methodology" in text
    assert "## Reproducibility" in text
    assert "validation/benchmarks/run_benchmarks.py" in text
    assert "docs/BENCHMARKS.md" in text
