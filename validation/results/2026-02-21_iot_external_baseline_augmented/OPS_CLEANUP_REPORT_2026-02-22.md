# OPS Cleanup Report (2026-02-22)

- lane_id: `ZPE IoT`
- lane_root: `/Users/prinivenpillay/ZPE IoT/zpe-iot/validation/results/2026-02-21_iot_external_baseline_augmented`
- timestamp_utc: `2026-02-22T02:29:30.351826+00:00`

## Pre-cleanup Disk Usage
- total_bytes: `70014494` (66.77 MB)

### Top Heavy Entries (pre)
| Path | Type | Size (bytes) | Size (human) |
|---|---:|---:|---:|
| `tsbs-bin` | dir | 31031088 | 29.59 MB |
| `tsbs_iot_data.influx` | file | 18452561 | 17.60 MB |
| `a4_tsbs_generate.log` | file | 18452561 | 17.60 MB |
| `tsbs-src` | dir | 1991502 | 1.90 MB |
| `iot_external_baseline_results.json` | file | 12481 | 12.19 KB |
| `a005_resolution_path2_preset_autotune.json` | file | 9448 | 9.23 KB |
| `handoff_manifest.json` | file | 7053 | 6.89 KB |
| `command_log.txt` | file | 4387 | 4.28 KB |
| `a005_resolution_path3_external_datasets.json` | file | 3854 | 3.76 KB |
| `determinism_replay_results.json` | file | 3806 | 3.72 KB |
| `a005_resolution_path1_legacy_contract.json` | file | 3102 | 3.03 KB |
| `internet_evidence_log.md` | file | 2986 | 2.92 KB |
| `rle_postpass_ablation.json` | file | 2713 | 2.65 KB |
| `quality_gate_scorecard.json` | file | 2526 | 2.47 KB |
| `baseline_delta_matrix.json` | file | 2465 | 2.41 KB |

### Top Heavy Files (pre)
| File | Size (bytes) | Size (human) |
|---|---:|---:|
| `tsbs-bin/tsbs_generate_data` | 31031088 | 29.59 MB |
| `tsbs_iot_data.influx` | 18452561 | 17.60 MB |
| `a4_tsbs_generate.log` | 18452561 | 17.60 MB |
| `tsbs-src/.git/objects/pack/pack-df6c8a407afbd835b94a72afcf01e70ae8f28ed4.pack` | 452927 | 442.31 KB |
| `tsbs-src/go.sum` | 138955 | 135.70 KB |
| `tsbs-src/.git/index` | 44543 | 43.50 KB |
| `tsbs-src/cmd/tsbs_generate_queries/databases/timescaledb/iot_test.go` | 28234 | 27.57 KB |
| `tsbs-src/README.md` | 20127 | 19.66 KB |
| `tsbs-src/internal/inputs/generator_queries_test.go` | 18955 | 18.51 KB |
| `tsbs-src/cmd/tsbs_generate_queries/databases/influx/iot_test.go` | 17485 | 17.08 KB |
| `tsbs-src/pkg/data/usecases/iot/simulator_test.go` | 17450 | 17.04 KB |
| `tsbs-src/cmd/tsbs_generate_queries/databases/timescaledb/devops_test.go` | 17165 | 16.76 KB |
| `tsbs-src/cmd/tsbs_generate_queries/databases/clickhouse/devops_test.go` | 15657 | 15.29 KB |
| `tsbs-src/cmd/tsbs_generate_queries/databases/timestream/devops_test.go` | 15507 | 15.14 KB |
| `tsbs-src/.git/objects/pack/pack-df6c8a407afbd835b94a72afcf01e70ae8f28ed4.idx` | 14680 | 14.34 KB |
| `tsbs-src/cmd/tsbs_run_queries_cassandra/query_plan.go` | 14459 | 14.12 KB |
| `tsbs-src/cmd/tsbs_generate_queries/databases/timescaledb/iot.go` | 14222 | 13.89 KB |
| `tsbs-src/cmd/tsbs_generate_queries/databases/influx/devops_test.go` | 13761 | 13.44 KB |
| `tsbs-src/cmd/tsbs_generate_queries/databases/mongo/devops.go` | 13320 | 13.01 KB |
| `iot_external_baseline_results.json` | 12481 | 12.19 KB |

## Post-cleanup Disk Usage
- total_bytes: `68020979` (64.87 MB)

### Top Heavy Entries (post)
| Path | Type | Size (bytes) | Size (human) |
|---|---:|---:|---:|
| `tsbs-bin` | dir | 31031088 | 29.59 MB |
| `tsbs_iot_data.influx` | file | 18452561 | 17.60 MB |
| `a4_tsbs_generate.log` | file | 18452561 | 17.60 MB |
| `iot_external_baseline_results.json` | file | 12481 | 12.19 KB |
| `a005_resolution_path2_preset_autotune.json` | file | 9448 | 9.23 KB |
| `handoff_manifest.json` | file | 7053 | 6.89 KB |
| `command_log.txt` | file | 4387 | 4.28 KB |
| `a005_resolution_path3_external_datasets.json` | file | 3854 | 3.76 KB |
| `determinism_replay_results.json` | file | 3806 | 3.72 KB |
| `a005_resolution_path1_legacy_contract.json` | file | 3102 | 3.03 KB |
| `internet_evidence_log.md` | file | 2986 | 2.92 KB |
| `rle_postpass_ablation.json` | file | 2713 | 2.65 KB |
| `quality_gate_scorecard.json` | file | 2526 | 2.47 KB |
| `baseline_delta_matrix.json` | file | 2465 | 2.41 KB |
| `strict_replay_campaign.json` | file | 2195 | 2.14 KB |

## Space Reclaimed
- reclaimed_bytes: `1993515` (1.90 MB)
- deleted_count: `3`
- quarantined_count: `0`

## Deleted Files
| Path | Type | Size (bytes) | Reason |
|---|---:|---:|---|
| `a4_install_go.log` | file | 1886 | Lane-local setup scratch/unreferenced clone log; regenerable and not required by active evidence chain. |
| `a4_tsbs_clone.log` | file | 127 | Lane-local setup scratch/unreferenced clone log; regenerable and not required by active evidence chain. |
| `tsbs-src` | directory | 1991502 | Lane-local setup scratch/unreferenced clone log; regenerable and not required by active evidence chain. |

## Quarantined Files
| Source Path | Quarantine Path | Type | Size (bytes) | Reason |
|---|---|---:|---:|---|
| (none) | (none) | - | - | - |

## Kept Critical Files
| File | Size (bytes) | Evidence Reference |
|---|---:|---|
| `a005_resolution_path1_legacy_contract.json` | 3102 | `claim_status_delta.md, commercialization_risk_register.md, handoff_manifest.json, internet_evidence_log.md, quality_gate_scorecard.json` |
| `a005_resolution_path2_preset_autotune.json` | 9448 | `claim_status_delta.md, commercialization_risk_register.md, handoff_manifest.json, internet_evidence_log.md, quality_gate_scorecard.json` |
| `a005_resolution_path3_external_datasets.json` | 3854 | `claim_status_delta.md, commercialization_risk_register.md, handoff_manifest.json, internet_evidence_log.md, quality_gate_scorecard.json` |
| `a005_resolution_path4_fpzip_tool_attempt.json` | 611 | `claim_status_delta.md, commercialization_risk_register.md, handoff_manifest.json, internet_evidence_log.md, quality_gate_scorecard.json` |
| `a0_dt09.log` | 188 | `command_log.txt` |
| `a0_strict.log` | 1820 | `command_log.txt` |
| `a1_generate_report.log` | 38 | `command_log.txt` |
| `a1_run_benchmarks.log` | 1454 | `command_log.txt` |
| `a2_dt09_after.log` | 188 | `command_log.txt` |
| `a2_pytest_dt09_semantics.log` | 98 | `command_log.txt` |
| `a3_pcodec_install.log` | 185 | `command_log.txt` |
| `a4_go_version.log` | 33 | `command_log.txt` |
| `a4_tsbs_generate.log` | 18452561 | `command_log.txt` |
| `a4_tsbs_install.log` | 0 | `command_log.txt` |
| `a7_cargo_test.log` | 1594 | `command_log.txt` |
| `a7_pytest_full.log` | 99 | `command_log.txt` |
| `a7_release_bundle.log` | 261 | `command_log.txt` |
| `a7_strict_run_1.log` | 1820 | `command_log.txt` |
| `a7_strict_run_2.log` | 1820 | `command_log.txt` |
| `a7_strict_run_3.log` | 1820 | `command_log.txt` |
| `a7_strict_run_4.log` | 1820 | `command_log.txt` |
| `a7_strict_run_5.log` | 1820 | `command_log.txt` |
| `baseline_delta_matrix.json` | 2465 | `handoff_manifest.json` |
| `before_after_metrics.json` | 984 | `claim_status_delta.md, handoff_manifest.json` |
| `claim_status_delta.md` | 2035 | `command_log.txt, control_file, handoff_manifest.json` |
| `command_log.txt` | 4387 | `claim_status_delta.md, control_file, handoff_manifest.json` |
| `commercialization_risk_register.md` | 1509 | `control_file, handoff_manifest.json` |
| `determinism_replay_results.json` | 3806 | `claim_status_delta.md, handoff_manifest.json` |
| `dt09_native_python_split.json` | 330 | `claim_status_delta.md, handoff_manifest.json` |
| `dt09_semantics_recheck.json` | 745 | `claim_status_delta.md, handoff_manifest.json` |
| `external_baseline_table.csv` | 1129 | `claim_status_delta.md, handoff_manifest.json` |
| `falsification_results.md` | 998 | `handoff_manifest.json` |
| `handoff_manifest.json` | 7053 | `command_log.txt, control_file, handoff_manifest.json` |
| `impracticality_decisions.json` | 22 | `handoff_manifest.json` |
| `internet_evidence_log.md` | 2986 | `claim_status_delta.md, control_file, handoff_manifest.json, quality_gate_scorecard.json` |
| `iot_external_baseline_results.json` | 12481 | `claim_status_delta.md, handoff_manifest.json` |
| `path_portability_audit.json` | 333 | `claim_status_delta.md, command_log.txt, handoff_manifest.json` |
| `payload_economics_table.csv` | 2007 | `claim_status_delta.md, handoff_manifest.json` |
| `quality_gate_scorecard.json` | 2526 | `control_file, handoff_manifest.json, quality_gate_scorecard.json, runpod_readiness_manifest.json` |
| `reproducibility_proof.txt` | 331 | `claim_status_delta.md, control_file, handoff_manifest.json` |
| `residual_risk_register.md` | 901 | `control_file, handoff_manifest.json` |
| `rle_postpass_ablation.json` | 2713 | `claim_status_delta.md, handoff_manifest.json` |
| `runpod_readiness_manifest.json` | 760 | `control_file, handoff_manifest.json, quality_gate_scorecard.json, runpod_readiness_manifest.json` |
| `strict_replay_campaign.json` | 2195 | `claim_status_delta.md, handoff_manifest.json` |
| `tsbs-bin/tsbs_generate_data` | 31031088 | `command_log.txt` |
| `tsbs_iot_data.influx` | 18452561 | `command_log.txt` |

## Validation Checks
- required_paths_exist: `True`
- required_paths_missing: `[]`
- required_adjudication_files_exist: `True`
- required_adjudication_files_missing: `[]`
- core_files_exist: `True`
- core_files_missing: `[]`
- post_cleanup_reference_integrity_pass: `True`
