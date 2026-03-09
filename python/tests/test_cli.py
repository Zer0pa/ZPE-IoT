from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from click.testing import CliRunner

from zpe_iot.cli import main


def _write_numeric_csv(path: Path, n: int = 512) -> np.ndarray:
    t = np.linspace(0.0, 8.0 * np.pi, n)
    values = np.sin(t) + 0.1 * np.cos(3.0 * t)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["index", "value"])
        for i, v in enumerate(values.tolist()):
            w.writerow([i, f"{v:.12g}"])
    return values


def test_cli_smoke_paths(tmp_path: Path) -> None:
    runner = CliRunner()

    input_csv = tmp_path / "input.csv"
    original = _write_numeric_csv(input_csv)
    packet = tmp_path / "packet.zpk"
    restored_csv = tmp_path / "restored.csv"

    compress = runner.invoke(
        main,
        ["compress", str(input_csv), "--preset", "generic", "--output", str(packet)],
    )
    assert compress.exit_code == 0, compress.output
    assert packet.exists()
    assert "Compression ratio:" in compress.output

    info = runner.invoke(main, ["info", str(packet)])
    assert info.exit_code == 0, info.output
    payload = json.loads(info.output)
    assert payload["sample_count"] == len(original)
    assert payload["packed_size"] > 0

    decompress = runner.invoke(main, ["decompress", str(packet), "--output", str(restored_csv)])
    assert decompress.exit_code == 0, decompress.output
    assert restored_csv.exists()

    restored = np.loadtxt(restored_csv, delimiter=",", skiprows=1, usecols=[1], dtype=np.float64)
    assert restored.shape[0] == original.shape[0]
    assert np.isfinite(restored).all()

    benchmark = runner.invoke(
        main,
        ["benchmark", str(input_csv), "--compare", "zlib", "--preset", "generic"],
    )
    assert benchmark.exit_code == 0, benchmark.output
    assert "zpe-iot CR:" in benchmark.output
    assert "NRMSE(window-normalized)" in benchmark.output
    assert "zlib CR:" in benchmark.output


def test_cli_missing_numeric_column_errors(tmp_path: Path) -> None:
    runner = CliRunner()
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("a,b,c\nx,y,z\nno,numbers,here\n", encoding="utf-8")
    packet = tmp_path / "bad.zpk"

    res = runner.invoke(main, ["compress", str(bad_csv), "--output", str(packet)])
    assert res.exit_code != 0
    assert "No numeric data found in input CSV" in res.output


def test_cli_malformed_packet_fails(tmp_path: Path) -> None:
    runner = CliRunner()
    bad_packet = tmp_path / "bad.zpk"
    bad_packet.write_bytes(b"bad-packet")

    out_csv = tmp_path / "out.csv"
    res = runner.invoke(main, ["decompress", str(bad_packet), "--output", str(out_csv)])
    assert res.exit_code != 0


def test_cli_json_mode_and_diagnostics(tmp_path: Path) -> None:
    runner = CliRunner()
    input_csv = tmp_path / "input.csv"
    _write_numeric_csv(input_csv, n=256)
    packet = tmp_path / "packet.zpk"

    compress = runner.invoke(
        main,
        [
            "compress",
            str(input_csv),
            "--output",
            str(packet),
            "--chunk-size",
            "64",
            "--json",
        ],
    )
    assert compress.exit_code == 0, compress.output
    payload = json.loads(compress.output)
    assert payload["command"] == "compress"
    assert payload["chunk_size"] == 64
    assert payload["exit_code"] == 0

    info = runner.invoke(main, ["info", str(packet), "--json"])
    assert info.exit_code == 0, info.output
    info_payload = json.loads(info.output)
    assert info_payload["command"] == "info"
    assert info_payload["sample_count"] == 256

    diag = runner.invoke(main, ["diagnostics", "--json"])
    assert diag.exit_code == 0, diag.output
    diag_payload = json.loads(diag.output)
    assert diag_payload["command"] == "diagnostics"
    assert "native_available" in diag_payload
    assert "chemosense_available" in diag_payload


def test_cli_chemosense_smoke_json() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["chemosense-smoke", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["command"] == "chemosense-smoke"
    assert payload["smell_stroke_count"] == 2
    assert payload["taste_event_count"] == 2
    assert payload["touch_stroke_count"] == 2
    assert payload["mental_stroke_count"] == 2
    assert payload["fused_event_count"] == 2
    assert payload["touch_placeholder_removed"] is True


def test_module_execution_chemosense_smoke_json() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "zpe_iot.cli", "chemosense-smoke", "--json"],
        cwd=str(Path(__file__).resolve().parents[1]),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout.strip())
    assert payload["command"] == "chemosense-smoke"
    assert payload["touch_stroke_count"] == 2
    assert payload["mental_stroke_count"] == 2
    assert payload["fused_event_count"] == 2


def test_cli_runtime_error_and_usage_error_exit_codes(tmp_path: Path) -> None:
    runner = CliRunner()
    input_csv = tmp_path / "input.csv"
    _write_numeric_csv(input_csv, n=128)

    runtime = runner.invoke(
        main,
        ["benchmark", str(input_csv), "--compare", "unknown", "--preset", "generic"],
    )
    assert runtime.exit_code == 1
    assert "Unknown comparator: unknown" in runtime.output

    usage = runner.invoke(main, ["compress", str(input_csv)])
    assert usage.exit_code == 2
