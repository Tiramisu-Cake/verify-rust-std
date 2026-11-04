# RESULT WIDTHU32 — u32 N8 permutation: kissat SUCCESS 210.8 s, default TIMEOUT, value-loss control FAILED as designed

PRE-BUILD e39f946565 (GO). Branch experiment/kani-k1-widthuthirtytwo-20261103, k1-network, base e0fda080f5. Library 78c4138175
→ tree 74039680 (opt-in `mod widthu32;` + widthu32.rs = PERMSOLVER `perm_arbitrary_kissat_u64_n8`, u64→u32, +2 covers). Build
0334e611-b11c-4036-9f4b-4e58417f7bbd @e39f946565, request widthuthirtytwo-g1-perm-u32n8-20261103 (ab2a1ab9…ca85), Kani
9461e07af7ec / nightly-2026-10-12; check-tooling vs e0fda080f5 ok. gcb-e2-standard-4 → k1-standard4, 4 CPU / 15.6 GiB, swap
off, controls on, jobs 1, uninit off, 10 min/row, unwind 25. T0 07:40:13Z, finish 08:04:13Z.

| Root (network::widthu32::, u32 N8) | Solver | Status | VT s | failed/total | covers | CBMC RSS |
|---|---|---|---:|---|---|---:|
| widthu32_perm_n8_default | default | TIMEOUT (600 s; "CBMC timed out") | — | — | UNKNOWN | 0.15 GiB |
| widthu32_perm_n8_kissat | kissat | **SUCCESS** | 210.77 | 0/334, 18 unreach. | 5/5 | 0.09 GiB |
| widthu32_perm_n8_value_loss_control | kissat | FAILED at designated literal (widthu32.rs:67) | 5.38 | 1/338 | 5/5 | 0.09 GiB |

## Gate and comparison
Gate met: row 2 SUCCESS, 0 unintended, 5/5 covers (probe occurs/absent both reached); row 3 failed only at `widthu32 negative:
full-value count after value loss`. Row 1 = measurement (summary gate False only because it was requested as SUCCESS).
N8, route `small_sort_network`, `strict_less`: **u8** default SUCCESS 143.6 s (`network_correctness_u8_n8`, PART2-FAST 5765f47e;
family body, sortedness + count); **u32** default TIMEOUT, kissat 210.8 s (this run); **u64** default TIMEOUT (POSTS8 97be7f87),
kissat 449.5 s (PERMSOLVER a931cf37, same body). Conclusion: at N8 the default solver already times out at u32 (u8 passes);
with kissat u32 takes 47 % of the u64 time. Single runs; no claim for other N/types/solvers, no proof carried between types.
Peaks: time -v max 1706360 KiB (kani-compiler 1.63 GiB), wall 14:46.61, OOM none_seen. No compile error/repair/retry; no
smallsort warnings (`log-grep '[-]> .*smallsort'`: no match). Cost: own $0.3105 of cap $0.90; project used $92.2830,
reserved $0.81 by another unfinished build, cap $98.96. Receipts: widthu32/{PREBUILD.md, body.diff, summary.md, tooling.txt}.
WIDTHU32 ЗАВЕРШЁН
