# RESULT-VALIDVAL

Stage `validval-s1`; request `validval-s1-20261104`; owner `k1-network`; runtime Codex.
Build `e60bcbdd-6e0b-48b1-ad22-ef98ba044389`; source `be6f8f2c70f2e15a2d9194e0e4129a87ac4612f9`; Cloud Build FAILURE, compilation succeeded.
Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`; library `5aafa241396c3e78bedb2bfa64cfb795ee466e51`.
Request SHA256 `4846df3da6e81992420b9a503c725140d537f751fb15d7d6423f192d9633073c`.
`check-tooling` PASS against `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`: source/run identities, six hashes, lane equality and k1-standard4 pool match.
Diagnostic: controls=true, valid_value_checks=true, uninit_checks=false, jobs=1, 2 min/root; outside organizer CI.
One build; actual ledger cost $0.1485, reserved $0, own cap $1.30; no retry or repair.
Evidence: bounded K-1 summary, rows 0..6 (next_offset=done), log-grep lines 2710..2787, check-tooling, budget; no raw evidence access.
Summary COMPLETE means all seven outcomes accounted for, not successful verification; gate=false and broad expect_check `valid` supply no proof credit.
Locations below use prefix `/workspace/src/library/core/src/`; roots use `slice::sort::shared::smallsort::verify::validval::`.

| Root | Actual classification | Exact failure text / location | Failed checks; covers |
| --- | --- | --- | --- |
| rejects_bool_byte_2 | FAILED: value-validity | Undefined Behavior: Invalid value of type `bool`; `ptr/mod.rs:1769`, ptr::read::<bool> | 1/33; 0/1 |
| accepts_bool_byte_0_or_1 | SUCCESS | No failed check/location; VERIFICATION:- SUCCESSFUL | 0/33; 2/2 |
| rejects_char_surrogate | FAILED: value-validity | Undefined Behavior: Invalid value of type `char`; `ptr/mod.rs:1769`, ptr::read::<char> | 1/33; 0/1 |
| accepts_char_scalar | SUCCESS | No failed check/location; VERIFICATION:- SUCCESSFUL | 0/33; 4/4 |
| unstable_bool_n4_to8 | TIMEOUT | CBMC timed out.; no failed-check location (log 2740); 2 min limit | unavailable; unavailable |
| stable_char_n4 | UNSUPPORTED OPERATION (reported FAILED) | Kani currently doesn't support checking validity of `copy_nonoverlapping` for `*const char`; `ptr/mod.rs:578`, ptr::copy_nonoverlapping::<char> | 1/466; 0/2 |
| unstable_nonzero_u8_n4 | UNSUPPORTED OPERATION (reported FAILED) | Kani currently doesn't support checking validity of `copy_nonoverlapping` for `*const num::nonzero::NonZero<u8>`; `ptr/mod.rs:578`, ptr::copy_nonoverlapping::<num::nonzero::NonZero<u8>> | 1/701; 1/2 |

Calibration established on this pin/profile: ptr::read detects bool byte 2 and char surrogate 0xD800 at the load; the same loads pass for {0,1} and all assumed Unicode scalars, with all positive covers satisfied.
No false alarm was observed on those valid calibration paths; this does not establish absence of false alarms in SmallSort.
No real-route safety/value-validity success is established: bool is unresolved by timeout, while char and NonZeroU8 hit explicit unsupported checks, not invalid-value counterexamples; partial covers do not override those outcomes.
Bool N4..8 and NonZeroU8 N4 select the network entry's insertion body; char N4 selects general with scratch48; covers do not establish successful completion for all attempted routes.
NOT_RUN: separate per-length bool proofs, sort9/sort13/network scratch merge, other sizes/types/invariant-bearing layouts, uninit-checks and a wider validity matrix; no sorting-correctness assertion was requested or proved.
No compile error occurred, so the compile-error repair allowance was not used; the one-stage experiment is closed with these limitations.
