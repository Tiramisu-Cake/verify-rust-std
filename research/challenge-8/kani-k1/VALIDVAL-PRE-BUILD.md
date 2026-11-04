# VALIDVAL pre-build packet

Stage `validval-s1`; request `validval-s1-20261104`; proposed stable owner `k1-network`.
Coordinator GO must confirm that owner's slot is free at dispatch. No dispatch before GO.
Branch: `experiment/kani-k1-validval-20261104`; runtime Codex; no subagents.
Task: `TASK-VALIDVAL.md` at `ccb792af5e`; library commit `5aafa241396c3e78bedb2bfa64cfb795ee466e51`.
Tooling base: `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`.
Upstream `233f96f66a`; Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`.

## Exact diagnostic scope

All seven roots are in `slice::sort::shared::smallsort::verify::validval`.
The new module is gated by `cfg(kani_smallsort_controls)` at its sole registration.
Existing v7 files change only by that registration; no runtime or tooling changes.

| Root | Input / real route | Expected |
| --- | --- | --- |
| rejects_bool_byte_2 | ptr::read bool from aligned live u8 = 2 | FAILED, located valid-value check |
| accepts_bool_byte_0_or_1 | same load, arbitrary u8 assumed <= 1 | SUCCESS, both values covered |
| rejects_char_surrogate | ptr::read char from aligned live u32 = 0xD800 | FAILED, located valid-value check |
| accepts_char_scalar | same load, arbitrary Unicode scalar | SUCCESS, endpoints and gap edges covered |
| unstable_bool_n4_to8 | arbitrary valid bool[8], symbolic slice N4..8, Unstable entry | SUCCESS, each length covered |
| stable_char_n4 | safe from_u32 constructor, full scalar domain, scratch48, Stable entry | SUCCESS, return and reversed-input covers |
| unstable_nonzero_u8_n4 | safe NonZeroU8::new, arbitrary nonzero bytes, Unstable entry | SUCCESS, return and reversed-input covers |

Real comparators use strict `<`; no contracts, stubs, sortedness or permutation assertions.
Bool/NonZeroU8 select small_sort_network, whose N4..8/N4 bodies use insertion from 1.
These roots do not reach sort9, sort13 or network scratch merge. Char N4 executes
small_sort_general_with_scratch, insertion into initialized scratch halves and bidirectional_merge.
Covers after the call demonstrate normal return, including unsorted inputs; verify all cover counts.

Negative request `expect_check: "valid"` is a case-tolerant substring of "invalid"/"Invalid".
It is a triage filter, not evidence credit: inspect the complete failed description and location
in bounded rows/log-grep and require a value-validity failure at the deliberate load.
Pointer, alignment, unsupported-operation, or other failures do not calibrate valid-value checks.
Bool negative FAILED plus positive SUCCESS is mandatory before any real-route evidence credit;
char calibration is assessed separately. Missing covers or incomplete output limit any conclusion.
Preserve exact unsupported-operation text, located failures, compile errors and TIMEOUT separately.
The pin's [UB documentation](https://github.com/model-checking/kani/blob/cd355b0bccd32300713bc2ce4f765dafa1510607/docs/src/undefined-behaviour.md)
still lists invalid-value production as a limitation; this experimental packet tests its flag.

## Budget and controls

`diagnostic`, `gcb-e2-standard-4`, controls=true, valid_value_checks=true,
uninit_checks=false, jobs=1; 2 min/root, 14 harness-min + 30 overhead = 44 min.
Planned reserve: 44 * $0.0135 = $0.594; own spent $0; own cap $1.30; project cap $118.96.
One build, no retries. Only a compile-error repair is allowed, at most once, if spent + reserve
remains within cap; two full planned reserves total $1.188. No reservation is claimed before dispatch.
Window: main 150 min plus closeout 30 min; dispatch timing remains subject to coordinator GO.

## Validation and authorized next step

Before review: validate RUN-REQUEST with the existing Python validator; inspect generated flags,
match all seven root names to source, check cfg registration and immutable lane/v7 scope, git diff --check.
No local cargo/rustc/Kani/CBMC; this is structural validation, not a compile or proof result.
After exact-packet GO: recheck project budget and confirmed stable owner, dispatch pushed branch
via tools/k1g.sh; record actual UUID with validval-s1/request binding, then `k1g.sh watch BUILD`
and end the turn. Do not poll status. Budget refusal is a stop, not permission to change caps.
On wake: use only bounded K-1 summary/rows/peaks/log-grep, and check-tooling BUILD with the full base above.
Write RESULT-VALIDVAL.md <= 30 lines with identities, calibration, row classifications, scope and NOT_RUN;
commit/push with [skip ci], then REVIEW REQUEST <sha> / VALIDVAL ЗАВЕРШЁН and stop.
No full raw logs, archives, Cloud Logging, credentials or competing patches are read.
