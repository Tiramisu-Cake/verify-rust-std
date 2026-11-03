# RESULT DIRECTBOUNDS — TIMEOUT N10/N13 (controls PASS as intended)
Task TASK-DIRECTBOUNDS.md; coordinator GO 14dececaa42c9500a8d0ebd88d84859e6eae2e5f; one Build, G1 4 rows, no retry.
Build `ee675c46-f9fc-4376-9641-7e6590d2889f`; request `directbounds-n10-n13-direct-u8-20261103`, SHA256 02a91ccb…9185009 matches.
Library commit 3b856adf15267507dd5648ca8b7e3000d5c5d776 (tree library 17dedd1eb7…); pin Kani 9461e07af7 / nightly-2026-10-12.
check-tooling vs e8e238db9d87323fa4da011a1a8b37fb76ec91c0: all ok (g1.tooling.txt). measurement, controls:true, jobs1,
uninit off, 600 s/row, unwind25 + unwinding assertions, default solver, k1-standard4 4CPU/16GiB, swap off.
T=u8, F=U8Cmp fn-pointer, value StrictU8::CMP, full any [u8;N] + independent any u8 probe; no stubs/summaries/adapters.
Positives are A9 positive9(false) byte-copies with only N/run/literal-prefix substituted (static-check.json a9_byte_diff).

| N | Row | Status | VT s | Failed/total; unreach | Covers | CBMC RSS KiB | Actual route (Unstable->Freeze/Copy->small_sort_network, no merge) |
|---|---|---|---:|---|---|---:|---|
| 9 | A9 netcomp_direct_u8_n9 (NETCOMP2 44af7732, reference) | SUCCESS | 242.8685 | 0/383; 22 | 4/4 | 275236 | sort9_optimal (25 swaps), 0 inserts |
| 10 | direct_u8_n10 | TIMEOUT | UNKNOWN | UNKNOWN | UNKNOWN/4 | 294628 | sort9_optimal on v[0..9] (25) + one insert_tail(v[9]) |
| 13 | direct_u8_n13 | TIMEOUT | UNKNOWN | UNKNOWN | UNKNOWN/4 | 473764 | sort13_optimal (45 swaps), 0 inserts |
| 10 | count_negative_u8_n10 | FAILED expected | 10.206177 | 1/348; 18 | 2/2 | 215988 | same as N10 |
| 13 | count_negative_u8_n13 | FAILED expected | 19.990736 | 1/348; 18 | 2/2 | 366332 | same as N13 |

Only failed checks: literals `directbounds negative: count n10` / `… n13` (reported assertion spans directbounds.rs:90/113,
literal lines 92/115). Controls pass sortedness+count before corruption, reach both covers, fail count(0) N->N-1 only.
Positives: "CBMC timed out" at the 600 s cap; VT/checks/covers not printed. CBMC RSS = sampled per-PID peak (g1.peaks.txt).
Compiler VmHWM time -v 1762864 KiB; sampled process-sum 1.71 GiB; command wall 21:42.78; dmesg OOM none_seen.
Cloud FAILURE, run COMPLETE; gate/expectation_met/measurement_ok false; Kani exit1 (TIMEOUT rows + expected controls).
No new warnings attributed to netcomp/directbounds.rs (bounded log-grep g1.checks-grep.txt / g1.warnings-grep.txt).
Static: ordinary exact 200, pfc_order 18/bad0 unchanged (NETCOMP2 tree predates v6 202/36); cfg-on 395->399; rustfmt PASS.
Cost: own 1/1 Build, spent $0.3915, reserved $0, cap $1.00; no compile-error repair needed. Project at 13:21Z:
198 builds, used $86.8560, unfinished $0.8100 (other stages), cap $93.96.
Limitations line: direct actual-route u8 sort permutation (sortedness + full-value count) with U8Cmp=StrictU8::CMP, default
solver, 600 s/row on this pin is proved at N9 only; N10 and N13 TIMEOUT (no claim for N11/N12, N>=18, other T/F).
Evidence: directbounds/g1.{summary.md,rows.txt,checks-lines.txt,checks-grep.txt,peaks.txt,tooling.txt,status.json,cost.txt}.
DIRECTBOUNDS ЗАВЕРШЁН
