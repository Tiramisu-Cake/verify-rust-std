# GEOM16 — COMPLETE bounded probe / historical automatic gates false

Three actual PFC rows and plain positive SUCCESS; four intended controls source-bound; covers8/8.
Branch experiment/kani-k1-geomsixteen-20261031; coordinator Claude Code; no further builds.
First recorded T0 clock2026-10-31T14:52:55Z; preparation already underway.
Conservative window14:50Z..19:50Z on 2026-10-31, closing19:20Z; closed within window.
Cap88.96 unchanged; tooling baseline6945f187208040e2d911e0797ef525668bdd46f8.
Library source commit0560a33adbbd8b058c05370108357dcf09c265b8.
Frozen library5084baaaa44d11967abca2f367626385dc7ec219 identical for G1/G2.
Kani9461e07af7ec929f050aa4192f29363c9be07779; nightly-2026-10-12.

G1 UUID eb7eef9a-349f-4e2d-bb5c-8224b8d5b5ba; request geom16-g1-20261031-r1.
G1 request/source SHA7684a98d474157f09d8702695262d5314460ccf0.
G1 request SHA256 ea859a4d7cda0fca92edd16495c7034e56672098fd4f8265c9f901dd93015134.
G2 UUID fcfce897-dafb-49d2-a156-4edc01f323e9; request geom16-g2-20261031-r1.
G2 request/source SHAa5fe87afe995ade63ef14684ee6a3540b534a3a6.
G2 request SHA256 519a123c9930905b8320262ab1f35fe5e91eb18dc60148060af7fc778e1c5e95.
Cloud statuses FAILURE; summaries COMPLETE; source/tool compilation successful; Kani exit1 each.
G1 start14:59:39Z/finish15:20:21Z; G2 start15:28:01Z/finish15:39:52Z on 2026-10-31.
Own UUID ledger2/2 builds: G1 USD0.2835 + G2 USD0.1620 = USD0.4455 <= USD2.
Final active reservedUSD0; no active own build/watch, both terminal notifications delivered.
Full envelopes honored: G1 80min/USD1.080, G2 60min/USD0.810, closing30min reserved.

All rows: Linux k1-standard4/gcb-e2-standard-4, jobs1, controls on, uninit checks off,
unwind34,10min per entry, swap off. Full namespace for suffixes below:
slice::sort::shared::smallsort::verify::merge::geom16::

| Row suffix | Status | VT s | CBMC RSS KiB | Failed/total; unreachable | Cover |
| --- | --- | --- | --- | --- | --- |
| final16_stable_scratch48_actual_pfc | SUCCESS | 526.8486 | 2438976 | 0/440;81 | 1/1 |
| same16to0_stable_scratch48_actual_pfc | SUCCESS | 155.65565 | 1257328 | 0/440;91 | 1/1 |
| same16to0_checker_positive | SUCCESS | 16.15625 | 284212 | 0/295;87 | 1/1 |
| same16to0_value_corruption_control | FAILED | 16.95444 | 284148 | 1/301;86 | 1/1 |
| same16to0_source_frame_control | FAILED | 17.498323 | 289320 | 1/301;86 | 1/1 |
| same24to8_stable_scratch48_actual_pfc | SUCCESS | 162.8244 | 1265540 | 0/457;91 | 1/1 |
| same24to8_value_corruption_control | FAILED | 17.663279 | 252108 | 1/302;86 | 1/1 |
| same24to8_left_frame_control | FAILED | 16.685663 | 299596 | 1/302;86 | 1/1 |

Every CBMC RSS value has direct metadata attribution, one match per harness; no driver sum claimed.
Sampling2s, G1/G2 samples409/137, sampled total RSS peaks3429076/1920088KiB.
Whole-run max RSS2438976/1710708KiB, wall13:36.45/4:31.93 including compilation.
RSS is process memory, not physical RAM; short-lived processes may be missed; OOM scan none_seen.

Frozen assert file library/core/src/slice/sort/shared/smallsort/verify/merge/geom16.rs.
Both value controls: check_same8 assert24/literal27 GEOM16_FULL_VALUE_COUNT.
G1 source control: check_same8 assert29/literal29 GEOM16_SOURCE_FRAME.
G2 left control: check_left_half assert34/literal34 GEOM16_LEFT_HALF_FRAME.
Exactly one intended assertion failure per control, covers1/1; no additional reported failures.
Sorted23, source29 in G2, and count24 in frame controls were not reported failed.
Runtime descriptions are placeholders; literal expectations UNMET and runtime machine class UNKNOWN.
Assertion class and literal are source-inferred from exact frozen file:line/function.
Historical gate/expectation_met/measurement_ok=false for both; requests and gates not rewritten.
G1 gate accepted by coordinator as ACCEPTED_BY_LOCATION in g1.coordinator-disposition.json.
G2 rows COMPLETE: actual PFC plus initialized left preservation SUCCESS; both controls confirmed
by frozen location by Codex. No separate coordinator disposition for G2 is claimed.
Bounded measurement completed; automated acceptance remains false, with manual attribution separate.

Every fixture has one stable [MaybeUninit<u8>;48] nonconst-repeat backing, initializer exactly
[MaybeUninit::<u8>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN].
Final16 initializes only scratch0..16; dst is a separate initialized arbitrary exact v16.
Same16to0 initializes only source16..24; disjoint same-object dst0..8 starts uninitialized.
Same24to8 initializes source24..32 plus independent arbitrary live left0..8; dst8..16 uninitialized.
No typed all48 view, uninitialized read, second scratch allocation or duplicate snapshot.
Each entry sets one parent arbitrary independent probe, unchanged; full-u8 probe_count_unrolled.
Parent pure lt_u8 function item orders by x>>1; no comparator closure or rank/key assumptions.

Actual PFC retains original requires, dst modifies and both ensures: sortedness/source-post count.
Mandatory PFCs avoid duplicate expensive postconditions; optional PFC adds live-left frame assertion.
Plain real bodies assume only sorted halves and check sortedness, pre-input/dst count and source
frame; same24to8 also checks left frame. Source borrow ends before mutation and fresh views.
Value flips change only payload; source flip slot16; left flip slot0. These calibrate predicates,
not callee counterexamples or modifies instrumentation. Frame checks cover initialized protected
spans, not all48 or general uninit validity. No caller-N16 theorem or sort8 contract established.

Both tooling/pool/source/request/pin checks and six bound-file hashes MATCH cap baseline.
Final source audit PASS: old parent/items/dependencies and cfg-off projection byte-identical;
only child geom16.rs plus EOF cfg/module registration. Other library/production/helpers unchanged.
Top specdiag registration area unchanged; two registrations integrate independently.
Python validator5/3, rustfmt and diff checks passed; no local compiler/proof/CI execution.
F03 generic-F/T remains OPEN; evidence applies only to concrete bounded pure-lt_u8 geometries.
No ordinary/P1/P2 admission, general aggregate, Mac/jobs3 or B2; SPEC-FIX may require review/repeat.

Handoff: geom16/geometry-manifest.json and exact g1/g2.request.json with args/runner/rustflags;
final-review.json, final-source-audit.json, evidence-index.json and per-run g1/g2.review.json.
Per-run bounded summary/rows/checks-lines/controls-grep/peaks/tooling/status/frozen-assertions saved.
G1 coordinator disposition separate; final own ledger budget-final.txt. All work closed for review.
