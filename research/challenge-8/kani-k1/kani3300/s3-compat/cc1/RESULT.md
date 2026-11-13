# CC1 — prepared, NOT_RUN in CI

Worker14; 2026-11-13; only issued CC1 scope.
Source base: fef9e0f38c0c645027f20223a562c7008969d9a9.
Source HEAD/tree and all file hashes: INPUTS.json.
Clone: /root/kani-fix-3300-cc1; branch fix/kani-3300-cc1.

Added exact active Instance/body keys, fresh per-root context and bounded cycle reason.
Cycle errors propagate as Err; partial graphs never leave a failed run or enter global joins.
Delayed pass emits normal Unsupported at that entry root and continues other roots.
Completed callees can be rerun with different initial graphs; no summary cache added.
S3 registration/discarded handling and all existing transfer/check/layout policies preserved.
Added7 helper unit controls and6 Rust fixture files (9 new harness occurrences).

Python static audit: PASS;270 protected files and8 oracle input hashes unchanged.
Existing oracle Python checker:21/21 PASS (mocked/offline, no Rust subprocess).
Authorized scratchpad rustfmt and git diff --check: PASS.
Rust typecheck / helper units / actual controls / CI: NOT_RUN.
Actual cycle path, original crash cause and model/property bindings: UNKNOWN.
Independent review: PENDING coordinator; nested agents forbidden by issued task.
CI-REQUEST.md and CI-ROOTS.json specify bounded coordinator-only requests.
No cargo/rustc/Kani/CBMC/Miri/builds, CI, push or raw evidence downloads performed.
Cloud $0. CC2/CC3 not started; mode-findings history unchanged.
Bool/layout regressions remain BLOCKED; recursive ordinary Unsupported is still a release blocker.
Part1 publication NO-GO; common Quick/strong suites and full gates NOT_RUN here.
