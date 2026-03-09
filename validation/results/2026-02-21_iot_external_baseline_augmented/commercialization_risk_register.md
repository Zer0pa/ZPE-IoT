# Commercialization Risk Register

| Severity | Claim | Precision Risk Statement | Evidence | Mitigation |
|---|---|---|---|---|
| High | IOT-A005 | Under unchanged comparator contract (zlib/lz4/zstd), wins remain 6/8; no directional move to 8/8 proven. | `/Users/prinivenpillay/ZPE IoT/zpe-iot/validation/results/2026-02-21_iot_external_baseline_augmented/a005_resolution_path1_legacy_contract.json` | Hold claim at FAIL and communicate dataset-conditional performance only. |
| Medium | IOT-A005 | Even with per-dataset preset autotuning, best achievable wins are 7/8, not 8/8. | `/Users/prinivenpillay/ZPE IoT/zpe-iot/validation/results/2026-02-21_iot_external_baseline_augmented/a005_resolution_path2_preset_autotune.json` | Evaluate codec-v2 or transform-stage innovation before any claim upgrade attempt. |
| Medium | External baseline comparability | External UCI datasets show mixed outcomes (1/3 wins with best preset), reducing generalization confidence. | `/Users/prinivenpillay/ZPE IoT/zpe-iot/validation/results/2026-02-21_iot_external_baseline_augmented/a005_resolution_path3_external_datasets.json` | Expand permissive external benchmark panel and keep conservative claim wording. |
| Low | Optional comparator breadth | fpzip path blocked by local storage, not by claim gate requirement. | `/Users/prinivenpillay/ZPE IoT/zpe-iot/validation/results/2026-02-21_iot_external_baseline_augmented/a005_resolution_path4_fpzip_tool_attempt.json` | Re-run optional tool-path once storage is cleared. |
