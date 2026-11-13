# CI handoff: HOLD, no dispatch requested

Required-state predicate is unresolved (REQUIRED-STATE.md). There is no implementation commit
or executable fixture set to send to CI. All compiler units and verifier integrations are NOT_RUN.
TEST-MANIFEST.json contains proposed obligations, not an approved selector/root count.

After the fact and implementation are reviewed, coordinator to predeclare exact roots/caps:

1. Compiler resolver units for missing marker, missing emitted symbol, ambiguous candidates,
   successful whole-static preservation, uninit-off, NOT_REQUIRED and UNKNOWN handling.
2. Fact controls for every write family, delayed instrumentation, transitive/indirect helpers,
   clause-only/other-root/address-taken false positives, zero-layout cases and reset/immutable seed.
3. Normal source→emitted integrations: uninit-off PFC, on/no writes inside wrapper, on/state binding.
4. Replace and RecursiveCheck roots with ordinary/SimpleCheck companions; bind actual modes,
   helper/return and clauses, recursive base/edge/reentry. Export complete JSON outcomes/properties.

Use existing JSON export; do not depend on worker14's unfinished checker. Do not guess goldens.
Build failure means downstream NOT_RUN. Staged units are not verifier acceptance.
Heavy fixtures retain b12 policy: `-Z unstable-options` before consuming
`--cbmc-args --object-bits 12`; preserve solver, slicing and checks.

After review/composition with worker14, one coordinated gate must preserve lawful user/private
writes, mapped P2/postcondition-hole checks and user outside-write frame-negative. The marker
diagnostic cannot substitute for these semantic results. Follow with one agreed Quick plus
selected new suites; M3/platform/SmallSort remain separate gates.

No builds, CI, push, raw evidence reads or prior grant reuse occurred in this preparation.
