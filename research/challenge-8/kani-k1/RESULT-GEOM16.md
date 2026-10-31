# GEOM16 — G1 REVIEW / PARTIAL GATE MISMATCH

Coordinator Claude Code. Mandatory actual PFC pair COMPLETE/SUCCESS; strict G1 gate false.
Branch experiment/kani-k1-geomsixteen-20261031. G2 NOT_RUN, no separate GO.
First recorded clock2026-10-31T14:52:55Z; conservative window14:50Z..19:50Z, closing19:20Z.
Cap88.96 unchanged; tooling baseline6945f187208040e2d911e0797ef525668bdd46f8.
Approved G1 request/source commit7684a98d474157f09d8702695262d5314460ccf0.
Library source commit0560a33adbbd8b058c05370108357dcf09c265b8.
Frozen library5084baaaa44d11967abca2f367626385dc7ec219; no post-GO library changes.
Kani9461e07af7ec929f050aa4192f29363c9be07779; nightly-2026-10-12.

G1 UUID eb7eef9a-349f-4e2d-bb5c-8224b8d5b5ba; request geom16-g1-20261031-r1.
Request SHA256 ea859a4d7cda0fca92edd16495c7034e56672098fd4f8265c9f901dd93015134.
Cloud FAILURE; source/tool compilation succeeded; summary COMPLETE, Kani exit1.
Build start14:59:39.050880025Z / finish15:20:21.709463Z on 2026-10-31.
Own UUID ledger: builds1/2, spentUSD0.2835, active reservedUSD0, limitUSD2.
G1 envelope80min/USD1.080; G2 proposed60min/USD0.810, spent+proposed=USD1.0935.
G2 request geom16-g2-20261031-r1 remains prepared; any dispatch needs fresh budget/window/GO.
Watch delivered terminal notification; no active own build. No retry dispatched.

All rows: Linux k1-standard4 / gcb-e2-standard-4, jobs1, controls on, uninit checks off,
unwind34,10min per entry, swap off. Full namespace for suffixes below:
slice::sort::shared::smallsort::verify::merge::geom16::

| Row suffix | Status | VT s | CBMC RSS KiB | Failed/total; unreachable | Cover |
| --- | --- | --- | --- | --- | --- |
| final16_stable_scratch48_actual_pfc | SUCCESS | 526.8486 | 2438976 | 0/440;81 | 1/1 |
| same16to0_stable_scratch48_actual_pfc | SUCCESS | 155.65565 | 1257328 | 0/440;91 | 1/1 |
| same16to0_checker_positive | SUCCESS | 16.15625 | 284212 | 0/295;87 | 1/1 |
| same16to0_value_corruption_control | FAILED | 16.95444 | 284148 | 1/301;86 | 1/1 |
| same16to0_source_frame_control | FAILED | 17.498323 | 289320 | 1/301;86 | 1/1 |
| same24to8_stable_scratch48_actual_pfc | NOT_RUN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| same24to8_value_corruption_control | NOT_RUN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| same24to8_left_frame_control | NOT_RUN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

RSS has direct metadata attribution for all five CBMC processes, one match per row.
Sampling2s/409 samples; sampled sum peak3429076KiB; whole-run max RSS2438976KiB,
wall13:36.45 including compilation. RSS is process memory, not physical RAM or per-row driver sum.
Short-lived processes may be missed; OOM scan none_seen, not an exhaustive OOM theorem.

Control failures: frozen file library/core/src/slice/sort/shared/smallsort/verify/merge/geom16.rs,
function check_same8: value control assert24/literal27 GEOM16_FULL_VALUE_COUNT;
source-frame control assert29/literal29 GEOM16_SOURCE_FRAME. Exactly one failure each,
all required covers reachable; no additional reported failures. Sorted assert23 not failed.
Runtime descriptions are Kani placeholder messages, not the expected literals.
The exact file/line/function binds each failure to its intended frozen-source assertion;
assertion class is source-inferred; runtime machine class is UNKNOWN (terse output omits it).
Strict literal expectations UNMET; original request/gate/matchers are preserved unchanged.
Automatic gate/expectation_met/measurement_ok=false. Controls require coordinator disposition;
no silent manual gate override. Positive rows retain their individual SUCCESS evidence.

Each fixture has exactly one [MaybeUninit<u8>;48] nonconst-repeat scratch backing:
[MaybeUninit::<u8>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN].
Final16 initializes scratch0..16; destination is separate initialized arbitrary exact v16.
Same16to0 initializes only source16..24; disjoint same-object dst0..8 starts uninitialized.
Prepared same24to8 initializes source24..32 plus independent arbitrary live left0..8;
dst8..16 starts uninitialized. No typed all48 view, second scratch or duplicate snapshot.
Each entry sets one parent independent arbitrary probe, unchanged across call/checker.
Parent lt_u8 function item orders by x>>1; count is parent full-u8 probe_count_unrolled.

Actual PFC verifies the unchanged callee with original requires/modifies/both ensures:
sortedness and source-post/dst count. Mandatory rows avoid duplicate expensive postconditions.
Plain real body assumes only sorted halves; checker tests sortedness, pre-input/dst count,
and initialized source frame. Source borrow ends before mutation and fresh bounded views.
Value flip changes payload; source flip slot16 changes frame only. Controls calibrate local
predicates, not callee failure or Kani modifies instrumentation. Optional left-frame is unmeasured.

Tooling/pool/source/request/pin and six bound-file hashes MATCH; check-tooling PASS.
Source audit: old parent/dependencies and cfg-off projection byte-identical except EOF registration;
other library/production/helpers/modules unchanged. Independent top specdiag insertion unaffected.
Python validator5/3, rustfmt and diff checks passed; no local compiler/proof execution.
F03 remains open for generic F/T; only this bounded concrete pure-lt_u8 profile has evidence.
No caller-N16 theorem, sort8 contract, general aggregate, ordinary/P1/P2 admission, Mac/jobs3 or B2.
After SPEC-FIX, changed source/assumptions require fresh review and possibly repeated evidence.

Bounded evidence/review: geom16/g1.review.json, g1.summary.md, g1.rows.txt,
g1.checks-lines.txt, g1.controls-grep.txt, g1.peaks.txt, g1.tooling-check.txt,
g1.frozen-assertions.txt, g1.status.json, budget-g1-final.txt; manifest and requests unchanged.
G1 acceptance and G2 authorization remain with coordinator; task not marked finally closed.
