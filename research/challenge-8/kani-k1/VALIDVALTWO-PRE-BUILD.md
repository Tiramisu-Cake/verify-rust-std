# VALIDVALTWO pre-build packet

Stage `validvaltwo-s1`; request `validvaltwo-s1-20261104`; runtime Codex; no subagents.
Branch `experiment/kani-k1-validvaltwo-20261104`; task `TASK-VALIDVALTWO.md` at `b20ef7d7e0`.
Library commit `5453d3515f19a5b63368710170a67631f2018b0f`.
Tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`.
Request SHA256 `d455ff141b7bead9b3bd42fe66803e781ce113c7da267cbe6c2fefa4407c0564`.
Stable owner `k1-merge`, authorized by coordinator's conditional GO for `c9ea5a1c04209f17337ab86a38b600001ababdf9`.
The GO explicitly permits the owner-only request change in a separate [skip ci] commit without renewed review.
Predecessor `7420db72-52f9-4f7e-9bdf-774780d91e84` finished FAILURE at `2026-11-04T20:05:57.831384Z`,
confirmed by watcher and one bounded status read. All diagnostic scope, limits and single-build constraints remain as reviewed.
Dispatch remains subject to the existing budget preflight; no build has been submitted yet.

## Exact diagnostic scope

All roots use prefix `slice::sort::shared::smallsort::verify::validval::`.

| Root | Input / real route | Expected; required covers |
| --- | --- | --- |
| accepts_bool_byte_0_or_1 | Existing ptr::read bool control, arbitrary byte assumed <= 1 | SUCCESS; byte 0 and byte 1 (2/2) |
| unstable_bool_n2 | Arbitrary valid bool[2], Unstable entry, strict `<` | SUCCESS; normal return and reversed input (2/2) |
| unstable_bool_n4 | Arbitrary valid bool[4], Unstable entry, strict `<` | SUCCESS; normal return and reversed input (2/2) |

Only two proof roots are added to `verify/validval.rs`; all existing roots and module registration stay unchanged.
Both new roots use cadical/unwind(20), as does `unstable_bool_n4_to8`, and its comparator and cover predicates.
Freeze + Copy and size 1 select the network entry; N2/N4 run insertion from index 1, without sort9/sort13 or scratch merge.
Fixed arrays pass their full slices; no symbolic length, contracts, stubs, sortedness or permutation assertions.
The module remains gated by `cfg(kani_smallsort_controls)`. Runtime, ordinary v7 roots, workflows and tooling are unchanged.
N8 is omitted: four rows would reserve $0.945 and exceed the authorized own cap $0.90.

## Budget and controls

`diagnostic`, `gcb-e2-standard-4`, controls=true, valid_value_checks=true, uninit_checks=false, jobs=1.
Three rows at 10 min/root: 30 harness-min + existing 30 min overhead = 60 min build timeout.
Planned reserve 60 * $0.0135 = $0.81; own spent $0; own cap $0.90; headroom $0.09; project cap $118.96.
The coordinator explicitly raised the task's original $0.80 cap to $0.90 in this session.
One build only; no retry or compile-error repair. No reservation, slot or active window is claimed before dispatch.
Window: main 90 min plus closeout 20 min; start timing and slot availability remain subject to coordinator GO.

## Validation and authorized next step

Before review: existing Python RUN-REQUEST validator; inspect generated flags and all three root bindings;
check fixed lengths, comparators, covers, preservation of existing functions, cfg registration and lane equality to tooling base;
check immutable v7/runtime scope and git diff --check. Structural checks do not establish compilation or proof.
Commits use [skip ci]; push without force. Stop at PRE-BUILD REVIEW <full source SHA> until coordinator GO.
After GO: recheck project budget via k1g.sh budget, confirmed free owner and exact pushed request/commit;
dispatch the pushed branch using existing k1g.sh, bind the actual UUID/source/request in this stage ledger,
then k1g.sh watch BUILD and end the turn. Do not poll status; budget refusal is a stop.
On wake: bounded K-1 summary/rows, targeted log-grep if needed, and check-tooling BUILD against the full base above;
check build/source/request/Kani identities and covers. Distinguish SUCCESS, actual invalid-value FAILED with exact location,
explicit unsupported copy_nonoverlapping text/location, compile error and TIMEOUT. Expected SUCCESS and gate are triage only.
Require positive control SUCCESS with both covers before crediting this profile. VALIDVAL previously established
negative bool byte 2 and char surrogate detection plus valid bool/char control success on this same pin;
its symbolic bool N4..8 timed out at 2 min and char/NonZeroU8 real routes hit unsupported copy_nonoverlapping checks.
Write RESULT-VALIDVALTWO.md <= 20 lines with identities, exact per-row text/location, and joint conclusions with VALIDVAL.
This is bounded safety/value-validity evidence only, not sorting correctness or other sizes/routes/types/uninit checks.
Commit/push [skip ci], then REVIEW REQUEST <sha> / VALIDVALTWO ЗАВЕРШЁН and stop.
No raw logs, archives, credentials, local cargo/rustc/Kani/CBMC, Actions or competing PR/code access.
