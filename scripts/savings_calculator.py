#!/usr/bin/env python3
"""Interactive ROI calculator for ZPE-IoT."""

from __future__ import annotations


def main() -> int:
    devices = int(input("How many devices? ").strip())
    kb_per_day = float(input("Average data per device per day (KB)? ").strip())
    cost_per_mb = float(input("Cellular cost per MB ($)? ").strip())
    compression = float(input("Expected compression ratio (x)? [default 5] ").strip() or "5")
    license_cost = float(input("Annual ZPE-IoT license cost ($)? [default 50000] ").strip() or "50000")

    annual_mb = devices * (kb_per_day / 1024.0) * 365
    annual_before = annual_mb * cost_per_mb
    annual_after = annual_before / compression
    savings = annual_before - annual_after
    net_roi = savings / max(license_cost, 1.0)

    print("---")
    print(f"Current annual cost: ${annual_before:,.0f}")
    print(f"With zpe-iot ({compression:.1f}x compression): ${annual_after:,.0f}")
    print(f"Annual savings: ${savings:,.0f}")
    print(f"ZPE-IoT Pro license: ${license_cost:,.0f}/year")
    print(f"Net ROI: {net_roi:.1f}x")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
