# RESULT WONEDIAG — SUCCESS (3/3 fixed-N3 PFCs)
Branch experiment/kani-k1-wonediag-20261102; 2026-11-02; base W1 1c107cb12a.
REVIEW REQUEST 31edc5a6fb81465514f28a24948c38f12299ad6c; coordinator GO for this exact packet.
Library commit af8b0db75a78f737772c8fe86ed7d5cdff109e11; tree af3da15225005c0eba22ef42626c8562485c8e7e.
G1 b9e00fd2-b4a6-42fa-986b-f74db31a2f12 / wonediag-g1-20261102: Cloud SUCCESS, summary COMPLETE, gate/expectations true.
Kani9461e07af7; measurement/controls:true/jobs1/uninit off/timeout10/standard4/unwind16 unchanged.
Head/request/pin/pool identities match; check-tooling vs 30f77e859903df14b442ff9294d4fbbd44827f20 PASS.
Existing private T/F/CMP, targets and requires/ensures/modifies unchanged; old harnesses byte-identical.
Three PFCs inside opt-in wrap::wone: explicit initialized backing5, offset1, literal3; no length dispatch.
A/B/C/probe/sentinels unrestricted; canonical byte_less/noncopy_less; real trait bodies without summaries.
Stable u8 retains separate uninitialized scratch48, entire borrowed slice and whole-slice modifies.
Sorted keys x>>1, scalar-old full-byte count and original post-return input_frame retained.
Static ordinary exact200/cfg-on391, target ordering23/bad0, rustfmt and whitespace PASS; counts are not proofs.

| wrap::wone row | N3 status | VT s | cbmc RSS KiB | Failed/total | Covers | W1 N0..3 status / RSS KiB |
|---|---|---|---|---|---|---|
| unstable_byte_n3 | SUCCESS | 59.776577 | 416160 | 0/498 | 7/7 | TIMEOUT / 2101724 |
| freeze_noncopy_n3 | SUCCESS | 272.5441 | 1161416 | 0/478 | 7/7 | TIMEOUT / 15585836 |
| stable_byte_n3 | SUCCESS | 286.1486 | 1156924 | 0/475 | 7/7 | OUT_OF_MEMORY / 15679436 |

Seven N3 covers each: return/reversed/increasing/tied-distinct/duplicate/independent-probe hit/miss.
No failed checks; reported unreachable checks 18/8/8 respectively; all seven required covers satisfied.
VT is explicitly printed by Kani; W1 VT remains UNKNOWN for these rows. No W1/N3 time ratio inferred.
RSS is sampled process kernel VmHWM with direct metadata attribution; whole run wall11:40.42 incl compilation.
Whole-run time-v max1730584KiB; dmesg OOM scan none_seen. Own builds1/1, spent$0.2430/reserved$0 vs reserve$0.810.
Fixed N3 succeeds with far less RSS than W1; this supports joint effects of length union/match/backings
and associated expressions, but does not isolate their individual cost or establish a unique cause.
Established only N3 sorted/count/frame in these fixtures, not N0..3/N16, all backings or scratch sizes.
Old negative controls were not rerun; their prior success does not substitute for these new PFCs.
Deferred assessment: prefix3 modifies changes write-set even with allocation48/frame retained; N2/N4+ changes geometry/cost, still UNKNOWN.
Next single pair: Stable u8 fixed-N3 PFC versus plain real-entry N3, same inputs/backing/scratch48 and explicit sorted/count/sentinel/covers.
That pair measures contract-instrumentation cost, including per-write frame checking versus plain post-return assertions; no run here.
A two-row timeout10 standard4 Build reserves (2*10+30)*$0.0135=$0.675; separate PRE-BUILD GO required, no success guarantee.
Evidence: wonediag/g1.summary.md, g1.rows.txt, g1.peaks.txt, g1.checks.txt, g1.tooling-check.txt, final-check.json; W1 RESULT-WONE.md.
WONEDIAG ЗАВЕРШЁН — SUCCESS; this one stage stops. No G2 or automatic length/write-set expansion.
