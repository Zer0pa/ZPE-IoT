from __future__ import annotations

import csv
import json
import os
import platform
import sys
from pathlib import Path

import click
import numpy as np

from . import _native
from .codec import EncodedStream, Mode, compute_nrmse, decode, encode

RUNTIME_ERROR_EXIT_CODE = 1


class RuntimeDataError(click.ClickException):
    exit_code = RUNTIME_ERROR_EXIT_CODE


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """zpe-iot CLI.

    Examples:
      zpe-iot compress input.csv --preset vibration --output out.zpk
      zpe-iot info out.zpk
      zpe-iot decompress out.zpk --output restored.csv
      zpe-iot benchmark input.csv --compare zstd,lz4,zlib
      zpe-iot diagnostics --json
    """


def _iter_csv_numeric(path: Path):
    with path.open("r", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            for cell in reversed(row):
                try:
                    yield float(cell)
                    break
                except ValueError:
                    continue


def _read_csv_values(path: Path, chunk_size: int) -> np.ndarray:
    if chunk_size <= 0:
        raise RuntimeDataError("chunk_size must be > 0")

    chunks: list[np.ndarray] = []
    chunk: list[float] = []

    for value in _iter_csv_numeric(path):
        chunk.append(value)
        if len(chunk) >= chunk_size:
            chunks.append(np.asarray(chunk, dtype=np.float64))
            chunk = []

    if chunk:
        chunks.append(np.asarray(chunk, dtype=np.float64))

    if not chunks:
        raise RuntimeDataError("No numeric data found in input CSV")

    if len(chunks) == 1:
        return chunks[0]
    return np.concatenate(chunks).astype(np.float64, copy=False)


def _write_csv_values(path: Path, values: np.ndarray, chunk_size: int = 100_000) -> None:
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["index", "value"])
        n = int(len(values))
        for start in range(0, n, max(1, int(chunk_size))):
            end = min(n, start + max(1, int(chunk_size)))
            for i in range(start, end):
                writer.writerow([i, f"{float(values[i]):.12g}"])


def _emit(payload: dict, as_json: bool, lines: list[str]) -> None:
    if as_json:
        click.echo(json.dumps(payload, sort_keys=True))
        return
    for line in lines:
        click.echo(line)


def _zpe_metrics(samples: np.ndarray, preset: str) -> dict:
    stream = encode(samples, preset=preset)
    packet = stream.to_bytes()
    restored = decode(packet)
    return {
        "compression_ratio": float(stream.compression_ratio),
        "nrmse": float(compute_nrmse(samples, restored)),
        "nrmse_label": "NRMSE(window-normalized)",
        "packed_size": int(len(packet)),
        "sample_count": int(stream.sample_count),
    }


@main.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path))
@click.option("--preset", default="generic", show_default=True, help="Sensor preset")
@click.option("--output", required=True, type=click.Path(path_type=Path), help="Output .zpk path")
@click.option("--mode", type=click.Choice([m.value for m in Mode]), help="Override mode")
@click.option("--threshold", type=float, help="Override threshold")
@click.option("--step", type=float, help="Override quantisation step")
@click.option("--adaptive/--no-adaptive", default=True, help="Enable adaptive threshold")
@click.option("--chunk-size", default=100_000, show_default=True, type=int, help="CSV rows per parse chunk")
@click.option("--json", "as_json", is_flag=True, help="Emit machine-readable JSON")
def compress(
    input: Path,
    preset: str,
    output: Path,
    mode: str | None,
    threshold: float | None,
    step: float | None,
    adaptive: bool,
    chunk_size: int,
    as_json: bool,
) -> None:
    """Compress a CSV file into packet bytes (.zpk)."""
    try:
        samples = _read_csv_values(input, chunk_size=chunk_size)
        kwargs: dict[str, object] = {"adaptive": adaptive}
        if mode is not None:
            kwargs["mode"] = mode
        if threshold is not None:
            kwargs["threshold"] = threshold
        if step is not None:
            kwargs["step"] = step

        stream = encode(samples, preset=preset, **kwargs)
        packet = stream.to_bytes()
        output.write_bytes(packet)

        payload = {
            "command": "compress",
            "input": str(input),
            "output": str(output),
            "sample_count": int(stream.sample_count),
            "packed_size": int(len(packet)),
            "compression_ratio": float(stream.compression_ratio),
            "preset": preset,
            "mode": stream.mode.value,
            "chunk_size": int(chunk_size),
            "native_available": bool(_native.available()),
            "exit_code": 0,
        }
        _emit(
            payload,
            as_json,
            [
                f"Wrote {output}",
                f"Samples: {stream.sample_count}",
                f"Packed size: {len(packet)} bytes",
                f"Compression ratio: {stream.compression_ratio:.2f}x",
            ],
        )
    except click.ClickException:
        raise
    except Exception as exc:  # pragma: no cover - defensive runtime surfacing
        raise RuntimeDataError(str(exc)) from exc


@main.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path))
@click.option("--output", required=True, type=click.Path(path_type=Path), help="Output CSV path")
@click.option("--chunk-size", default=100_000, show_default=True, type=int, help="CSV rows per write chunk")
@click.option("--json", "as_json", is_flag=True, help="Emit machine-readable JSON")
def decompress(input: Path, output: Path, chunk_size: int, as_json: bool) -> None:
    """Decompress packet bytes (.zpk) into CSV."""
    try:
        packet = input.read_bytes()
        restored = decode(packet)
        _write_csv_values(output, restored, chunk_size=chunk_size)

        payload = {
            "command": "decompress",
            "input": str(input),
            "output": str(output),
            "recovered_samples": int(len(restored)),
            "chunk_size": int(chunk_size),
            "native_available": bool(_native.available()),
            "exit_code": 0,
        }
        _emit(payload, as_json, [f"Wrote {output}", f"Recovered {len(restored)} samples"])
    except click.ClickException:
        raise
    except Exception as exc:
        raise RuntimeDataError(str(exc)) from exc


@main.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path))
@click.option("--compare", default="zstd,lz4,zlib", show_default=True, help="Comma-separated baselines")
@click.option("--preset", default="generic", show_default=True, help="Sensor preset")
@click.option("--chunk-size", default=100_000, show_default=True, type=int, help="CSV rows per parse chunk")
@click.option("--json", "as_json", is_flag=True, help="Emit machine-readable JSON")
def benchmark(input: Path, compare: str, preset: str, chunk_size: int, as_json: bool) -> None:
    """Benchmark zpe-iot vs selected compressors on one CSV input."""
    try:
        samples = _read_csv_values(input, chunk_size=chunk_size)
        zpe = _zpe_metrics(samples, preset=preset)

        comparators: dict[str, dict[str, object]] = {}
        raw = samples.astype(np.float64).tobytes()
        names = [c.strip().lower() for c in compare.split(",") if c.strip()]
        for name in names:
            if name == "zlib":
                import zlib

                comp = zlib.compress(raw, level=6)
                comparators[name] = {"compression_ratio": float(len(raw) / max(1, len(comp))), "status": "OK"}
            elif name == "zstd":
                try:
                    import zstandard as zstd
                except Exception:
                    comparators[name] = {"status": "SKIPPED_DEP_MISSING"}
                    continue
                comp = zstd.ZstdCompressor(level=3).compress(raw)
                comparators[name] = {"compression_ratio": float(len(raw) / max(1, len(comp))), "status": "OK"}
            elif name == "lz4":
                try:
                    import lz4.frame
                except Exception:
                    comparators[name] = {"status": "SKIPPED_DEP_MISSING"}
                    continue
                comp = lz4.frame.compress(raw)
                comparators[name] = {"compression_ratio": float(len(raw) / max(1, len(comp))), "status": "OK"}
            else:
                raise RuntimeDataError(f"Unknown comparator: {name}")

        payload = {
            "command": "benchmark",
            "input": str(input),
            "preset": preset,
            "chunk_size": int(chunk_size),
            "native_available": bool(_native.available()),
            "zpe_iot": zpe,
            "comparators": comparators,
            "exit_code": 0,
        }

        lines = [
            f"zpe-iot CR: {zpe['compression_ratio']:.2f}x",
            f"zpe-iot {zpe['nrmse_label']}: {zpe['nrmse']:.4f}",
        ]
        for name, metrics in comparators.items():
            if metrics.get("status") != "OK":
                lines.append(f"{name}: {metrics['status']}")
                continue
            lines.append(f"{name} CR: {float(metrics['compression_ratio']):.2f}x")
        _emit(payload, as_json, lines)
    except click.ClickException:
        raise
    except Exception as exc:
        raise RuntimeDataError(str(exc)) from exc


@main.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path))
@click.option("--json", "as_json", is_flag=True, help="Emit machine-readable JSON")
def info(input: Path, as_json: bool) -> None:
    """Print packet metadata from a .zpk file."""
    try:
        packet = input.read_bytes()
        stream = EncodedStream.from_bytes(packet)
        payload = {
            "command": "info",
            "mode": stream.mode.value,
            "sample_count": int(stream.sample_count),
            "step": float(stream.step),
            "preset_id": int(stream.preset_id),
            "adaptive": bool(stream.adaptive),
            "packed_size": int(len(packet)),
            "compression_ratio": float(stream.compression_ratio),
            "native_available": bool(_native.available()),
            "exit_code": 0,
        }
        _emit(payload, as_json, [json.dumps(payload, indent=2)])
    except click.ClickException:
        raise
    except Exception as exc:
        raise RuntimeDataError(str(exc)) from exc


@main.command("chemosense-smoke")
@click.option("--json", "as_json", is_flag=True, help="Emit machine-readable JSON")
def chemosense_smoke(as_json: bool) -> None:
    """Run deterministic smell+taste+touch+mental smoke flow."""
    try:
        from .chemosense import run_smoke_flow

        payload = run_smoke_flow()
        _emit(
            payload,
            as_json,
            [
                f"Smell strokes decoded: {payload['smell_stroke_count']}",
                f"Taste events decoded: {payload['taste_event_count']}",
                f"Touch strokes decoded: {payload['touch_stroke_count']}",
                f"Mental strokes decoded: {payload['mental_stroke_count']}",
                f"Fused events: {payload['fused_event_count']}",
            ],
        )
    except click.ClickException:
        raise
    except Exception as exc:
        raise RuntimeDataError(str(exc)) from exc


@main.command()
@click.option("--json", "as_json", is_flag=True, help="Emit machine-readable JSON")
def diagnostics(as_json: bool) -> None:
    """Print runtime diagnostics for automation and operator support."""
    try:
        from . import chemosense

        chemosense_available = True
        chemosense_modules = list(getattr(chemosense, "__all__", []))
        chemosense_error = None
    except Exception as exc:  # pragma: no cover - defensive runtime surfacing
        chemosense_available = False
        chemosense_modules = []
        chemosense_error = str(exc)

    payload = {
        "command": "diagnostics",
        "native_available": bool(_native.available()),
        "native_lib_env": os.getenv("ZPE_IOT_NATIVE_LIB"),
        "chemosense_available": chemosense_available,
        "chemosense_modules": chemosense_modules,
        "chemosense_error": chemosense_error,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "implementation": platform.python_implementation(),
        "argv0": sys.argv[0],
        "exit_code": 0,
    }

    _emit(
        payload,
        as_json,
        [
            f"native_available: {payload['native_available']}",
            f"native_lib_env: {payload['native_lib_env']}",
            f"chemosense_available: {payload['chemosense_available']}",
            f"python_version: {payload['python_version']}",
            f"platform: {payload['platform']}",
        ],
    )


if __name__ == "__main__":  # pragma: no cover - module execution entrypoint
    main()
