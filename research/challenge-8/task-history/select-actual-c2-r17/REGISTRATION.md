# R17 registration basis

Task `select-actual-c2-autonomous-2026-10-21-r17` has a fresh explicit Select authorization for phase `SORT4-ACTUAL-C2-2026-10-21-R17`, owner `select-sort4`, and lane `o26-sort4-c1-current-recovery`. The branch client must bind only this task's phase to its exact start (`2026-10-21T20:06:19Z`), main cutoff (`2026-10-21T22:06:19Z`), absolute cutoff (`2026-10-21T22:36:19Z`), 3600 Cloud seconds, 1200-second per-build maximum, and 240-second report reserve.

## Defect and applicability

R16's exact phase client accepts only the R16 identity and dates. Reusing it would either reject R17 or leave a branch-client path where an R17 ledger could not be checked against the task's authorized window. The recovery lane also needs an R17 adapter/profile route so the task reaches the full actual-body runner under the existing protocol and strict lane guards.

## Invariant

A dispatch is admissible only when the phase, owner, sole allowed lane, start/main/absolute deadlines, fresh 3600-second account, unlimited sequential-build count, maximum timeout, and report reserve match the explicit R17 task. The profile remains unaccepted, proof credit false, and all matrix cases NOT_RUN until evidence establishes otherwise. R16 and earlier pins remain unchanged.

## Distinguishing controls

Synthetic registration checks accept the exact R17 ledger and reject single-field mutations to owner, lane, each deadline, ceiling, maximum timeout, or build-count policy. Time-budget checks accept only 270..1200 seconds with a 240-second reserve and reject booleans/floats/out-of-range values. Environment and lane tests bind the exact profile bytes and R17 adapter. Recipe checks include the R17 profile/body/adapters and preserve the full R16 dependency closure. No Cloud, compiler, exporter, extraction, MIR, or verifier execution is part of registration.
