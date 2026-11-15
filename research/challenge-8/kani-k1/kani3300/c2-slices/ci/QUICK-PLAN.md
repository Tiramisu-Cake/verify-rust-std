# Cumulative fork Quick plan — stage 0, NOT_RUN

CI-only overlay/request is prepared in a later authorized stage for each exact source head. This plan does not dispatch, publish or create a workflow. Coordinator owns fork CI; Cloud $0. U/B1 fixed, no rebase.

Use accepted `.github/workflows/uninit-quick.yml` @0998b98867 as recipe, not as an unchanged artifact uploader: its three historical Part1 JSON artifact paths are stale. Overlay may remove stock workflows only within overlay; source heads retain all stock workflows. Overlay records parent/source SHA + tree and source manifest before/after; compiler/runtime/tests/docs/deps cannot differ from source. `ubuntu-24.04`, job cap120 min, per-test2400s, no auto-retries, `RUST_TEST_THREADS=2`; fmt → build-dev → workspace/tests clippy `-D warnings` → units → suites. About7 minutes is a past observation, not a timeout target.

Preserve native checks/solver/pins and per-fixture12-bit flags. No global object-bits change, no new ignores/fixmes, no golden changes or whole-file filtering to hide a missing prerequisite. Missing prerequisites → STOP before candidate acceptance.

Every head runs these exact base selections (expanded names in QUICK-PLAN.json):

- `cargo run -p compiletest --quiet -- --suite kani --mode kani Uninit Quantifiers TailCall --no-fail-fast --timeout 2400` (24 fixture files).
- Same invocation with `--suite expected --mode expected uninit quantifier-capture arbitrary` (counts below; this includes all present uninit).
- `--suite ui --mode expected quantifier-safety-checks explicit-tail-calls` (17).
- `--suite script-based-pre --mode exec mem-init-reinstrumentation autoharness_explicit_tail_call` (2).
- `--suite json-handler --mode exec` (all17 upstream suites, no three old Part1 suites).

| Head | expected discovery / intended pass / unchanged ignored | Targeted added unit filters / total |
|---|---|---|
| 1 | 87 / 85 / 2 | active_call_tests:9 / 9 |
| 2 | 93 / 91 / 2 | immutable_allocations::tests:9, active_call_tests:9 / 18 |
| 3 | 112 / 110 / 2 | immutable_allocations::tests:9, active_call_tests:9 / 18 |
| 4 | 187 / 185 / 2 | immutable_allocations::tests:9, marker_category_tests:1, active_call_tests:9, argument_size_tests:1 / 20 |
| 5 | 234 / 232 / 2 | immutable_allocations::tests:9, marker_category_tests:1, active_call_tests:9, argument_size_tests:1 / 20 |
| 6 | 247 / 245 / 2 | immutable_allocations::tests:9, marker_category_tests:1, active_call_tests:9, argument_size_tests:1 / 20 |
| 7 | 247 / 245 / 2 | immutable_allocations::tests:9, marker_category_tests:1, active_call_tests:9, argument_size_tests:1, delayed_cache::tests:6, delayed_scope_tests:2 / 28 |

Counts are static fixture discovery under this map's current dependency bounds; they are not observed pass counts. B1's22 fixtures remain on every head;4 final-source entry replacements change no discovery counts. Recompute from each actual candidate if coordinator changes an owner/prerequisite. Never demand F's245 passed or76 total compiler units from an earlier head. Unit filters must select exactly the listed nonzero count, with actual pass/fail/ignore lines retained; zero tests is not qualification.

Slice-specific acceptance:

1. ANALYSIS: `active_call_tests`9 includes DAG/repeated-call positive, self/mutual-cycle negatives, exact body/instance identity, root-order independence and bounded diagnostics. These are generic ActiveCalls tests, not reached compiler MIR/ordinary-slot evidence. All present baseline uninit remains mandatory. Add bounded `kani FunctionContracts` smoke (25 source fixtures, native existing fixmes preserved) and the exact12 expected smoke selectors below. STOP unresolved final-fixture prerequisite / ordinary captured-closure regression risk; don't accept only compile+units as complete CC1/CC2 integration coverage.
2. IMMUTABLE: immutable_allocations9 (zero vs None; exact descriptor conflict; alias order qualification join; mutable/nonqualifying refusal; reset completion/edges; empty extent),6 coalescing/CTFE expected files. Other immutable masks/promoted fixtures require raw_eq3 and copy target4; pending qualification is explicit, never fake SUCCESS on early raw_eq Unsupported.
3. LAYOUT-RAW:4 u8 mixed stack/promoted controls now runnable; promoted/direct/helper and immutable source qualification row join here. Full raw-eq-uninit and nested Pat/enum fixture files still require4 for local MU storage. No broad Unsupported substituted for intended raw read failure. Complete3 requires dependency review if this leaves its actual offset behavior unqualified.
4. STORAGE: all MU storage, Copy/Move/pairing/return0/reset/transmute/data/padding, part1 composition, padded stride/cross-slot extents and F6 two distinguishing negatives plus reinit. argument_size1 and marker_category1. Ordinary entry/payload/cycle deferred fixtures join here. Hook-only refusal vs ordinary marker/model; two marked-model controls have a pending E1 seam review, and generated-modifies PFC waits for5. No release with an incoherent paired protocol or an unsafe intermediate guard.
5. CLOSURE: all21 closure fixtures, contract-immutable, lawful frame, clause/frame negatives; all7 mode fixtures and7 root-composition fixtures. Ordinary-slots/positive runs entire file, including ordinary/PFC roots. Strong semantics exact N, useful successes and permitted modifies must hold. Source count2 in each Replace file, exact one caller selected; local PFC companion is not selected proof credit.
6. E1: union-constant/variable/raw-field, borrowed/by-value unsized controls and final docs. Common guards/masks/setter and argument_size remain4. Final complete expected set245+2ignored; no unassigned shared cases. Recheck all strong oracles/sensitivity if affected by a dependency reassignment.
7. F7: delayed_cache6 + delayed_scope2 plus all previous20 targeted units, same complete Quick. Journal/RAII units require actual nonzero selection. No old T1b allowlist or old JSON runner; mixed-vs-isolated research basis is explicit in ../f7/EXTRACTION-PLAN.md.

Exact head1 expected smoke expansion (full-name native compiletest selector; source fixture count12):

- `[expected] expected/function-contract/as-assertions/assert-postconditions.rs`
- `[expected] expected/function-contract/as-assertions/assert-preconditions.rs`
- `[expected] expected/function-contract/capture_load_checks_elided.rs`
- `[expected] expected/function-contract/capture_load_escaping_closure.rs`
- `[expected] expected/function-contract/capture_load_user_deref_fail.rs`
- `[expected] expected/function-contract/capture_load_user_deref_pass.rs`
- `[expected] expected/function-contract/clause_calls_check_target.rs`
- `[expected] expected/function-contract/clause_calls_check_target_fail.rs`
- `[expected] expected/function-contract/clause_context_no_assert.rs`
- `[expected] expected/function-contract/gcd_rec_contract_fail.rs`
- `[expected] expected/function-contract/gcd_rec_replacement_pass.rs`
- `[expected] expected/function-contract/gcd_rec_simple_pass.rs`

Function-contract smoke uses its original fixture flags/goldens; no added uninit flag. It is a bounded ordinary regression check, not direct CC entry-seeding qualification or a claim that the complete contract suite ran. QUICK-PLAN.json also enumerates all25 kani smoke selectors, the inherited17 JSON selectors and the exact expected selector list for every head.

On first full strong-oracle head5 run4 independent S5 sensitivity mutations using `--force-rerun`, same built tool, unique build base and source restoration between mutants. Pin each input/patch hash against final F; no stale expected-input hashes accepted. Clean selected cases PASS first. Each mutant must finish native verification with the intended outcome and make compiletest fail from that golden mismatch:

| Mutation | Completed native result | Required distinguishing mismatch |
|---|---|---|
|positive-remove-useful-assertion|SUCCESS N0|Missing outside==41 SUCCESS block|
|negative-extra-reached-failure|FAILED N2|Exact frame N1 rejects extra failure, intended user failure retained|
|negative-repair-user-write|SUCCESS N0|Missing outside-assigns FAILURE/N1|
|golden-invert-required-count|SUCCESS N0|Sanity-only N1 golden rejects actual N0|

Mutation compile/setup failure, timeout, cached/ignored selection, early unrelated Unsupported or a bare nonzero exit is INVALID detection. Keep all native output and original failure/consequence checks; no cover-summary can satisfy `SUMMARY` + `** N of`. Repeat on later affected heads and the full F7 Quick, preserving the recipe's4/4 check.

Always-upload artifacts must include actual compiletest build bases and per-test stdout/stderr, unit/suite counts, original argv/exits/termination reasons, source SHA/tree/manifest/dirty state before/after and clean/mutant outputs separately. Preserve original exit under aggregation; missing/partial output means NOT_RUN/UNKNOWN, never PASS. Don't keep obsolete `/tmp/...uninit-contract-oracles`, mode-boundary-results or composition paths as the only uploader. Recipe's grep/FAILED shortcut is not sufficient sensitivity acceptance; inspect completed native verdict/N and mismatch.

Previously distinguishing exact unchanged baselines may be referenced with their fixture/flag/semantic identities. New/altered negatives need a distinguishing observation; don't repeat every old baseline automatically. F6 controls must reject baseline false SUCCESS; final hook return must replace internal load_argument placeholder with sole explicit pairing Unsupported. Both read checks for Copy/padded holes are N2 in F, superseding historical prose N1.

Quick is intermediate regression/qualification, not three-platform Gate A, not formal proof credit. Accepted full F runs do not qualify heads1–6 automatically. All new source/overlay SHAs, CI runs, runtime outcomes and counts remain NOT_CREATED / NOT_RUN in this stage.
