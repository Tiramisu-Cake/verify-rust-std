# GEOM16 — PREPARED / WAIT GO

Coordinator: Claude Code. Task: TASK-GEOM16.md. No build dispatched; proof verdict PENDING.
Branch experiment/kani-k1-geomsixteen-20261031.
First recorded clock 2026-10-31T14:52:55Z, preparation already underway.
Conservative window start14:50Z, closing19:20Z, deadline19:50Z on 2026-10-31.
Cap88.96; baseline6945f187208040e2d911e0797ef525668bdd46f8; no cap/history changes.
Source0560a33adbbd8b058c05370108357dcf09c265b8.
Library5084baaaa44d11967abca2f367626385dc7ec219.
Kani9461e07af7ec929f050aa4192f29363c9be07779; nightly-2026-10-12.

Own UUID ledger empty: builds0/2, spentUSD0, active reservedUSD0, limitUSD2.
G1 request geom16-g1-20261031-r1; G2 request geom16-g2-20261031-r1.
G1 proposed80min/USD1.080; G2 proposed60min/USD0.810; full140min/USD1.890.
Every dispatch needs fresh global budget, own UUID ledger, GO and closing30min reserve.
G1 gate PENDING; G2 NOT_RUN, conditional on accepted G1 and separate GO/time/budget.

All rows: Linux k1-standard4 / gcb-e2-standard-4, jobs1, controls on, uninit checks off,
unwind34,10min per entry. Exact names and required covers in geom16/geometry-manifest.json.
Common full namespace: slice::sort::shared::smallsort::verify::merge::geom16::

| Row suffix | State | VT/RSS | Assert / cover |
| --- | --- | --- | --- |
| final16_stable_scratch48_actual_pfc | NOT_RUN | UNKNOWN | actual ensures / post-call |
| same16to0_stable_scratch48_actual_pfc | NOT_RUN | UNKNOWN | actual ensures / post-call |
| same16to0_checker_positive | NOT_RUN | UNKNOWN | sorted,count,source / after checks |
| same16to0_value_corruption_control | NOT_RUN | UNKNOWN | count24,literal27 / pre-mutation |
| same16to0_source_frame_control | NOT_RUN | UNKNOWN | source29 / pre-mutation |
| same24to8_stable_scratch48_actual_pfc | NOT_RUN | UNKNOWN | actual ensures,left34 / post-check |
| same24to8_value_corruption_control | NOT_RUN | UNKNOWN | count24,literal27 / pre-mutation |
| same24to8_left_frame_control | NOT_RUN | UNKNOWN | left34 / pre-mutation |

Assert file library/core/src/slice/sort/shared/smallsort/verify/merge/geom16.rs;
sorted23, count24 (literal27), source29, left34; actual checks/locations not observed yet.
Exact literal matchers preserved; placeholder/attribution mismatch must remain UNKNOWN.

Each fixture creates exactly one [MaybeUninit<u8>;48] nonconst-repeat backing.
Initializer [MaybeUninit::<u8>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN].
Final16: scratch0..16 initialized from arbitrary input, separate initialized any v16 dst.
Same16to0: only source16..24 initialized; same-object disjoint dst0..8 initially uninitialized.
Same24to8: source24..32 and independent live left0..8 initialized; dst8..16 uninitialized.
No view over all48, no uninitialized read, no second scratch allocation or duplicate snapshot.
One parent arbitrary independent probe per call, unchanged; full-u8 probe_count_unrolled.
Parent pure lt_u8 function item orders by x>>1; no new comparator closure/default ordering.

Actual PFC retains original requires, destination modifies, sortedness and count ensures;
count ensures compare source-post/dst. Optional PFC separately checks live left preservation.
Plain real-body rows assume only sorted halves and check sortedness, pre-input/dst count,
source frame; optional rows also check left frame. Source shared borrow ends before mutation.
Value flip changes payload only; source flip slot16; optional left flip slot0.
Negative covers occur after actual merge before mutations, positive covers after properties.
These controls calibrate checker sensitivity, not callee correctness or modifies instrumentation.
Local frame checker covers initialized protected spans; no all48/uninit claim.

Static source audit PASS: old parent items/dependencies byte-identical, cfg-off EOF module
projection byte-identical; only new child and EOF registration added, top region unchanged.
Other library/production/helper/modules/lane/flags/pins unchanged. Specdiag insertion independent.
Python request validator accepted5/3 entries; rustfmt --check and git diff --check passed.
No local compiler/proof/CI execution. No terminal evidence or independently established proof yet.

F03 remains open for generic F/T; only concrete bounded u8/lt_u8 geometry can receive credit.
No caller theorem, sort8 contract, general aggregate, ordinary/P1/P2 admission, Mac/jobs3 or B2.
After SPEC-FIX, new assumptions/source may require fresh review and repeat.
Handoff: geom16/PRE-BUILD-REVIEW.md, geometry-manifest.json, source-audit.json,
g1/g2.request.json plus validated args/runner/rustflags; RUN-REQUEST.json installs G1.
