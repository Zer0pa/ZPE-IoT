# Internet Evidence Log

- generated_utc: 2026-02-21T15:38:38.822853+00:00
- objective: blocker-exhaustion for IOT-A005 closure under commercial-safe evidence policy

## Source Inventory

| Source | URL | License / Access | Commercialization notes | Claim linkage |
|---|---|---|---|---|
| UCI Air Quality (id=360) | https://archive.ics.uci.edu/dataset/360/air+quality | License shown on page: CC BY 4.0 | Commercial-safe with attribution; suitable for external comparator expansion. | IOT-A005 |
| UCI Beijing PM2.5 (id=381) | https://archive.ics.uci.edu/dataset/381/beijing+pm2+5+data | License shown on page: CC BY 4.0 | Commercial-safe with attribution; used for external stress test. | IOT-A005 |
| UCI Individual Household Electric Power Consumption (id=235) | https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption | License shown on page: CC BY 4.0 | Commercial-safe with attribution; used for low-variance/periodic shape stress test. | IOT-A005 |
| UCI Beijing Multi-Site Air Quality (id=501) | https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data | License shown on page: CC BY 4.0; API import unavailable in ucimlrepo | Commercial-safe by license, but import path blocked in this environment (API availability). | IOT-A005 |
| fpzip reference implementation | https://github.com/LLNL/fpzip | BSD 3-Clause License (repo metadata) | Commercial-safe baseline candidate; local build attempt blocked by storage. | IOT-A005 |

## Resolution Paths (>=3)

1. PATH-1 Legacy contract normalization:
   - evidence: `/Users/prinivenpillay/ZPE IoT/zpe-iot/validation/results/2026-02-21_iot_external_baseline_augmented/a005_resolution_path1_legacy_contract.json`
   - outcome: before=6/8, after=6/8, moved_toward_target=false, result=FAIL_TO_CLOSE.

2. PATH-2 Preset autotune sweep:
   - evidence: `/Users/prinivenpillay/ZPE IoT/zpe-iot/validation/results/2026-02-21_iot_external_baseline_augmented/a005_resolution_path2_preset_autotune.json`
   - outcome: default=6/8, best-preset=7/8, still below 8/8, result=FAIL_TO_CLOSE.

3. PATH-3 External commercial-safe dataset expansion:
   - evidence: `/Users/prinivenpillay/ZPE IoT/zpe-iot/validation/results/2026-02-21_iot_external_baseline_augmented/a005_resolution_path3_external_datasets.json`
   - outcome: wins_best_preset=1/3 on external UCI panel; import attempt for dataset id=501 classified IMP-ACCESS, result=FAIL_TO_CLOSE.

4. PATH-4 External baseline tool (fpzip) integration:
   - evidence: `/Users/prinivenpillay/ZPE IoT/zpe-iot/validation/results/2026-02-21_iot_external_baseline_augmented/a005_resolution_path4_fpzip_tool_attempt.json`
   - outcome: install/build failed with `No space left on device`, classified IMP-STORAGE, result=FAIL_TO_EXECUTE.

## Adjudication Conclusion

- IOT-A005 is closed as **FAIL** (not INCONCLUSIVE): claim requirement "moved toward 8/8" is not met after blocker-exhaustion.
- No claim upgrade was issued without direct artifact evidence.
