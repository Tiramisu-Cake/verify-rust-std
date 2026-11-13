# CBMC ZST-BITS2EXPR — CI result (coordinator, 2026-11-13)

Fork https://github.com/Tiramisu-Cake/cbmc, branch `ci/zst-bits2expr-20261113-r2`, run
https://github.com/Tiramisu-Cake/cbmc/actions/runs/43334186094 (ubuntu-24.04, gcc-13, CMake Release, minisat2).

- Source/fix commit `cd41a5c74b0c42edf4f08834b3e2808dd3344cab` (parent develop `107a1e504c`), one-line change in
  `src/util/simplify_utils.cpp` (`*el_size_opt > bitst{0}` → `>= bitst{0}`) + 13 regression dirs + `unit/util/zst_bits2expr.cpp`.
- CI-only commit `91062c7dba9da7541c0e607a3735482e38d28d36` = worker's `33235a4ef1` + coordinator harness fix:
  no RLIMIT_FSIZE on build steps (r1 run 43330853783 died with SIGXFSZ while linking libgoto-instrument-lib.a);
  format oracle accepts empty `git-clang-format --diff` output (r1 format exit 0, empty diff = clean).
- Earlier run 43329473713 failed on test-delta SHA mismatch and a real clang-format diff (fixed by worker R1).

| Variant | Build | Focused 13 | Neighbour regression 13 | Unit focused 3 | Unit `[util]` rest |
|---|---|---|---|---|---|
| baseline = develop + tests only | BUILT | 12 FAILED, memcpy control passes | NOT_RUN | NOT_RUN | NOT_RUN |
| fix | BUILT | 13/13 oracle met (incl. intended negative) | 13/13 (Array_*, Empty_struct1-3, Struct_Bytewise1, byte_extract1, empty_compound_type2-4, union-unequal-element-size1) | 3/3 | 205/212 — the 7 failures are all `unit/util/piped_process.cpp` (z3 subprocess tests: response "Launching" instead of "sat"; z3 not installed on the runner), unrelated to the change |

Not run: full `ctest` regression, other platforms, Kani replay, owner literal / Kani-like fixtures summary to be checked.
No issue/PR opened.

## Z3 util follow-up (2026-11-13)

Run https://github.com/Tiramisu-Cake/cbmc/actions/runs/43341504085, CI-only `b794c3c99d` (parent 91062c7dba), fix-only
build of `cd41a5c74b`, Ubuntu z3 4.8.12 installed (preflight PASS). `[util]~[zst-bits2expr]`: 212 cases, 210 passed.
The seven z3 piped_process failures are gone. Remaining 2:
- `Creating a sub process with a binary that doesn't exist` (unit/util/piped_process.cpp:72, expected error text not found);
- `Scenario: run() error reporting` (unit/util/run.cpp:45, `result != 0` got 0).
Both test subprocess error handling and do not touch bits2expr; baseline util was not run, so "pre-existing on develop"
is NOT established (likely environment/harness: the runner executes tests under its own preexec/rlimits).
