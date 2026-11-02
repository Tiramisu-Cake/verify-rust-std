# PART2-SPLIT31 G2 PRE-BUILD REVIEW (matching baseline)

Status: WAITING FOR COORDINATOR GO (G2). G1 is terminal and accounted; candidate evidence below is separate from the baseline.
Owner k1-network; branch `experiment/kani-k1-partsplit-20261102`; packet base = G1 GO packet `52c9be6c` (PREBUILD.md).
Library tree unchanged `05eb97eaef01dc4015e659d46256b2d910750d58` (library commit `b2a13747`); no library change since G1.
Tooling lane = `30f77e859903df14b442ff9294d4fbbd44827f20`, Kani `9461e07a…`, nightly-2026-10-12 (unchanged files).

## G1 result (terminal, `g1.summary.md`, `g1.tooling-check.txt`)

Build `ce83c352-888f-4163-b82c-5e34c8deb196`, source `52c9be6c`, request sha256 `57bf1824…0b22`, Cloud Build SUCCESS,
gate True, Kani exit 0, controls on, jobs1, k1-standard4, check-tooling vs 30f77e85 all ok. Actual cost $0.1755.

| Root | Status | VT s | checks failed/total | covers | CBMC peak |
|---|---|---:|---|---|---:|
| network::dispatch_safety_stable_bytes17_n31 | SUCCESS | 113.3 | 0/368 | 2/2 | 1.64 GiB |
| network::dispatch_safety_unstable_bytes17_n31 | SUCCESS | 167.4 | 0/368 | 2/2 | 2.38 GiB |

Process peaks: kani-compiler 1.57 GiB, kani-driver 0.71 GiB, largest sampled RSS sum 2.90 GiB; whole run max RSS 2.38 GiB
(2499676 KiB), wall 5:55; OOM none. Candidate proof gate met on G1 (both SUCCESS, 0 failures, covers 2/2 each).

## G2 request (only change in this packet besides evidence files)

`RUN-REQUEST.json` = `partsplit/g2.request.json`, sha256 `2b516f70c703c7e6d3ee02ac3b47f7cb61e1ac6ceb968d9f3aa9ced0b7e74ec6`
(unchanged since G1 packet; validated). request_id `partsplit-g2-measure-bytes17-n31-pair-20261102`, measurement,
gcb-e2-standard-4, controls true, kani_jobs 1, uninit_checks false, 10 min; single row
`network::dispatch_safety_stable_unstable_bytes17_n31` (unchanged pair root), expect SUCCESS, required covers 3/3.
Envelope 40 min / reserve $0.540.

## Budget / slots / window (`budget-before-g2.txt`)

Project used $81.0915, reserved $0 (0 unfinished, PARTTWO-TREE no longer reserving); k1-network 0 unfinished.
Own spent $0.1755 + G2 $0.540 = $0.7155 ≤ $2.50. Headroom $7.8685.
Snapshot 18:43Z; G2 40 min envelope ends before the 21:15Z main deadline if dispatched by ~20:35Z. Re-check before dispatch.
