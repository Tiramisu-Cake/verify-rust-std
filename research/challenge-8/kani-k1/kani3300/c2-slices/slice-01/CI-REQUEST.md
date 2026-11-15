# Slice1 exact-head CI request (coordinator / worker15 only)

Source `d82752c8bc878398e672bffaa631ca6a28430acc`, tree `c7024fb95c9cbb8ca2b1091056b9d5aa9c8cea9b`, parent existing B1 `6fe484b30043b3696b5f1ccc4bea0e42891ad012`.
Prepared request only: no CI overlay, push, dispatch, local build or native execution in this session.

Qualification: **NO_REGRESSION**. Integration **PENDING on heads4/5**; exact source/golden/part hashes and closure conditions are in SLICE.json and DEFERRED-OBLIGATIONS.json.

Use accepted recipe `.github/workflows/uninit-quick.yml` @0998b98867 with an exact-parent CI-only overlay. Stock workflows remain in source. ubuntu-24.04; RUST_TEST_THREADS=2; job cap120min; per-test2400s; no auto retries. fmt -> build-dev -> clippy workspace/tests -D warnings -> ActiveCalls9 -> all manifest selectors. Preserve solver/checks, original per-test flags/object-bits; no extra uninit flag on contract tests.

TEST-MANIFEST.json supersedes the stage0 bounded smoke list for this source head. Every listed selector is required; groups overlap and can be deduplicated by exact suite/mode/selector. Static counts are discovery expectations, not observed passes. Native ignored counts must match existing directives/paths; zero selected units is failure.

| Group | Static selectors | Existing path ignores |
|---|---:|---:|
| common_kani | 24 | 0 |
| common_expected | 87 | 2 |
| common_ui | 17 | 0 |
| common_script-based-pre | 2 | 0 |
| common_json-handler | 17 | 0 |
| full_FunctionContracts | 25 | 3 |
| full_function_contract | 138 | 4 |
| upstream_uninit_delayed_expected | 34 | 2 |
| upstream_uninit_delayed_kani | 15 | 0 |
| upstream_uninit_delayed_script-based-pre | 2 | 0 |
| upstream_uninit_delayed_std-checks | 2 | 0 |
| upstream_uninit_delayed_ui | 9 | 0 |

Compiler unit request: `cargo test -p kani-compiler active_call_tests` -> exactly9 tests, 9 passed/0 failed/0 ignored required. This does not exercise compiler MIR integration.

For each group invoke compiletest with its manifest suite/mode, `--exact --force-rerun --no-fail-fast --timeout 2400`, and the exact full selector strings in `selectors[].selector`. Retain all original flags/goldens. Run full kani FunctionContracts and full expected/function-contract; the old12 expected smoke list is insufficient. The upstream uninit inventory also reaches verify_std_cmd and std-checks/std expected selectors via their existing uninit settings; preserve their native cargo/exec modes.

Upload original argv, exit, termination reason, native discovery/counts, unit and fixture output, and source/tree/manifest/dirty identities before and after with always. Preserve actual compiletest output/build-base paths; no stale Part1 JSON-only artifacts. Missing/partial/timeout output is NOT_RUN/UNKNOWN, not PASS. A reached ordinary regression, new false SUCCESS, extra Unsupported or lost assertion is STOP; no new ignore/filter/golden updates.

Worker15 owns independent review and CI-only overlay. ORACLE-DELTA.json supplies pending stage0-map refresh items without editing its research area. No new Gate A, SmallSort proof or structural F7 credit is claimed.
