# GEOM16 PRE-BUILD REVIEW

State: prepared and published for Claude Code review; **WAIT GO**, no dispatch.
Published package SHA is supplied by the handoff message (this file cannot bind its own commit).
Branch: `experiment/kani-k1-geomsixteen-20261031`.
Source commit: `0560a33adbbd8b058c05370108357dcf09c265b8`.
Library tree: `5084baaaa44d11967abca2f367626385dc7ec219`.
Base library tree: `b10a21505be73f26be50cd0e1c0f0c5f48773f9a`.
Cap/tooling baseline: `6945f187208040e2d911e0797ef525668bdd46f8`, cap USD88.96 unchanged.
Kani: `9461e07af7ec929f050aa4192f29363c9be07779`; nightly-2026-10-12 unchanged.

First recorded session clock: 2026-10-31 14:52:55 UTC, preparation already in progress.
Use conservative window start 14:50 UTC, closing 19:20 UTC, deadline 19:50 UTC.
Own ledger: no UUIDs/builds; spent USD0, active reserved USD0; maximum two builds / USD2.
Global bounded ledger snapshot: `budget-pre-review.txt`; refresh before every dispatch.
G1 proposed envelope: 5*10+30=80min / USD1.080.
G2 proposed envelope: 3*10+30=60min / USD0.810.
Combined: 140min / USD1.890, plus 30min closing reserve; no timeout reductions.
G2 requires accepted G1, its own GO, full remaining time and own spent+reserved+0.810<=2.
Failed/cancelled/retry builds consume slots. Any source delta requires review/GO and new identity.

## Exact entries

Full namespace for every row below:
`slice::sort::shared::smallsort::verify::merge::geom16::`

| Gate | Exact final component | Mode | Expected |
| --- | --- | --- | --- |
| G1 | final16_stable_scratch48_actual_pfc | actual PFC | SUCCESS |
| G1 | same16to0_stable_scratch48_actual_pfc | actual PFC | SUCCESS |
| G1 | same16to0_checker_positive | plain actual body | SUCCESS |
| G1 | same16to0_value_corruption_control | plain actual body | FAILED count |
| G1 | same16to0_source_frame_control | plain actual body | FAILED source frame |
| G2 | same24to8_stable_scratch48_actual_pfc | actual PFC | SUCCESS |
| G2 | same24to8_value_corruption_control | plain actual body | FAILED count |
| G2 | same24to8_left_frame_control | plain actual body | FAILED left frame |

Both requests use measurement, controls:true, jobs1, uninit_checks:false, unwind34,
10min per entry, Linux `gcb-e2-standard-4` / `k1-standard4` (4CPU/16GiB).
`RUN-REQUEST.json` equals `g1.request.json`; G2 is prepared but not installed or authorized.
Request IDs: `geom16-g1-20261031-r1`, `geom16-g2-20261031-r1`.
Stock Python validator accepted five and three entries; exact args/runner/rustflags are saved.

## Concrete memory and properties

Every fixture has one stable `[MaybeUninit<u8>;48]` backing, initialized using exactly
`[MaybeUninit::<u8>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN]` (nonconst repeat).
Final16 initializes only scratch[0..16] from arbitrary input and merges to a separate,
initialized arbitrary `[u8;16]`. Same16to0 initializes only scratch[16..24], dst[0..8].
Same24to8 initializes source[24..32] and independent arbitrary protected left[0..8];
dst[8..16] remains uninitialized until merge. All offsets share one scratch base in same cases.
Other scratch slots are never read; only bounded initialized source/left views are formed.
Input and optional left arrays are retained directly as snapshots, with no duplicate snapshot.
`geometry-manifest.json` records full identities, spans, eight names and source coordinates.

Comparator in every actual call is the parent's pure function item `lt_u8` (`x>>1` order).
Each entry sets the parent arbitrary independent value probe once; no subsequent mutation.
The parent `probe_count_unrolled` counts full u8 values, rather than keys.
Actual PFC targets the unchanged real bidirectional_merge; no stubs, wrapper target or clone.
All original requires, dst modifies, sortedness and source-post/dst count ensures remain intact.
The two required PFC rows do not duplicate expensive postconditions in another checker.
Optional PFC separately checks protected left preservation after the real call.

Plain fixtures assume only original sorted-halves requires and execute the full real body
under the lane's existing --no-assert-contracts. They explicitly check parent sortedness,
pre-input/dst full-value count and source equality; optional rows also check left equality.
Post-call mutation closures are fixture callbacks only; the comparator is still `lt_u8`.
Source shared views end before callbacks; checker forms fresh bounded views afterwards.
Each monomorphization reaches only its own cover: positive after checks, negative before mutation.
Dst payload flips preserve keys; only full-value count should fail for some arbitrary probe.
Source slot16 flip preserves sorted/count, violating source frame. Optional left slot0 flip
preserves source/sorted/count, violating only protected left frame.

Frozen child assert coordinates: sorted 23, count assert 24 (literal27), source frame29,
left frame34. Literals are GEOM16_SORTED, GEOM16_FULL_VALUE_COUNT, GEOM16_SOURCE_FRAME,
GEOM16_LEFT_HALF_FRAME. Exact literals are request matchers; placeholder mismatch is UNKNOWN.
Before accepting any control, verify exactly one intended failed check, file/line/class and
every other check, plus reachable required cover. Never rewrite historical matcher/gate results.

G1 gate requires both PFCs and plain positive SUCCESS, reachable required covers, both intended
controls, no extra failures or identity mismatch. TIMEOUT/compile/unsupported/missing is STOP;
retain valid individual positive rows. Optional G2 cannot run after a failed gate.

## Audit, evidence and limits

`source-audit.json`: old parent content/dependencies byte-identical; only new child plus EOF
two-line cfg/module registration. All other library files and lane/pin/flags/cap unchanged.
Cfg-off parent projection is byte-identical; no new ordinary harness. Top registration area
is unchanged, so the independent specdiag insertion and EOF geom16 insertion do not overlap.
No specdiag content was read or transferred. Rustfmt --check and git diff --check passed.
No local cargo/rustc/Kani/CBMC, Actions/CircleCI or proof run has been performed.

After GO, library is frozen across G1/G2. Before dispatch refresh global budget and UUID ledger,
check full envelope/closing reserve and published request/source identity. After dispatch run
k1g.sh watch UUID and end turn. Terminal review uses bounded status/summary/peaks/check-tooling
against cap baseline and targeted log-grep/log-lines; missing fields stay UNKNOWN.

F03 generic-F question remains open; evidence applies only to concrete bounded u8/lt_u8/layout.
Post-call controls calibrate local predicates, not modifies instrumentation or callee failure.
Frame checks cover initialized protected spans; uninit checks are off. No all48 frame claim.
No caller-N16 theorem, sort8 contract, general aggregate, ordinary/CI admission, Mac/jobs3 or B2.
SPEC-FIX may change assumptions/source; transfer requires another review and possibly a rerun.
