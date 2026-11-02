# RESULT NETTHIRTEEN — TIMEOUT (600 s resource fit)
Task TASK-NETTHIRTEEN.md including «Уточнения»; coordinator GO42843d7d0d; G1 only, 2 rows.
Reviewed/build head `42843d7d0d4b8ff592059facd659667bef5bdc26`.
Library commit `d60b2c975d18ef8f69234f0269c5cf89faa2fa24`; tree `a618a0bdce2816d5d50ce73b351fcdcba1a59d1e`.
Build `beefc7a4-f532-4bc2-ac48-42b393cb42eb`; request `netthirteen-g1-full-value-count-20261102`.
Request SHA256 `af58fb068502f9342ad5c8badfca7a030e7e88b4c11d3c5ed443d9c73f2b1a07` matches.
Pin Kani9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12; tooling identity PASS.
measurement, controls:true, jobs1, uninit off, unwind25 with unwinding assertions; k1-standard4, 4CPU/16GiB, swap off.
Actual F is the function-item type of strict_less::<u8>, inferred without fn-pointer coercion.
Real Unstable u8/Freeze/Copy -> small_sort_network -> sort13_optimal -> insertion_sort_shift_left:
prefix13 already complete, zero insertions, no merge. Positive has full any [u8;13] and independent any u8 probe.
Both rows have no stubs/input assumptions; old N9 and ordinary code/domains unchanged.

| network:: harness | Status | VT seconds | CBMC RSS KiB | Failed/total | Covers |
|---|---|---:|---:|---:|---:|
| netthirteen_full_value_count_u8_n13 | TIMEOUT | UNKNOWN | 462300 | UNKNOWN | UNKNOWN/4 |
| netthirteen_full_value_count_u8_n13_negative | FAILED (expected) | 16.02919 | 345172 | 1/326 | 2/2 |

Positive cap600s; VT not printed, row wall UNKNOWN; CBMC sampled active84..683s, direct model/metadata RSS attribution.
Negative input=[0;13], probe0; after real sort v[12]=1: sortedness checked after corruption, count(0)13 ->12.
Both negative covers reached: sort returned before corruption; corrupted count-check reached after sortedness.
Only FAILED: literal kani::assert "netthirteen negative: full-value count preserved", network.rs:1055, exact expect_check.
No unrelated sortedness/unwind/unsupported failure; negative18 unreachable; terse backend check class not separately printed.
Whole verification including compilation wall684.02s, max RSS1665876KiB; sampled RSS sum1880228KiB; no OOM seen.
Cloud Build FAILURE, wall1066.110461s; run COMPLETE; expectation_met=false, measurement_ok=false, gate=false; Kani exit1.
Own builds1/1, spent $0.2430, reserved $0; initial reserve $0.675; global cap $88.96 unchanged; no retry/input narrowing.
Static ordinary exact200 unchanged, cfg-on386=384+2; PFC16/bad0; rustfmt/whitespace PASS; counts are not proofs.
N13 direct full-value proof did not fit600s on this pin; remains opt-in/uninit-off and unproved here; no N18/u64 claim.
Evidence: netthirteen/g1.{summary.md,rows.txt,peaks.txt,checks-lines.txt,tooling.txt,cost.txt}, final-check.json.
NETTHIRTEEN ЗАВЕРШЁН
