# Benchmark Authority

Date: 2026-03-21
Anchor: `validation/results/bench_summary_E1_real_public_20260321T225305.json`

## Governing Result

The promoted March 21 real-public E1 surface is above the governing gate:

- `mean CR = 17.163613932777356x`
- `wins = 10/11`
- remaining competitor win on the promoted surface: `DS-12`

## Dataset-Level Outcome

| Dataset | ZPE-IoT CR | Best baseline CR | Winner |
| ------- | ---------- | ---------------- | ------ |
| `DS-01` | `6.184694121802311x` | `zlib 4.261137440758294x` | `zpe-iot` |
| `DS-02` | `6.39722204594255x` | `zstd 1.6982637989116351x` | `zpe-iot` |
| `DS-03` | `7.656956823634123x` | `zlib 3.8134473829682x` | `zpe-iot` |
| `DS-04` | `7.159965904843323x` | `zlib 1.0492811169105638x` | `zpe-iot` |
| `DS-05` | `7.290115821056622x` | `zlib 7.021212770516391x` | `zpe-iot` |
| `DS-06` | `6.240327588524611x` | `gorilla-proxy 2.985247324269598x` | `zpe-iot` |
| `DS-07` | `6.977718665392963x` | `zstd 1.3718065454697688x` | `zpe-iot` |
| `DS-08` | `6.5710898070463655x` | `zstd 3.5722228278643846x` | `zpe-iot` |
| `DS-09` | `6.380880412591241x` | `zstd 2.5529693617187044x` | `zpe-iot` |
| `DS-10` | `7.4701938344227035x` | `zstd 1.9139348451440503x` | `zpe-iot` |
| `DS-12` | `120.47058823529412x` | `zstd 5957.818181818182x` | `competitor` |

## Interpretation

The benchmark question is no longer open inside this PRD. The promoted March 21 surface moved materially, and the active authority line is now the widened `10/11` READY dataset set rather than the earlier `7/8` subset closure.

The boundary is not whether the benchmark line is green. It is that `DS-12` remains a competitor win and `DS-11` remains blocked, so the verdict must stay bounded rather than implying a clean sweep or a fully open dataset surface.

## Methodology Disclosures

- **Gorilla-proxy:** The `gorilla-proxy` comparator is a simplified ~25-line XOR-delta + zlib implementation inspired by Facebook Gorilla's XOR encoding. It is not Facebook's production Gorilla codec.
- **CR denominator:** All compression ratios use float64 (8 bytes/sample) raw size as denominator. Against a float32 baseline, ratios would be approximately half.
- **Lossy vs lossless:** ZPE-IoT is bounded-lossy; all baseline comparators (zstd, LZ4, zlib, gorilla-proxy) are lossless.
- **Stream length cap:** Codec has a 65,536-sample hard cap (2-byte header); ~16 minutes at 60 Hz.
- **Non-finite inputs:** NaN and Inf values cause codec failure.
