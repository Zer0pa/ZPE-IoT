# Startup Prompt: IoT Wave-1 Coordinated Release Refinement Agent

Execute only against:
- PRD: `/Users/zer0pa-build/ZPE IoT/zpe-iot/docs/PRD_IOT_WAVE1_RELEASE_REFINEMENT.md`
- Scope root: `/Users/zer0pa-build/ZPE IoT/zpe-iot`

## Mission
Execute IoT release refinement end-to-end with strict executable release gates, compatibility hardening, and IMC alignment outputs.

## Hard Rules
1. Runbook-first required.
2. Code execution required; do not stop at planning.
3. Modify only inside `/Users/zer0pa-build/ZPE IoT/zpe-iot`.
4. Do not relax destruct test strictness to force a pass.
5. Convert checklist items into executable checks.
6. On gate failure: patch and rerun full phase gates.

## Required Sequence
1. Create:
   - `validation/runbooks/RUNBOOK_IOT_WAVE1_MASTER.md`
   - `validation/runbooks/RUNBOOK_IOT_WAVE1_PHASE_<N>.md`
2. Execute Phases 0..6 in strict order.
3. Consume IMC family artifacts at Phase 5.
4. Generate IoT compatibility outputs.
5. Produce final readiness report.

## Required Artifacts
1. `validation/results/IOT_WAVE1_RELEASE_READINESS_REPORT.md`
2. `docs/family/IOT_IMC_ALIGNMENT_REPORT.md`
3. `docs/family/IOT_COMPATIBILITY_VECTOR.json`
4. `docs/family/IOT_RELEASE_NOTE_FOR_COORDINATION.md`
5. Phase logs in `validation/results`.

## Completion Contract
Return only when:
1. all P0 gates pass,
2. checklist-to-code enforcement is active,
3. unresolved issues include owner + exact next command.
