# RESULT PERMSOLVER — u64 N8 permutation with kissat: arbitrary probe SUCCESS 449.5 s; quadratic TIMEOUT

Reviewed PRE-BUILD 33043cb6a4 (GO; review fix restored the POSTS8 length cover). Branch experiment/kani-k1-permsolver-20261103,
owner k1-merge, base a7271841 (PERMPROBE). Library 33898a9768 + 4be7709979 → tree bbbf5e48 (perm.rs append `mod solver;`, new
verify/network/posts/perm/solver.rs; old roots/helpers unchanged). Build a931cf37-8984-4162-bced-869643a82f6d @33043cb6a4,
request permsolver-g1-kissat-oracles-u64n8-20261103 (2c2307e3…9314). Kani 9461e07af7ec / nightly-2026-10-12; check-tooling vs
30f77e859903 ok. gcb-e2-standard-4 → k1-standard4, 4 CPU / 15.6 GiB, swap off, controls on, jobs 1, uninit off, 10 min/row,
unwind 25, T0 11:04:24Z → 11:31:26Z. Domain/bodies = POSTS8 count / PERMPROBE quadratic + `#[kani::solver(kissat)]`; no cuts.

| Oracle (u64 N8, same entry) | Default SAT | Kissat | covers | RSS kissat row (cbmc + kissat) |
|---|---|---|---|---|
| arbitrary u64 probe | TIMEOUT 600 (ref POSTS8 97be7f87) | **SUCCESS 449.48 s**, 0/334 (this run) | 3/3 | 0.09 + 0.04 GiB |
| index probe | TIMEOUT 600 (ref PERMPROBE 87487311) | SUCCESS 573.99 s, 0/342 (ref PERMPROBE) | 2/2 | 0.09 + 0.05 GiB |
| O(N²) quadratic | TIMEOUT 600 (ref PERMPROBE) | TIMEOUT 600, VT UNKNOWN (this run) | UNKNOWN | 0.12 + 0.05 GiB |
| control arbitrary `[P;8]` | — | FAILED `permsolver negative: arbitrary count` 2.05 s, 1/328 | 2/2 | UNKNOWN |
| control quadratic `[P;8]` | — | FAILED `permsolver negative: quadratic count` 3.04 s, 1/330 | 2/2 | UNKNOWN |

Metatheorem (PERMPROBE): the three oracles are equivalent permutation claims on this domain; kissat changes only the SAT backend.
Gates: arbitrary+kissat SUCCESS, 0 unintended, 3/3 covers → **permutation credit** (exact POSTS8 count body). quadratic+kissat
TIMEOUT → no credit. Controls: each failed only at its designated literal (solver.rs:80, :106), initial and after-overwrite
checks passed, 2/2 covers → gate met. Build peaks: max RSS 1754204 KiB (kani-compiler 1.67 GiB), process-sum 1.79 GiB,
wall 18:42.71, OOM none_seen. No compile error; no repair/retry used.
Solver vs oracle (single runs, not a ranking): kissat moves arbitrary/index under 600 s; re-formulating the probe does not
help with kissat (index 574 s, quadratic TIMEOUT vs arbitrary 449 s). No speed-up from TIMEOUT caps is derived.
Cost: $0.3510 own spent of cap $1.00, own reserved $0; project used $84.9255, reserved $0, cap $88.96.

Conclusion: **C1 заморожен** by the stated rule — no oracle with kissat reaches ≤ ~300 s on GCB; the best one, the arbitrary
probe with kissat at 449.5 s, is 22 % under the index row but 1.5× the screen, so there is no N9..12 candidate. Usable as opt-in
evidence only: POSTS8 partposts_sorted_u64_n8 + perm_arbitrary_kissat_u64_n8 give sortedness + permutation for u64 N8.
Receipts: permsolver/PREBUILD.md, permsolver/body-diff.txt, permsolver/g1.request.json, permsolver/g1.result.md.
