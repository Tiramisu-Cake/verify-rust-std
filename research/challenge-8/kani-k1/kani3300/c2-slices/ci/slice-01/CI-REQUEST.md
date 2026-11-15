# Slice 01 ANALYSIS — exact-head CI request

**READY for coordinator CI preparation.** Local overlay `4f5dc3732c8fbaa94c814c41d184534148a1d312` (tree `464131d91d8568c589a38fdd90ccc0da0e3143c3`), exact parent/source `d82752c8bc878398e672bffaa631ca6a28430acc` / source tree `c7024fb95c9cbb8ca2b1091056b9d5aa9c8cea9b`; source parent is unchanged B1 `6fe484b30043b3696b5f1ccc4bea0e42891ad012`.

Worktree `/root/kani-fix-3300-c2-slices-w15`, branch `uninit-ci/c2-slices-01-w15`. g0 input `0a6e3005d10942b2f7169f07d8d138c5911fcf8f`. No local Rust builds, push, dispatch or new CI run. Cloud $0.

**Qualification: NO_REGRESSION.** Head1 integration is PENDING on cumulative heads4/5 under mandatory variant C. Full deferred source/golden/part hashes and closure criteria remain in [DEFERRED-OBLIGATIONS](../../slice-01/DEFERRED-OBLIGATIONS.json); a green aggregate or ActiveCalls9 does not close them.

[Independent review](../../reviews/slice-01.md): source static PASS; four inherited `unresolved-calls` changes are comment-only, with code/flags/goldens intact. They belong to this descendant and do not modify submitted B1/#5172.

Use the committed `.github/workflows/uninit-quick.yml` only on the exact overlay; fork push/dispatch belongs to the coordinator. It follows accepted recipe `0998b98867` (run43656920767): ubuntu-24.04, 120-minute job, per-test2400s, RUST_TEST_THREADS=2, no retries. fmt → build-dev → workspace/tests clippy `-D warnings` → ActiveCalls9 → six deduplicated suite invocations. Native fixture flags/checks/solver/goldens remain unchanged; no extra uninit flag on contract tests. Source workflows remain intact in the source head; stock workflows are removed only in the overlay.

The complete stage1 manifest supersedes the old 12-file expected contract smoke. Every selector in [TEST-MANIFEST](../../slice-01/TEST-MANIFEST.json) is included: common Quick, all present upstream uninit/delayed-UB (including verify_std_cmd and the two std-checks cargo selectors), all22 inherited B1 controls, full kani FunctionContracts25 and expected function-contract138. Exact arrays, argv and overlapping group counts are in [CI-REQUEST.json](CI-REQUEST.json).

| Suite / mode | Static discovery | Required passed if green | Existing ignored |
|---|---:|---:|---:|
| kani / kani | 53 | 50 | 3 |
| expected / expected | 219 | 213 | 6 |
| ui / expected | 17 | 17 | 0 |
| script-based-pre / exec | 3 | 3 | 0 |
| json-handler / exec | 17 | 17 | 0 |
| std-checks / cargo-kani | 2 | 2 | 0 |

Total:311 selectors,302 passed/9 ignored if green; ActiveCalls units exactly9 passed/0 failed/0 ignored. These are static expectations, not observations. Zero/missing/mismatched native selection or new ignore fails the runner. Existing ignores remain in the original source.

`actions/upload-artifact` runs with `always()` and preserves `${runner.temp}/c2-slices-01-evidence/`: original command argv/exits/termination reasons/stdout/stderr, actual native test names/counts/logfiles, per-fixture outputs at explicit external `build-tests/<suite>` paths, test manifest and source snapshots before/after. Each stage begins as explicit NOT_RUN; missing/partial/interrupted/timeout output cannot be PASS. Original child-verifier receipts are not added to unchanged compiletest; its normal per-fixture outputs and failure diagnostics are retained.

Both source snapshots enforce clean worktree (including untracked paths), exact overlay parent/source tree/B1 ancestry, CI-only commit delta, and all3878 protected source entries. Source-guard failure prevents later build/test steps. After-snapshot and artifact steps still run on failure.

Stop on an ordinary regression, false SUCCESS, extra Unsupported, lost assertion, weakened golden, source mismatch or incomplete execution; preserve the failing outcome for review. No native result is established by this preparation. This is intermediate regression/unit CI, not Gate A, F7 structural qualification or SmallSort proof credit.

Local validation:17 synthetic Python runner checks PASS, manifest input/golden hashes checked against exact source, complete contract and B1 selector coverage, Python AST/YAML parse and git diff --check PASS. Rust parsing/fmt/build/clippy/unit/compiletest/CI are NOT_RUN. [Static validation](STATIC-VALIDATION.json), [CI-only patch](overlay.patch).
