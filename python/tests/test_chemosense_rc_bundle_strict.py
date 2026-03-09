from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "build_chemosense_rc_bundle.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("build_chemosense_rc_bundle", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_chemosense_rc_bundle"] = module
    spec.loader.exec_module(module)
    return module


def _write_dt_result(path: Path, *, strict: bool, results_count: int, mandatory_failures: int) -> None:
    payload = {
        "timestamp": "2026-02-20T00:00:00Z",
        "strict_gates": strict,
        "mandatory_failures": [
            {"dt": i + 1, "status": "FAIL", "name": f"DT-{i + 1:02d}"} for i in range(mandatory_failures)
        ],
        "results": [
            {"dt": i + 1, "name": f"DT-{i + 1:02d}", "priority": "P1", "status": "PASS", "output": "", "returncode": 0}
            for i in range(results_count)
        ],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_rc_bundle_uses_latest_full_strict_dt(tmp_path: Path) -> None:
    module = _load_module()

    results_dir = tmp_path / "validation" / "results"
    release_root = tmp_path / "release"
    results_dir.mkdir(parents=True)

    full_strict = results_dir / "dt_results_20260220T010101.json"
    partial_newer = results_dir / "dt_results_20260220T010102.json"
    _write_dt_result(full_strict, strict=True, results_count=27, mandatory_failures=0)
    _write_dt_result(partial_newer, strict=True, results_count=3, mandatory_failures=0)

    module.ROOT = tmp_path
    module.RESULTS_DIR = results_dir
    module.RELEASE_ROOT = release_root

    assert module.main() == 0

    rc_dirs = sorted(release_root.glob("RC_CHEMOSENSE_*"))
    assert len(rc_dirs) == 1
    rc_dir = rc_dirs[0]

    manifest = json.loads((rc_dir / "bundle_manifest.json").read_text(encoding="utf-8"))
    assert manifest["strict_dt_evidence"]["strict_gates"] is True
    assert manifest["strict_dt_evidence"]["results_count"] == 27
    assert manifest["strict_dt_evidence"]["mandatory_failures"] == 0
    assert Path(manifest["strict_dt_evidence"]["source"]).name == full_strict.name

    bundled_dt_files = sorted((rc_dir / "validation_results").glob("dt_results_*.json"))
    assert [path.name for path in bundled_dt_files] == [full_strict.name]


def test_rc_bundle_fails_without_full_strict_dt(tmp_path: Path) -> None:
    module = _load_module()

    results_dir = tmp_path / "validation" / "results"
    release_root = tmp_path / "release"
    results_dir.mkdir(parents=True)

    partial_only = results_dir / "dt_results_20260220T010102.json"
    _write_dt_result(partial_only, strict=True, results_count=3, mandatory_failures=0)

    module.ROOT = tmp_path
    module.RESULTS_DIR = results_dir
    module.RELEASE_ROOT = release_root

    assert module.main() == 1
    assert sorted(release_root.glob("RC_CHEMOSENSE_*")) == []
