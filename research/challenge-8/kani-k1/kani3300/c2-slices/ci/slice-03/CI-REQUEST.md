# Slice 03 LAYOUT-RAW — exact-head CI request

**READY_LOCAL_ONLY for coordinator.** Overlay
`a2a533e0877e840a73b5805e039686a1bad61d87`, exact parent/source
`d0345ddf4f70d10caf5ee34ddca402867264379e`, source tree
`8ac48a5660a94de062919ebcf80fdcdef2cc2f03`.
Source parent is accepted slice2 `932fb8395a58f8c86c0d702ba2cae835823b2962`,
run43701587141. No rebase or source delta. Input g0
`fc82cfd8b40d653b71ff2b2ba383682bc185165e`.

Worktree `/root/kani-fix-3300-c2-slices-w15`, branch
`uninit-ci/c2-slices-03-w15`. [Independent review](../../reviews/slice-03.md):
PASS_STATIC_ONLY, no blocking findings. Push/dispatch remain coordinator-only.
Local native builds/tests, push, dispatch and CI results are NOT_RUN; Cloud $0.

## Recipe and exact selection

Use committed `.github/workflows/uninit-quick.yml`. Accepted slice2 overlay
`536f1d20d127987cdd860bc6367acc9fff90c5cb` / run43701587141 is the recipe.
Runner is byte-identical to its `slice02_ci.py`, renamed `slice03_ci.py`.
Only config/manifest pins, workflow stage names/count and artifact directory change.
Stock workflows are removed only in the CI overlay. Every non-CI Git entry,
including production/runtime/tests/docs/dependency pins, equals exact source3.

ubuntu-24.04, RUST_TEST_THREADS=2, job120min, per-fixture2400s, no auto retries.
Order: fmt → build-dev → workspace/tests clippy `-D warnings` → ActiveCalls9 →
immutable9 → six cumulative suites. Original flags, solver, checks, per-fixture
object-bits and goldens remain; no added uninit flags on stock contracts.

| Suite / mode | Discovery | Passed if green | Existing ignored |
|---|---:|---:|---:|
| kani / kani |53|50|3|
| expected / expected |244|238|6|
| ui / expected |17|17|0|
| script-based-pre / exec |3|3|0|
| json-handler / exec |17|17|0|
| std-checks / cargo-kani |2|2|0|

Total336 selectors,327 passes +9 pre-existing ignores expected. ActiveCalls and
immutable filters each require exactly9 passed/0 failed/0 ignored, by full native
names; zero or substituted selection fails. These are expectations, not observations.
All317 inherited selectors/identities remain. The19 additions match Quick head3:
four u8 mixed raw/eq operand orders plus15 immutable masks/promoted/static/subrange/
relocation fixtures. Common expected inventory112 =110 passes +2 old ignores.
Full inherited FunctionContracts/function-contract and upstream/B1 uninit/delayed-UB
remain selected. No newly present test is filtered after a failure.

[CI-REQUEST.json](CI-REQUEST.json) gives exact argv, selector/unit names, hashes and
nineteen fixture/golden identities; embedded manifest is byte-identical to
[source TEST-MANIFEST](../../slice-03/TEST-MANIFEST.json). Each suite uses
`--exact --force-rerun --no-fail-fast --timeout 2400` and explicit external
build-base/native logfile.

## Required native review

The19 unchanged F goldens prescribe10 SUCCESSFUL and9 FAILED outcomes and use
literal matches, not exact property counts. Inspect actual per-fixture native
output before acceptance; runner count match alone cannot close these obligations.

- u8 mixed raw/eq stack/promoted in both orders: useful equality assertions and
  both checked raw operands reach SUCCESS where emitted.
- Direct/helper promoted legal: useful assertion and both operand byte checks
  succeed. Left/right holes: intended operand's extent check fails, opposite
  operand check succeeds; earlier UB, unrelated Unsupported or extra failure
  is not the intended distinction.
- Immutable zero/empty/static/relocation/subrange controls retain intended
  initialized/hole distinction and diagnostics. `immutable-subrange-legal`
  deliberately expects known conservative FAILED with `[u8; 3]` diagnostic;
  never report it as a positive SUCCESS.

All nine deferred owner3 fixtures stay PENDING on4: four raw-MU mixed, nested
Pat data/padding, nested enum same/different padding and whole raw-eq-uninit.
Their source ownership remains3; u8/promoted controls do not qualify nested
offsets. Inherited owner1 integration remains pending4/5 and later owner2
consumers retain their pending obligations. Storage units/helpers belong4,
closure layout5, F7 units7.

## Evidence and static checks

Always upload `c2-slices-03-evidence/`, including source before/after identities,
inputs/manifest, original argv/exits/termination reasons, native stdout/stderr,
suite logs and actual compiletest build bases with per-fixture outputs. Unstarted
stages are explicit NOT_RUN/null exit. Missing/partial output, new ignores,
count/name mismatch and per-fixture timeout fail the runner. Original failures
are retained; successful runner status still says REQUIRES_REVIEW.

Local checks: [SOURCE-VALIDATION](SOURCE-VALIDATION.json) confirms22 ownership parts,
19 exact-F pairs,649 manifest file hashes and all inherited selectors;
[SEAM-VALIDATION](SEAM-VALIDATION.json) reports bounded static PASS/errors[];
[STATIC-VALIDATION](STATIC-VALIDATION.json) records19 Python synthetic checks PASS,
accepted runner byte identity, clean overlay and3930 protected source entries.
Review independently checked imports/impls/signatures/call sites; no compile PASS
is claimed. [overlay.patch](overlay.patch) is the exact CI-only patch.

Quick is intermediate regression/target qualification, not three-platform Gate A
or independent formal proof credit. No stage4–7 implementation or CI is authorized
by this request. Coordinator accepts and dispatches this exact overlay separately.
