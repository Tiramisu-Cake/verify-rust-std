# C2-S6 accepted — C2 frozen candidate

**Frozen source:** `ad499e41dd2db9ccd432f89721638a1f3a0bbd44`, tree `9829702c1aa0ecb73c860fc0ad5451757917d6cb`.
Fork refs: `fix/kani-3300-c2-s6` and `freeze/kani-3300-c2` (both at ad499e41). Do not change source/tests/docs under this freeze.

Lineage on top of S5 `8d67298c4`:
- `61eb057b4` Refine shadow transfer boundaries and initialization controls (worker14: hook predicate fix, 17 controls, docs, hygiene)
- `503d7f0b1` Correct custom MIR copy operands and initialization test oracles (worker14, after CI 43653703859)
- `ad499e41d` Format padded slice extent tests (coordinator, rustfmt only)

Delta 8d..ad49: 73 files, +865/−65. Upstream base U = 0aac16ef62 (+ B1); 18 commits on top of U.
Subtree trees at ad49: kani-compiler c738897777, library eeae80b128, kani-driver f05085b98b, tests 945332aacc,
docs edb41c0886, cprover_bindings b34b353024. Pins: nightly-2026-10-23, CBMC 6.11.0, Kissat 4.0.1.

## Qualification — run 43656920767 (ubuntu-24.04, CI-only commit 0998b98867, `uninit-ci/c2-s6-cand3`)

All steps success: fmt, build, clippy -D warnings; units delayed_cache 6/0, delayed_scope 2/0, immutable 9/0,
marker_category_tests 1/0; kani (Uninit, Quantifiers, TailCall) 24/0; expected (uninit, quantifier-capture,
arbitrary) 245/0 + 2 pre-existing fixme ignored; ui 17/0; script-based-pre 2/0; json-handler (all) 17/0;
4/4 S5 sensitivity mutations DETECTED with `--force-rerun`.

Hook fix discrimination: matched observation 43653700248 (8d) vs 43653703827 (61eb, same hook fixtures unchanged
through ad49): ordinary-hook-return placeholder internal assert → one explicit pairing Unsupported; scalar hook,
fn-item plain/shadow-return, companions unchanged. See `../ci-43653703859/CI-RESULT.md`.

History: 43653703859 (61eb) — 8 new test-authoring failures + fmt failure; 43655819395 (503d) — tests green, fmt failure.

Not covered here (by design): function-contract suites (none use `-Z uninit-checks`; predicate is uninit-only),
full kani-regression, Gate A on 3 platforms (**NOT_RUN**, next coordinator step on this exact SHA), SmallSort/SEL1 replay.
