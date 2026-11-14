# C2-S6 candidate CI — 61eb057b46 (not accepted yet)

Runs (ubuntu-24.04): candidate quick 43653703859 (CI-only 516941146f, `uninit-ci/c2-s6-cand`);
matched observation baseline 8d 43653700248 (CI-only 1baec10257, `uninit-ci/c2-s6-base-observe`) and
candidate 43653703827 (same commit 516941146f). Observation fixtures = exported
`tests/expected/uninit/marker-hook-calls/{ordinary-hook-return,ordinary-hook-scalar,fn-item-plain,fn-item-shadow-return}.rs`
from 61eb, run identically on both heads with `RUSTFLAGS="<compile-flags> --emit mir" kani <f> --keep-temps <kani-flags>`.

## Matched observation (baseline 8d → candidate 61eb)

| Fixture | Baseline 8d | Candidate 61eb |
|---|---|---|
| ordinary-hook-return | FAILED 1 of 141: placeholder (internal load_argument assert) | FAILED 1 of 143: "Kani does not support shadow transfers without a paired argument/return protocol." |
| ordinary-hook-scalar | SUCCESS 0 of 25 | SUCCESS 0 of 25 |
| fn-item-plain | SUCCESS 0 of 20 | SUCCESS 0 of 20 |
| fn-item-shadow-return | FAILED 1 of 111: explicit pairing Unsupported | same |
| companion legal-ordinary / maybe-uninit-argument-return | SUCCESS 0/365 / FAILED 1/176 (u16 read) | same |

Discriminating: the hook fix changes exactly the intended outcome.

## Candidate quick 43653703859 — FAILURE

- fmt / build / clippy: PASS. Units: delayed_cache 6/0, delayed_scope 2/0, immutable 9/0, marker_category_tests 1/0.
- kani 24/0; ui 17/0; script 2/0; json-handler 17/0.
- expected: 237 passed / **8 failed** / 2 ignored (pre-existing fixmes). All 9 new marker-hook-calls fixtures PASS.
- 4/4 S5 sensitivity mutations DETECTED (`--force-rerun`).

Failures (per-test compiletest sections in this directory, `*.compiletest.txt`):
1. `copy-source-arguments/{arg0,arg1}-{hole,initialized}.rs`: compile error E0423 — custom MIR `Copy(source)`
   is not a constructor in `core::intrinsics::mir` (copy operands are written as plain places; `Move(..)` is explicit).
2. `padded-slice-extents/{raw,borrowed}-{hole,initialized}.rs`: verification runs; initialized variants SUCCESSFUL
   (0 of 199 / 0 of 197), hole variants FAILED 2 of 215 / 2 of 213 with both
   `Reading from an uninitialized pointer of type `*const u8`` and `... of type `u8`` at `std::ptr::read::<u8>`
   (expected file had 1 failure, only `u8`). Expected matcher also missed the useful-assertion blocks
   (check names/numbering differ from the golden). Exact actual check lists are in the saved sections.
