# Slice02 prepared exact-head CI request

Source `b0a5a4fff9122ae4dabcc9808568c0d15fbe9b12`, tree `03e33b5a3a8b3aa1fd5505467bbe869d1001b44e`,
parent accepted1 `d82752c8bc878398e672bffaa631ca6a28430acc` (NO_REGRESSION, run43696666260).
Prepared only: worker15 owns independent review/CI overlay; dispatch/push remain coordinator-only.
No local builds, native checks, overlay, push or CI occurred in this writer session.

Use accepted recipe `0998b98867:.github/workflows/uninit-quick.yml` and an exact-parent CI-only overlay,
with source/tree/hash identities before and after. Source workflows remain intact; remove stock workflows
only in overlay. ubuntu-24.04, RUST_TEST_THREADS=2, job cap120min, per-test2400s, no auto retries.
fmt -> build-dev -> clippy workspace/tests -D warnings -> units -> every TEST-MANIFEST selector.
Preserve native solver/checks, original directives/goldens and fixture-specific object bits;
no global object-bits setting, contract uninit flag addition or new test exclusion.

Units, separate filters:

- `cargo test -p kani-compiler active_call_tests`: exactly9 passed, 0 failed/ignored.
- `cargo test -p kani-compiler immutable_allocations::tests`: exactly9 passed, 0 failed/ignored.

TEST-MANIFEST.json retains the complete accepted1 regression manifest and adds all six
immutable-descriptor-coalescing fixtures, unchanged .rs/.expected pairs from F. Exact selectors,
flags and hashes are recorded. Groups overlap; deduplicate only by exact suite/mode/selector.
Invoke compiletest with each manifest suite/mode and `--exact --force-rerun --no-fail-fast --timeout 2400`,
using `selectors[].selector` verbatim. Native discovery/unit counts must agree; zero units is failure.

| Deduplicated suite | Selectors | Existing ignores | Expected passes if all succeed |
|---|---:|---:|---:|
| kani | 53 | 3 | 50 |
| expected | 225 | 6 | 219 |
| ui | 17 | 0 | 17 |
| script-based-pre | 3 | 0 | 3 |
| json-handler | 17 | 0 | 17 |
| std-checks | 2 | 0 | 2 |

317 selectors, 308 expected passes/9 existing ignores, plus18 compiler units. Counts are static
expectations, not results. All present uninit tests, full FunctionContracts/function-contract with
original flags and all upstream uninit/delayed-UB selectors remain required.
The six new fixtures must reach their three useful value SUCCESS assertions and exact N0 goldens;
coalescing units must preserve false masks, alias-order behavior and genuine descriptor rejection.

SLICE.json and ORACLE-DELTA.json record sixteen absent owner2 whole fixtures, first runnable3/4,
and eleven later-owner mixed/contract consumers on3/4/5. Do not add them early, filter already-present
failures, substitute units for integration, or treat historical F gates as intermediate qualification.
Parent1 integration obligations on4/5 stay pending with their own immutable part hashes/receipts.

Upload original argv/exits/termination reasons, native discovery/counts, exact fixture/unit output and
source/tree/manifest identities with always, preserving actual build-base/output paths. Partial,
missing or timeout output is NOT_RUN/UNKNOWN. Any false SUCCESS, new ordinary regression, lost check
or extra Unsupported is STOP; never weaken goldens or add ignores to obtain a pass.
No F7 structural isolation, Gate A or SmallSort proof credit follows from this request.
