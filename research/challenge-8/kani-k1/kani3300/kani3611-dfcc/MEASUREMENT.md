# kani#3611 — SAT size vs --object-bits on upstream main (coordinator, 2026-11-14)

Kani upstream main `0aac16ef62da9e9d5645782d458593e5d78143ba` (no patches), CBMC 6.11.0, CaDiCaL default.
Fork Actions run 43605710505 (ubuntu-24.04), CI-only commit 94ffc77cc7 (workflow `workflow-scaling.yml` here).
Command: `kani tests/expected/function-contract/interior-mutability/whole-struct/refcell.rs -Z function-contracts
-Z unstable-options --cbmc-args --object-bits B`. All runs VERIFICATION SUCCESSFUL, exit 0.

| B | variables | clauses | Convert SSA | max RSS | wall |
|---:|---:|---:|---:|---:|---:|
| 8 | 74 388 | 172 601 | 0.05 s | 0.26 GB | 2.6 s |
| 10 | 272 532 | 665 657 | 0.18 s | 0.26 GB | 2.6 s |
| 12 | 1 065 108 | 2 637 881 | 0.68 s | 0.66 GB | 3.4 s |
| 14 | 4 235 412 | 10 526 777 | 2.65 s | 2.52 GB | 7.2 s |
| 16 | 16 916 628 | 42 082 361 | 10.75 s | 9.84 GB | 22.4 s |

Exact fit (residual 0 at all five points): V = 258·2^B + 8 340, C = 642·2^B + 8 249.
258 = 2 × 129 and 642 = 2 × 321, the per-read cost of one sliced DFCC table read derived in audit R3 §2.1
(first read of a table version with a non-constant `POINTER_OBJECT` index: 129·N + 64 variables, 321·N + 1 clauses, N = 2^B).
So refcell.rs pays exactly two such reads. Our uninit-checks P1 measurement (h1-step1, run 43393496999) paid six (774 = 6·129, 1926 = 6·321).
