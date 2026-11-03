# RESULT COVERCOST — diagnostic SUCCESS; driver still 11.92 GiB, same growth -> covers not the cause
Runtime Claude Code, no subagents. Diagnostic, no proof credit; original reachability obligations not replaced.
Build 623c19b0-7637-4fb8-a191-1622c8e893a3, request covercost-g1-positive-nocover-u64-n10-20261103 (d47b9fa2…),
source de75524bb7 (GO after review), library 8b986b9775 / tree 67f41939ab (= U64-TEN-CALLER tree + appended clone).
Kani 9461e07a / nightly-2026-10-12; check-tooling vs 30f77e8599 exit0 (6 bound hashes). diagnostic, controls:true,
jobs1, uninit off, 10 min/row, gcb-e2-standard-4 -> k1-standard4 (15.63 GiB, swap off). Row log binding: Stub
swap_if_less->swap_adapter_u64ten, insert_tail->insert_adapter_u64ten; Verified stub swap_u64_net9, insert_tail_profile.
Clone = byte copy of u64tencall_positive_u64_n10 minus its 9 covers + one #[allow(unused_*)]; 0 reachable covers.

| Run | Row (...::tenleaves::caller::) | Status | VT s | checks; unr. | covers | driver peak | CBMC peak | sum | wall |
|---|---|---|---:|---|---|---:|---:|---:|---|
| COVERCOST G1 | u64tencall_positive_nocover_u64_n10 | SUCCESS | 347.03745 | 0/1104; 62 | none | 11.92 GiB @413s | 2.29 GiB | 11.82 GiB @413s | 6:55.65 |
| U64-TEN-CALLER G1 | u64tencall_positive_u64_n10 | UNKNOWN (OOM) | - | not printed | 9 planned | 15.29 GB @503s (OOM) | 2.71 GB | 15.30 GB | 9:01.43 |

Peaks KiB: kani-driver time -v max 12499880 = sampled VmHWM 12499880; CBMC 2406292 @316s (pid 9209, direct attribution);
process-sum 12395608 @413s; kani-compiler 1854600. dmesg OOM none_seen. Kani exit0, gate true, Complete 1/1, 0 failed.
Cloud 10:45:43Z -> 10:59:24Z (start 10:46:31Z). Own 1/1 Build, spent $0.1755, reserved $0 (cap $0.60).
Driver RSS (KiB, 30 s samples), CBMC alive 68-387 s here vs 72-469 s before:
  here:   ~7e3 to 210s; 240 163368; 270 794152; 300 1494584; 331 2252348; 361 2969148; 391 5687520; peak 12499880 @413
  before: ~7e3 to 270s; 300 425488; 330 1216032; 361 1984036; 391 2741796; 421 3530280; 451 4292136; 481 8653424; OOM @503
Growth while CBMC runs: here +0.60/+0.67/+0.72/+0.68 GiB per 30 s; before +0.75/+0.73/+0.72/+0.75/+0.73 — same rate.
Both runs: steep jump around CBMC exit (here 361s 2.83 -> 413s 11.92 GiB, CBMC last 387s; before 451s 4.09 -> OOM, last 469s).
Verdict (task rule "driver grows the same -> covers not the cause"): hypothesis "driver memory comes from cover/trace
  output" is refuted. Without covers the driver is not << 15 GB (11.92 GiB, 76% of RAM) and grows at the same rate.
  Observed only: removing covers shortened the CBMC phase (~319 s vs ~397 s alive) and the peak stayed below RAM;
  whether that is the causal reason is not established. Growth onset/rate track the CBMC phase, mechanism unknown.
Not established: the original positive with covers (still OPEN/UNKNOWN on 16 GB); any reachability claim for the
  composed route; the theorem with its original obligations. SUCCESS here is "diagnostic, no proof credit".
  The 16 GB margin is thin (3.7 GiB); driver memory of u64 N10 composition remains the barrier; next step is the
  coordinator's decision. Ledger after: builds189, used $84.0885 (other owners' builds unfinished $0.9450).
Evidence: covercost/g1.summary.md, g1.{status,tooling,cost,peaks,checks-grep}.txt, PREBUILD.md, static-check.json. STOP.
