#!/usr/bin/env python3
"""Generate benchmark charts and docs/BENCHMARKS.md from latest artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "validation" / "results"
DOC_BENCH = ROOT / "docs" / "benchmarks"
DOC_BENCH.mkdir(parents=True, exist_ok=True)


def latest(prefix: str) -> Path:
    files = sorted(RESULTS.glob(f"{prefix}_*.json"))
    if not files:
        raise FileNotFoundError(f"No files for {prefix}")
    return files[-1]


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> int:
    summary = load(latest("bench_summary"))
    zstd = load(latest("bench_vs_zstd"))["results"]
    lz4 = load(latest("bench_vs_lz4"))["results"]
    zlib = load(latest("bench_vs_zlib"))["results"]
    gor = load(latest("bench_vs_gorilla"))["results"]

    ds = [r["dataset"] for r in summary["datasets"]]
    zpe_cr = [r["zpe_iot_cr"] for r in summary["datasets"]]
    zstd_cr = [r["zstd_cr"] for r in summary["datasets"]]
    lz4_cr = [r["lz4_cr"] for r in summary["datasets"]]
    zlib_cr = [r["zlib_cr"] for r in summary["datasets"]]
    gor_cr = [r["gorilla_cr"] for r in summary["datasets"]]

    # 1) CR comparison chart
    x = np.arange(len(ds))
    width = 0.16
    plt.figure(figsize=(12, 5))
    plt.bar(x - 2 * width, zpe_cr, width, label="zpe-iot")
    plt.bar(x - width, zstd_cr, width, label="zstd")
    plt.bar(x, lz4_cr, width, label="lz4")
    plt.bar(x + width, zlib_cr, width, label="zlib")
    plt.bar(x + 2 * width, gor_cr, width, label="gorilla")
    plt.xticks(x, ds)
    plt.ylabel("Compression Ratio (x)")
    plt.title("CR Comparison Across Datasets")
    plt.legend()
    plt.tight_layout()
    cr_png = DOC_BENCH / "cr_comparison.png"
    plt.savefig(cr_png)
    plt.close()

    # 2) Pareto scatter
    pareto_files = sorted(RESULTS.glob("pareto_frontier_*.json"))
    if pareto_files:
        pareto = load(pareto_files[-1])
        rows = pareto.get("rows", [])
        plt.figure(figsize=(8, 5))
        for mode in ["fast", "balanced"]:
            pts = [r for r in rows if r["mode"] == mode]
            if pts:
                plt.scatter([p["nrmse"] for p in pts], [p["cr"] for p in pts], label=mode, alpha=0.8)
        plt.xlabel("NRMSE")
        plt.ylabel("Compression Ratio (x)")
        plt.title("CR vs NRMSE Pareto Frontier")
        plt.legend()
        plt.tight_layout()
        pareto_png = DOC_BENCH / "pareto_frontier.png"
        plt.savefig(pareto_png)
        plt.close()

    # 3/4) Latency + memory
    comp_names = ["zpe-iot", "zstd", "lz4", "zlib", "gorilla"]

    def avg_metric(rows: list[dict], key: str, comp: str) -> float:
        vals = []
        for r in rows:
            vals.append(float(r[comp][key]))
        return float(np.mean(vals))

    zstd_map = {r["dataset"]: r for r in zstd}
    lz4_map = {r["dataset"]: r for r in lz4}
    zlib_map = {r["dataset"]: r for r in zlib}
    gor_map = {r["dataset"]: r for r in gor}

    zpe_lat = np.mean([r["zpe_iot"]["encode_ms"] for r in zstd])
    zstd_lat = avg_metric(zstd, "encode_ms", "zstd")
    lz4_lat = avg_metric(lz4, "encode_ms", "lz4")
    zlib_lat = avg_metric(zlib, "encode_ms", "zlib")
    gor_lat = avg_metric(gor, "encode_ms", "gorilla")

    plt.figure(figsize=(8, 4))
    plt.bar(comp_names, [zpe_lat, zstd_lat, lz4_lat, zlib_lat, gor_lat])
    plt.ylabel("Encode latency (ms, mean)")
    plt.title("Latency Comparison")
    plt.tight_layout()
    latency_png = DOC_BENCH / "latency_comparison.png"
    plt.savefig(latency_png)
    plt.close()

    zpe_mem = np.mean([r["zpe_iot"]["peak_bytes"] for r in zstd])
    zstd_mem = avg_metric(zstd, "peak_bytes", "zstd")
    lz4_mem = avg_metric(lz4, "peak_bytes", "lz4")
    zlib_mem = avg_metric(zlib, "peak_bytes", "zlib")
    gor_mem = avg_metric(gor, "peak_bytes", "gorilla")

    plt.figure(figsize=(8, 4))
    plt.bar(comp_names, [zpe_mem, zstd_mem, lz4_mem, zlib_mem, gor_mem])
    plt.ylabel("Peak memory (bytes)")
    plt.title("Memory Usage Comparison")
    plt.tight_layout()
    mem_png = DOC_BENCH / "memory_comparison.png"
    plt.savefig(mem_png)
    plt.close()

    # markdown report
    lines = []
    lines.append("# ZPE-IoT Benchmark Results")
    lines.append("")
    lines.append("## Methodology")
    lines.append("- Benchmarks run on DS-01..DS-08 with identical raw float64 inputs for all compressors.")
    lines.append("- Comparators: zstd(level=3), LZ4, zlib(level=6), Gorilla-proxy.")
    lines.append(f"- Latest summary artifact: `{latest('bench_summary')}`")
    lines.append("")
    lines.append("## Results Summary")
    lines.append(f"- PT-6 status: **{'PASS' if summary['pt6_pass'] else 'FAIL'}** ({summary['wins']}/{summary['total']} wins for zpe-iot)")
    lines.append(f"- Mean zpe-iot CR across DS-01..DS-08: **{summary['mean_cr']:.2f}x**")
    lines.append("")
    lines.append("## Detailed Results")
    lines.append("")
    lines.append("| Dataset | zpe-iot CR | zpe-iot NRMSE | zstd CR | LZ4 CR | zlib CR | Gorilla CR | Winner |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
    for r in summary["datasets"]:
        lines.append(
            f"| {r['dataset']} | {r['zpe_iot_cr']:.2f} | {r['zpe_iot_nrmse']:.4f} | {r['zstd_cr']:.2f} | {r['lz4_cr']:.2f} | {r['zlib_cr']:.2f} | {r['gorilla_cr']:.2f} | {r['winner']} |"
        )
    lines.append("")
    lines.append("### Charts")
    lines.append(f"![CR comparison](benchmarks/{cr_png.name})")
    lines.append(f"![Pareto frontier](benchmarks/pareto_frontier.png)")
    lines.append(f"![Latency comparison](benchmarks/{latency_png.name})")
    lines.append(f"![Memory comparison](benchmarks/{mem_png.name})")
    lines.append("")
    lines.append("## When NOT to Use ZPE-IoT")
    lines.append("- Already compressed payloads.")
    lines.append("- Cryptographically random/high-entropy data.")
    lines.append("- Workloads demanding strict lossless reconstruction.")
    lines.append("")
    lines.append("## How to Reproduce")
    lines.append("```bash")
    lines.append("cd /Users/prinivenpillay/ZPE\\ IoT/zpe-iot")
    lines.append("source .venv/bin/activate")
    lines.append("python validation/benchmarks/run_benchmarks.py")
    lines.append("python validation/benchmarks/generate_report.py")
    lines.append("```")
    lines.append("")
    lines.append("## ROI Calculator")
    lines.append("Example: 10,000 devices × 1 MB/day × $1.00/MB = $3.65M/year")
    lines.append("At 5x compression: $0.73M/year")
    lines.append("Savings: $2.92M/year; $50K license implies ~58x ROI.")

    (ROOT / "docs" / "BENCHMARKS.md").write_text("\n".join(lines) + "\n")
    print("Updated docs/BENCHMARKS.md and charts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
