from __future__ import annotations

import csv
import io
import json
import time
from pathlib import Path

import click
import numpy as np

from .codec import Config, EncodedStream, Mode, compute_nrmse, decode, encode


@click.group()
def main() -> None:
    """zpe-iot CLI."""


def _read_csv_values(path: Path) -> np.ndarray:
    values = []
    with path.open("r", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            numeric = None
            for cell in reversed(row):
                try:
                    numeric = float(cell)
                    break
                except ValueError:
                    continue
            if numeric is not None:
                values.append(numeric)
    if not values:
        raise click.ClickException("No numeric data found in input CSV")
    return np.asarray(values, dtype=np.float64)


def _write_csv_values(path: Path, values: np.ndarray) -> None:
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["index", "value"])
        for i, v in enumerate(values.tolist()):
            writer.writerow([i, f"{v:.12g}"])


@main.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path))
@click.option("--preset", default="generic", show_default=True)
@click.option("--output", required=True, type=click.Path(path_type=Path))
@click.option("--mode", type=click.Choice([m.value for m in Mode]))
@click.option("--threshold", type=float)
@click.option("--step", type=float)
@click.option("--adaptive/--no-adaptive", default=True)
def compress(input: Path, preset: str, output: Path, mode: str | None, threshold: float | None, step: float | None, adaptive: bool) -> None:
    """Compress a CSV file into .zpk bytes."""
    samples = _read_csv_values(input)
    kwargs = {"adaptive": adaptive}
    if mode is not None:
        kwargs["mode"] = mode
    if threshold is not None:
        kwargs["threshold"] = threshold
    if step is not None:
        kwargs["step"] = step

    stream = encode(samples, preset=preset, **kwargs)
    output.write_bytes(stream.to_bytes())

    click.echo(f"Wrote {output}")
    click.echo(f"Samples: {stream.sample_count}")
    click.echo(f"Packed size: {stream.packed_size} bytes")
    click.echo(f"Compression ratio: {stream.compression_ratio:.2f}x")


@main.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path))
@click.option("--output", required=True, type=click.Path(path_type=Path))
def decompress(input: Path, output: Path) -> None:
    """Decompress .zpk bytes into a CSV."""
    packet = input.read_bytes()
    restored = decode(packet)
    _write_csv_values(output, restored)
    click.echo(f"Wrote {output}")
    click.echo(f"Recovered {len(restored)} samples")


@main.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path))
@click.option("--compare", default="zstd,lz4,zlib", show_default=True)
@click.option("--preset", default="generic", show_default=True)
def benchmark(input: Path, compare: str, preset: str) -> None:
    """Benchmark zpe-iot against selected compressors."""
    samples = _read_csv_values(input)
    stream = encode(samples, preset=preset)
    restored = decode(stream)

    click.echo(f"zpe-iot CR: {stream.compression_ratio:.2f}x")
    click.echo(f"zpe-iot NRMSE: {compute_nrmse(samples, restored):.4f}")

    raw = samples.astype(np.float64).tobytes()
    for name in [c.strip().lower() for c in compare.split(",") if c.strip()]:
        if name == "zlib":
            import zlib

            comp = zlib.compress(raw, level=6)
            cr = len(raw) / len(comp)
        elif name == "zstd":
            try:
                import zstandard as zstd
            except Exception:
                click.echo("zstandard not installed, skipping zstd")
                continue
            comp = zstd.ZstdCompressor(level=3).compress(raw)
            cr = len(raw) / len(comp)
        elif name == "lz4":
            try:
                import lz4.frame
            except Exception:
                click.echo("lz4 not installed, skipping lz4")
                continue
            comp = lz4.frame.compress(raw)
            cr = len(raw) / len(comp)
        else:
            click.echo(f"Unknown comparator: {name}")
            continue
        click.echo(f"{name} CR: {cr:.2f}x")


@main.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path))
def info(input: Path) -> None:
    """Print metadata from a packed .zpk file."""
    packet = input.read_bytes()
    stream = EncodedStream.from_bytes(packet)
    payload = {
        "mode": stream.mode.value,
        "sample_count": stream.sample_count,
        "step": stream.step,
        "preset_id": stream.preset_id,
        "adaptive": stream.adaptive,
        "packed_size": len(packet),
        "compression_ratio": stream.compression_ratio,
    }
    click.echo(json.dumps(payload, indent=2))
