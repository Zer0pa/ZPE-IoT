# PRD: IoT Wave-1 Coordinated Release Refinement

Date: 2026-02-20
Owner: Product/Engineering
Repo: `/Users/zer0pa-build/ZPE IoT/zpe-iot`
Scope: code + release engineering only
Priority: P0

## 1. Mission

Ship IoT as a production-grade sector artefact in the same release window as IMC and Bio, with strict reproducibility, security/provenance outputs, and compatibility guarantees for packet evolution.

## 2. Position in the Release Family

IoT remains independently deployable. Chemosense/multimodal features must remain explicit and test-isolated. Shared assumptions with IMC are consumed via published contract artifacts, not by tight runtime coupling.

Upstream artifact dependency:
1. `IMC_INTERFACE_CONTRACT.md`
2. `IMC_COMPATIBILITY_VECTOR.json`
3. `IMC_RELEASE_NOTE_FOR_BIO_IOT.md`

## 3. Current Baseline

Observed baseline:
1. Package: `zpe-iot==0.1.0`
2. CLI commands: `compress`, `decompress`, `benchmark`, `info`, `diagnostics`, `chemosense-smoke`
3. Local python tests: `63 PASS` with coverage above threshold
4. Local rust tests: `PASS`
5. CI workflows exist (`ci.yml`, `packaging_warnings.yml`)
6. Release checklist still has unchecked critical items (security artifact, SBOM/manifest, warning-free build, fresh env smoke, publish path)

## 4. Target State

IoT release candidate is acceptable only if all are true:
1. Release checklist is fully automated and hard-gated.
2. Security scan + SBOM + release manifest are generated reproducibly.
3. Fresh-environment command smoke passes for full CLI command set.
4. Wire-format golden compatibility tests are in place.
5. IMC alignment outputs are published for release wave.

## 5. Non-Goals

1. No conversion into monorepo release.
2. No relaxation of existing strict destruct-gate semantics.
3. No external outreach execution in this coding cycle.

## 6. Cross-Repo Coordination Contract (IoT Outputs)

Generate:
1. `docs/family/IOT_IMC_ALIGNMENT_REPORT.md`
2. `docs/family/IOT_COMPATIBILITY_VECTOR.json`
3. `docs/family/IOT_RELEASE_NOTE_FOR_COORDINATION.md`

`IOT_COMPATIBILITY_VECTOR.json` minimum schema:
1. `iot_package_version`
2. `imc_contract_version_consumed`
3. `packet_version_matrix`
4. `multimodal_alignment_assumptions`
5. `wire_compatibility_guarantees`
6. `known_divergences`
7. `breaking_change_policy`

## 7. Execution Protocol (Runbook-First)

Before edits:
1. `validation/runbooks/RUNBOOK_IOT_WAVE1_MASTER.md`
2. `validation/runbooks/RUNBOOK_IOT_WAVE1_PHASE_<N>.md`

Per phase:
1. execute,
2. capture logs,
3. gate,
4. patch,
5. rerun full phase gates,
6. advance only on green.

## 8. Phase Plan

### Phase 0: Baseline Freeze
Tasks:
1. Capture package metadata, CLI command map, test inventory.
2. Re-run python + rust baseline tests.
3. Snapshot current release checklist state.

Outputs:
1. `validation/results/iot_wave1_phase0_inventory.txt`
2. `validation/results/iot_wave1_phase0_baseline.txt`

Gate:
1. Baseline passes.

### Phase 1: Checklist-to-Code Conversion
Tasks:
1. Convert `docs/RELEASE_CHECKLIST.md` items into executable checks in `scripts/release_preflight.sh`.
2. Make preflight exit non-zero on any unmet critical condition.
3. Add machine-readable preflight report output.

Outputs:
1. `validation/results/iot_wave1_phase1_preflight_dryrun.txt`
2. `validation/results/iot_wave1_phase1_preflight_schema.json`

Gate:
1. Preflight enforces all critical items.

### Phase 2: Build and Install Integrity
Tasks:
1. Enforce warning-free build in CI.
2. Add fresh-environment install + CLI smoke for full command set.
3. Add artifact checksums generation for release outputs.

Outputs:
1. `validation/results/iot_wave1_phase2_build_clean.txt`
2. `validation/results/iot_wave1_phase2_fresh_env_smoke.txt`
3. `validation/results/iot_wave1_phase2_checksums.txt`

Gate:
1. Build/install/command smoke green.

### Phase 3: Wire Compatibility Hardening
Tasks:
1. Add golden packet fixtures for versioned decode compatibility.
2. Add strict malformed-packet behavior tests.
3. Add upgrade/backward-compatibility assertions.

Outputs:
1. `validation/results/iot_wave1_phase3_golden_packets.txt`
2. `validation/results/iot_wave1_phase3_malformed_behavior.txt`

Gate:
1. Compatibility and malformed behavior tests pass.

### Phase 4: Security and Provenance Automation
Tasks:
1. Add reproducible security scan command in CI.
2. Generate SBOM and release manifest artifacts.
3. Attach provenance artifacts in release workflow.

Outputs:
1. `validation/results/iot_wave1_phase4_security_scan.txt`
2. `validation/results/iot_wave1_phase4_sbom_manifest.txt`
3. `validation/results/iot_wave1_phase4_release_attestation.txt`

Gate:
1. Security/provenance artifacts generated with passing status.

### Phase 5: IMC Alignment Publication
Tasks:
1. Consume IMC contract artifacts.
2. Publish IoT alignment and compatibility vector in `docs/family`.
3. Record intentional divergence boundaries.

Outputs:
1. `docs/family/IOT_IMC_ALIGNMENT_REPORT.md`
2. `docs/family/IOT_COMPATIBILITY_VECTOR.json`
3. `docs/family/IOT_RELEASE_NOTE_FOR_COORDINATION.md`
4. `validation/results/iot_wave1_phase5_alignment.txt`

Gate:
1. Alignment artifacts complete and schema-valid.

### Phase 6: RC Rehearsal and Handover
Tasks:
1. Execute full preflight and release rehearsal from clean env.
2. Produce final readiness and unresolved risk register.

Outputs:
1. `validation/results/IOT_WAVE1_RELEASE_READINESS_REPORT.md`
2. `validation/results/iot_wave1_phase6_rc_rehearsal.txt`

Gate:
1. All P0 gates pass.

## 9. Acceptance Criteria

Release-ready if all are true:
1. Full checklist is enforced by executable gates.
2. Security/SBOM/provenance outputs are generated.
3. Fresh environment smoke for command set is green.
4. Wire compatibility suite passes.
5. IMC alignment artifacts are published.

## 10. Risks

1. Drift between checklist markdown and executable checks.
2. Compatibility breaks hidden by non-replayable artifacts.
3. Multimodal extension coupling drift against IMC.

Mitigation:
1. Checklist-to-code conversion in Phase 1.
2. Golden packet fixtures in Phase 3.
3. Mandatory Phase 5 alignment checkpoint.
