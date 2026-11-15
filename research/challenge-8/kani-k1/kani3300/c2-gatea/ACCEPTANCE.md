# C2 Gate A — ACCEPTED (run 43665002636)

Coordinator acceptance, 2026-11-15. Fork Tiramisu-Cake/kani, push branch `ci/kani3300-c2-gatea-w15-r2`.

- Export (FREEZE): `ad499e41dd2db9ccd432f89721638a1f3a0bbd44`, tree `9829702c1aa0ecb73c860fc0ad5451757917d6cb`.
- Control overlay: `39bcdd7ad51dc169f75a9974e43717205553bad0` (worker15 overlay e795403859 + push trigger + bash 3.2 owner guard + control checkout beside export; CI-only, no export change).
- Run 1 (43661248113 Linux rows + 43661668298 macOS row; see COORDINATOR-DISPATCH.md, `run1-infra/`) was an infrastructure failure (nested Cargo workspace at std-checks), not a C2 result.

## Rows

| row | job | duration | status | script exit | stages | source clean / 22 hashes | events | runtime required_missing |
|---|---|---|---|---|---|---|---|---|
| ubuntu-24.04 (X64) | success | 2136 s | COMPLETE_EXIT_ZERO_REQUIRES_REVIEW | 0 (EXIT) | 33/33 ordered | clean / ok | complete, 132 | none |
| ubuntu-24.04-arm (ARM64) | success | 2012 s | COMPLETE_EXIT_ZERO_REQUIRES_REVIEW | 0 (EXIT) | 33/33 ordered | clean / ok | complete, 132 | none |
| macos-15 (ARM64) | success | 3855 s | COMPLETE_EXIT_ZERO_REQUIRES_REVIEW | 0 (EXIT) | 33/33 ordered | clean / ok | complete, 132 | none |

Aggregate `kani3300-gatea-aggregate-v1`: three coherent rows, identical export/tree/overlay/run identities, `problems: []`.
Stage order identical on all rows. `problems` and `observer_errors` empty on every row.
Runtime per row: CBMC/goto-instrument 6.11.0, Kissat 4.0.1, rustc 1.101.0-nightly (7189d39d9 2026-10-22), Kani 0.68.0; binary SHA-256 differ by architecture as expected. UNKNOWN (not required): cadical, minisat, kani, kani-compiler-rt.

## Counts (passed/failed/ignored) — identical on all three rows; C1b Gate A for comparison

| stage | C2 | C1b | delta |
|---|---|---|---|
| unit:cprover_bindings | 42/0/0 | 42/0/0 | |
| unit:kani-compiler | 76/0/0 | 63/0/0 | +13 passed |
| unit:kani-driver | 215/0/0 | 214/0/0 | +1 passed |
| unit:kani_metadata | 4/0/0 + 2/0/1 | same | |
| unit:compiletest | 0/0/0 + 2/0/0 | same | |
| unit:kani-cov | 2/0/0 | same | |
| unit:kani | 6/0/0 + 25/0/2 | same | |
| unit:kani_macros | 7/0/0 | 4/0/0 | +3 passed |
| suite:kani | 654/0/23 | 647/0/23 | +7 passed |
| suite:expected | 744/0/13 | 686/0/13 | +58 passed |
| suite:ui | 172/0/0 | 168/0/0 | +4 passed |
| suite:std-checks | 5/0/0 | 5/0/0 | |
| suite:firecracker | 0/0/2 | 0/0/2 | |
| suite:prusti | 8/0/0 | same | |
| suite:smack | 40/0/0 | same | |
| suite:cargo-kani | 72/0/0 | same | |
| suite:cargo-ui | 30/0/0 | same | |
| suite:script-based-pre | 102/0/0 | 99/0/0 | +3 passed |
| suite:coverage | 20/0/0 | same | |
| suite:cargo-coverage | 2/0/0 | same | |
| suite:kani-docs | 13/0/0 | same | |
| suite:kani-fixme | 22/0/655 | 22/0/648 | +7 ignored |
| suite:json-handler | 17/0/0 | 11/0/0 | +6 passed |

Non-count stages (cbmc, kissat, fmt, build-dev, compiletest-config, build-cov, firecracker-codegen, cargo-smoke, cargo-clean, warnings-build): EXIT_ZERO on all rows.

## Ignore / zero-suite review

- Ignored counts in kani (23), expected (13), firecracker (2), unit:kani_metadata (1), unit:kani (2) equal C1b Gate A: no new ignore.
- kani-fixme +7 ignored = the +7 new non-fixme tests in tests/kani (fixme mode ignores every non-`fixme` test; 654+23 = 677 = 655+22). Fixme passes unchanged (22).
- firecracker 0 passed / 2 ignored and unit:compiletest first binary 0/0/0 are unchanged from C1b (existing upstream layout).
- No filtered tests on any stage. All deltas are additions from C2 (new controls, unit tests, json-handler fixtures); no test removed.
- Count-level comparison only: the ignored test names are not listed in the receipts; equality of counts with unchanged ignore markers in the frozen tree is the evidence.

## Verdict

All acceptance conditions of FULL-GATE-REQUEST.md hold: three complete exact-source receipts, 33 ordered stages, original script exit 0, complete bounded event streams, required identities known, clean source before/after, no unexpected failures, ignores reviewed. **C2 Gate A ACCEPTED on freeze `ad499e41dd`.**
This is regression evidence only: `formal_proof_credit: NOT_ESTABLISHED`; no publication authorization follows.

## Files

`run2-43665002636/{aggregate.json, <row>/receipt.json, <row>/lifecycle.json}` (event logs remain in the run artifacts, 14-day retention).
SHA-256: macos receipt `f4730aea29dd21ae…`, ubuntu X64 receipt `7a2eef40ca0abc75…`, ubuntu arm receipt `1b33f58ece8a632a…`, aggregate `7215198f41fe35f9…`.
