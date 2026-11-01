# RESULT NETNINE — PASS
Task TASK-NETNINE.md; branch experiment/kani-k1-netnine-20261102; G1 only, 2 rows.
Review/build head `915da659071b5b00fe51921394ce6a5e25c11c9b`; coordinator GO915da65907.
Library commit `24d9f1d3d8f1ff03f2c3dbe891d1e8f6f30a4d13`; tree `ac095c9d7bc9d6909f15015bea6ba692ee032f00`.
Build `15e9cc87-6e89-4b44-b839-e43161af6a31`; request `netnine-g1-full-value-count-20261102`.
Request SHA256 `8cfb89050296377ebb752357659fd6f4eeac31b82e2a663b65a68e6235ddcafd` matches.
Pin Kani9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12; tooling identity PASS.
measurement, controls:true, jobs1, uninit off, cap600s/row; k1-standard4, 4CPU/16GiB, swap off.
F is the function-item type of strict_less::<u8>, inferred without fn-pointer coercion.
Real UnstableSmallSortTypeImpl -> Freeze/Copy -> network -> sort9_optimal, empty insertion suffix.
Positive: full any [u8;9], pre=v, independent any u8 probe; sortedness and full-value count.
Neither row has stubs or input assumptions; both opt-in; ordinary code/domains unchanged.

| network:: harness | Status | VT seconds | CBMC RSS KiB | Failed/total | Covers |
|---|---|---:|---:|---:|---:|
| netnine_full_value_count_u8_n9 | SUCCESS | 261.0528 | 265272 | 0/345 | 4/4 |
| netnine_full_value_count_u8_n9_negative | FAILED (expected) | 7.939304 | 199624 | 1/326 | 2/2 |

Positive covers all reached: sort moves, probe hits input, probe misses input, duplicates present.
Negative witness input=[0;9], probe0, after real sort v[8]=1: sorted, count(0) changes9 ->8.
Both negative covers reached: sort returned before corruption; corrupted count check reached.
Only failure: literal kani::assert "netnine negative: full-value count preserved", network.rs:1005.
No sortedness/unwind/unsupported failure; terse output does not separately print backend check class.
Both rows report18 unreachable checks; required covers reached, target failure matches exact expect_check.
Cloud Build SUCCESS; run COMPLETE; expectation_met=true, measurement_ok=true, gate=true; Kani exit1 expected.
Whole verification command including compilation wall336.29s, max RSS1664128KiB; sampled process sum1978224KiB.
Row RSS attribution direct by model/metadata; build wall728.75s (setup included), not row VT.
Own builds1/1; spent $0.1755, reserved $0; initial reserve $0.675 <=$0.75; global cap $88.96 unchanged.
Static ordinary exact200 unchanged, cfg-on384=382+2; PFC16/bad0; rustfmt/whitespace PASS.
N9 answer: yes, this pinned full-route u8/default-< count check fits600s; direct count can replace the
structural-only permutation argument for this exact N9 instance. Ordinary200 retains its prior asserts.
N13/N18 remain unproved here: larger networks, insertion/merge may cost more; no timing extrapolation promised.
Evidence: netnine/g1.summary.md, g1.rows.txt, g1.peaks.txt, g1.checks-lines.txt, g1.tooling.txt, g1.cost.txt.
NETNINE ЗАВЕРШЁН
