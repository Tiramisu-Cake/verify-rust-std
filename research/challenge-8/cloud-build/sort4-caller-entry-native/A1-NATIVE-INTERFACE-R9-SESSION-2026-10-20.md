# R9 session — native interface proof registration

Session: `select-native-interface-proof-autonomous-2026-10-20-r9`; owner
`select-sort4`; branch `research/night-select-sort4-cloud-2026-10-09`.
Authorization is the explicit `CURRENT-TASK.md` assignment. T0 is
`2026-10-20T17:07:04Z`, main deadline `2026-10-20T19:07:04Z`, absolute
deadline `2026-10-20T19:37:04Z`; ceiling 3600 Cloud seconds, used 0, carry 0.
Lane: `o26-sort4-c1-current-recovery`; phase:
`SORT4-NATIVE-INTERFACE-PROOF-2026-10-20-R9`; timeout ceiling 900 seconds.

## Defect, applicability, and rationale

R8 is closed and its phase, profile, deadline, and ledger must remain historical.
The R9 assignment authorizes a fresh 3600-second window and a new phase. Current
transport and consumers accept only explicitly registered phases; reusing R8
would bind the run to expired authorization and would not establish R9 identity.
The R8 transport/entry/adapter/focus-helper/core-consumer/recipe pattern is the
applicable registration model. Register R9 as a distinct exact profile and
dependent closure while retaining existing guards, source-core byte identities,
environment equality, protocol checks, accepted=false rejection, focus/dead-code
controls, and baseline→overlay→C source transitions.

The candidate source repair `8e46fbf4c603e9a0133d3024ce22e73958d73542`
qualifies four accesses as `Ast.sized` while preserving predicates and control
flow. It is applicable to the prior R-only compile failure, but actual
compilation, extraction, and verification remain NOT_RUN. R9 registration does
not change proof semantics, runtime std, tool semantics, native contracts,
equality/refinement criteria, or proof credit.

## Distinguishing controls

Run only synthetic/static registration and service tests locally: exact R9
success plus wrong/unknown/old/missing/null/bad-type/hash/path/environment,
protocol/core mutation negatives, and runner success/error/NOT_RUN/partial
preservation. Check dependent pins and complete recipe closure against committed
files and hashes. Do not import the real proof core in isolated activation tests.
Independent review of the current diff/dependencies and the existing Cloud
preflight remain mandatory before any coordinator submission. These controls
establish registration integrity only, not source applicability or proof.

## Checkpoint

At activation, proofs remain at the R8 baseline: 0 formally closed obligations
and 0 independent B1/B2 credit. Actual candidate compilation and verifier are
NOT_RUN. Registration work, any later Build charge, and proof progress are to be
reported separately. Historical R8 ledger and releases remain untouched.
