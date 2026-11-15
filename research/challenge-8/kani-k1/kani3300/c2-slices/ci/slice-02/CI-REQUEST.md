# Slice 02 IMMUTABLE — exact-head CI request

**READY_LOCAL_ONLY for coordinator.** Overlay `83550218ea0dc6df4b5dbf78dcbf244a56645c2f`,
tree `e69afc2eafcaced852c61dead92e5212303cb9c9`, exact parent/source
`b0a5a4fff9122ae4dabcc9808568c0d15fbe9b12`, source tree `03e33b5a3a8b3aa1fd5505467bbe869d1001b44e`.
Source parent `d82752c8bc878398e672bffaa631ca6a28430acc` is the accepted slice1 from run43696666260;
its parent remains B1 `6fe484b30043b3696b5f1ccc4bea0e42891ad012`. No rebase or source delta.

Worktree `/root/kani-fix-3300-c2-slices-w15`, branch `uninit-ci/c2-slices-02-w15`.
Input g0 `ff3ce29e4f6694f28b0d6fcf025e70cfeae8f378`. Source review:
[worker15 PASS_STATIC_ONLY](../../reviews/slice-02.md). Push/dispatch belong to the coordinator;
no local Rust build, CI invocation or publication has occurred. Cloud $0; CI run NOT_RUN.

## Recipe and commands

Use this committed `.github/workflows/uninit-quick.yml` on the exact overlay. It extends the accepted
slice1 overlay `4f5dc3732c8fbaa94c814c41d184534148a1d312` / run43696666260, itself based on
`0998b98867932b307bd99109dc8f2741cac507b1`. Changes to that recipe are the source/manifest pins,
stage2 names/artifact directory, a separate immutable9 unit action, and the source-parent diagnostic
wording (the parent of source2 is source1, not B1). No production/test/doc/dependency changes.
Stock workflows are deleted only in the overlay; source retains them.

ubuntu-24.04;120-minute job; per-fixture2400s; RUST_TEST_THREADS=2; no auto retries.
Order: fmt → build-dev → workspace/tests clippy `-D warnings` → ActiveCalls9 → immutable9 → six suites.
Original flags, solver, checks, per-fixture object-bits and goldens remain unchanged. No global object-bits
or added uninit flag on stock contract tests; no new ignores or failure filtering.

Exact argv, source/golden identities, selectors, units and hashes are in [CI-REQUEST.json](CI-REQUEST.json)
and the embedded byte-identical [stage2 TEST-MANIFEST](../../slice-02/TEST-MANIFEST.json).
Each compiletest invocation uses `--exact --force-rerun --no-fail-fast --timeout 2400`, explicit external
build-base and native logfile. All inherited311 selectors remain; the only6 additions are the whole
immutable-descriptor-coalescing fixtures: direct-first, nested-first, both volatile variants,
aggregate-constant-initializer and const-fn-initializer. Whole current `uninit` is selected.

| Suite / mode | Static discovery | Required passed if green | Existing ignored |
|---|---:|---:|---:|
| kani / kani |53|50|3|
| expected / expected |225|219|6|
| ui / expected |17|17|0|
| script-based-pre / exec |3|3|0|
| json-handler / exec |17|17|0|
| std-checks / cargo-kani |2|2|0|

Total317 selectors:308 intended passes/9 unchanged ignores. ActiveCalls exactly9 passed/0 failed/0 ignored,
immutable_allocations exactly9/0/0, separately checked by full native test names. These are expectations,
not observations. Native zero/missing/substituted selection, new ignores, count mismatch or partial output fails.
Common expected group is93 (91+2ignored);225 includes full original function-contract and upstream inventory.
Full FunctionContracts25, function-contract138, B1 controls and all accepted slice1 regression inputs remain.

## Evidence and remaining obligations

Always-upload directory `${runner.temp}/c2-slices-02-evidence/` contains original command argv/exits/
termination reasons/stdout/stderr, normal per-fixture outputs at `build-tests/<suite>`, native names/counts/
logfiles, inputs and manifest, and source before/after snapshots. Every command starts as explicit NOT_RUN.
Runner failure/timeout/interrupt/partial/missing outputs cannot yield PASS. The unchanged compiletest retains
its normal native outputs; no new individual child-verifier receipt instrumentation is claimed.

Both snapshots enforce clean worktree including untracked paths, exact overlay parent/source SHA/tree,
source parent, CI-only delta and3892 protected source entries. After-snapshot and upload run with `always()`.
Local successful before/after snapshot checks agree on all entries. As in accepted1, setup may initialize
submodules only at their pinned commits. Source-guard failure prevents build/test stages.

Qualification is **TARGETED_IMMUTABLE_AND_CUMULATIVE_REGRESSION** on source2. Six coalescing controls must
reach all useful SUCCESS assertions; immutable9 must preserve exact masks, descriptor conflicts, alias
qualification/refusal and reset-edge semantics. No actual native negative outcome is established here.

The16 owner2 deferred whole fixtures remain PENDING:15 masks/promoted/static/subrange/relocation cases
on3; immutable-masks/copy-hole on4. Eleven later-owner immutable consumers remain on3/4/5, including
contract-immutable on5. [SLICE.json](../../slice-02/SLICE.json) records exact paths, hashes, prerequisites,
assertions and intended negatives; [CI-REQUEST.json](CI-REQUEST.json) indexes every deferred fixture.
Do not introduce early raw_eq Unsupported as a replacement oracle or pretend these absent fixtures ran.
Parent [analysis obligations](../../slice-01/DEFERRED-OBLIGATIONS.json) stay PENDING4/5.
Aggregate exit0/units and historical full-F gates cannot close those obligations.

STOP on ordinary regression, false SUCCESS, extra Unsupported, lost assertions/weakened oracle,
source identity mismatch, or incomplete native execution. This is not three-platform Gate A,
F7 structural isolation, all-SmallSort verification or formal proof credit.

## Local validation

[STATIC-VALIDATION.json](STATIC-VALIDATION.json):52 owner parts/hashes and exact extraction PASS;
all source/golden/manifest identities and inherited selections checked; protected future scopes unchanged;
Python AST/YAML and git diff --check PASS;19/19 Python synthetic runner checks PASS, including exact9 immutable,
error/timeout/partial/missing/NOT_RUN and source mismatch paths. [overlay.patch](overlay.patch) pins the CI delta.

NOT_RUN: Rust parse/fmt/build/clippy, native units/compiletest/Kani/CBMC, docs build, CI, push, dispatch.
Coordinator acceptance must cite the actual exact-head run; preparation itself establishes no runtime result.
