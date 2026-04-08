from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARKS_PATH = REPO_ROOT / "BENCHMARKS.md"


def test_root_benchmarks_doc_has_phase3_tables() -> None:
    text = BENCHMARKS_PATH.read_text()

    assert "Phase 3 verification rerun" in text
    assert "| Dataset | Domain | Raw bytes | ZPE bytes | ZPE CR | Fidelity (NRMSE) | Source |" in text
    assert (
        "| Dataset | Best baseline | Baseline bytes | Baseline CR | ZPE bytes | ZPE CR | Improvement vs baseline | Winner |"
        in text
    )
    assert "validation/results/bench_summary_E1_real_public_20260408T043806.json" in text
    assert "DS-01" in text
    assert "DS-12" in text
    assert "blocked pending a public downloadable EnOcean sensor trace dataset" in text
