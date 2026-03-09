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
    pattern = f"{prefix}_*.json"
    if prefix == "bench_summary":
        pattern = "bench_summary_[0-9]*.json"
    files = sorted(RESULTS.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files for {prefix}")
    return files[-1]


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _pick_claim_tier(e0: dict, e1: dict, e2: dict) -> tuple[str, dict]:
    if int(e2.get("total", 0)) > 0:
        return "E2", e2
    if int(e1.get("total", 0)) > 0:
        return "E1", e1
    return "E0", e0


def _pt6_status(payload: dict) -> str:
    total = int(payload.get("total", 0))
    if total == 0:
        return "NOT_AVAILABLE"
    return "PASS" if bool(payload.get("pt6_pass", False)) else "FAIL"


def main() -> int:
    summary = load(latest("bench_summary"))
    e0 = load(latest("bench_summary_E0_proxy"))
    e1 = load(latest("bench_summary_E1_real_public"))
    e2 = load(latest("bench_summary_E2_real_customer"))

    zstd = load(latest("bench_vs_zstd"))["results"]
    lz4 = load(latest("bench_vs_lz4"))["results"]
    zlib = load(latest("bench_vs_zlib"))["results"]
    gor = load(latest("bench_vs_gorilla"))["results"]

    claim_tier, claim_payload = _pick_claim_tier(e0, e1, e2)
    pt6_final_status = _pt6_status(claim_payload)
    pt6_provisional_status = _pt6_status(e0)
    nrmse_label = summary.get("fidelity_metric_label", "NRMSE(window-normalized)")

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

    # 2) Pareto scatter (if available)
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
        plt.savefig(DOC_BENCH / "pareto_frontier.png")
        plt.close()

    # 3/4) Latency + memory
    comp_names = ["zpe-iot", "zstd", "lz4", "zlib", "gorilla"]

    def avg_metric(rows: list[dict], key: str, comp: str) -> float:
        return float(np.mean([float(r[comp][key]) for r in rows]))

    zpe_lat = float(np.mean([r["zpe_iot"]["encode_ms"] for r in zstd]))
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

    zpe_mem = float(np.mean([r["zpe_iot"]["peak_bytes"] for r in zstd]))
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

    # Markdown report
    lines: list[str] = []
    lines.append("# ZPE-IoT Benchmark Results")
    lines.append("")
    lines.append("## Evidence Labeling")
    lines.append(f"- Evidence Class: **{claim_tier}**")
    lines.append(f"- PT-6 FINAL ({claim_tier}): **{pt6_final_status}** ({claim_payload.get('wins', 0)}/{claim_payload.get('total', 0)} wins)")
    lines.append(f"- PT-6 PROVISIONAL (E0): **{pt6_provisional_status}** ({e0.get('wins', 0)}/{e0.get('total', 0)} wins)")
    lines.append("")
    lines.append("## Methodology")
    lines.append("- Benchmarks run on DS-01..DS-08 with identical raw float64 inputs for all compressors.")
    lines.append("- Comparators: zstd(level=3), LZ4, zlib(level=6), Gorilla-proxy.")
    lines.append(f"- Fidelity metric in benchmark table: `{nrmse_label}`")
    method_meta = summary.get("method_metadata", {})
    if method_meta:
        lines.append(f"- Encode/decode pathway: `{method_meta.get('encode_decode_pathway', 'unspecified')}`")
        lines.append(
            f"- Iterations: {method_meta.get('iteration_count', 'n/a')} "
            f"(warmup {method_meta.get('warmup_iterations', 'n/a')})"
        )
    lines.append(f"- Overall summary artifact: `{rel(latest('bench_summary'))}`")
    lines.append(f"- E0 summary artifact: `{rel(latest('bench_summary_E0_proxy'))}`")
    lines.append(f"- E1 summary artifact: `{rel(latest('bench_summary_E1_real_public'))}`")
    lines.append(f"- E2 summary artifact: `{rel(latest('bench_summary_E2_real_customer'))}`")
    lines.append("")
    lines.append("## Results Summary")
    lines.append(f"- Mean zpe-iot CR across DS-01..DS-08: **{summary['mean_cr']:.2f}x**")
    lines.append(f"- Active claim tier mean CR ({claim_tier}): **{claim_payload['mean_cr']:.2f}x**")
    lines.append("")
    lines.append("## Detailed Results")
    lines.append("")
    lines.append(f"| Dataset | Evidence | zpe-iot CR | zpe-iot {nrmse_label} | zstd CR | LZ4 CR | zlib CR | Gorilla CR | Winner |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---|")
    for r in summary["datasets"]:
        lines.append(
            f"| {r['dataset']} | {r.get('evidence_class', 'E0')} | {r['zpe_iot_cr']:.2f} | {r['zpe_iot_nrmse']:.4f} | {r['zstd_cr']:.2f} | {r['lz4_cr']:.2f} | {r['zlib_cr']:.2f} | {r['gorilla_cr']:.2f} | {r['winner']} |"
        )
    lines.append("")
    lines.append("### Charts")
    lines.append(f"![CR comparison](benchmarks/{cr_png.name})")
    lines.append("![Pareto frontier](benchmarks/pareto_frontier.png)")
    lines.append(f"![Latency comparison](benchmarks/{latency_png.name})")
    lines.append(f"![Memory comparison](benchmarks/{mem_png.name})")
    lines.append("")
    lines.append("## Reproducibility Envelope")
    repro = summary.get("reproducibility", {})
    lines.append(f"- Dataset manifest SHA256: `{repro.get('manifest_sha256', 'unknown')}`")
    lines.append(f"- Toolchain: `{json.dumps(repro.get('toolchain', {}), sort_keys=True)}`")
    lines.append(f"- Hardware profile: `{json.dumps(repro.get('hardware_profile', {}), sort_keys=True)}`")
    lines.append(f"- Commands: `{json.dumps(repro.get('commands', {}), sort_keys=True)}`")
    lines.append("")
    lines.append("## When NOT to Use ZPE-IoT")
    lines.append("- Already compressed payloads.")
    lines.append("- Cryptographically random/high-entropy data.")
    lines.append("- Workloads demanding strict lossless reconstruction.")
    lines.append("")
    lines.append("## How to Reproduce")
    lines.append("```bash")
    lines.append('ZPE_IOT_ROOT="${ZPE_IOT_ROOT:-$(pwd)}"')
    lines.append('cd "$ZPE_IOT_ROOT"')
    lines.append("source .venv/bin/activate")
    lines.append("python validation/benchmarks/run_benchmarks.py")
    lines.append("python validation/benchmarks/generate_report.py")
    lines.append("python validation/benchmarks/run_wi1_ablation.py --repeats 5")
    lines.append("python validation/benchmarks/run_zh1_ablation.py --repeats 5")
    lines.append("```")

    (ROOT / "docs" / "BENCHMARKS.md").write_text("\n".join(lines) + "\n")
    print("Updated docs/BENCHMARKS.md and charts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
