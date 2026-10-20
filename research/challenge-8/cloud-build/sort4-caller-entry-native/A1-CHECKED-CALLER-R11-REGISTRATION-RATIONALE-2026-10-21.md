# R11 checked-caller phase registration rationale

## Applicability and authorization

R10 is closed; its unused balance was retired and cannot fund another attempt.
R11 has a separate authorization, phase, profile, entry/runner adapters, and
ledger on the existing `select-sort4` recovery lane. The authorized window is
T0 `2026-10-20T21:41:43Z`, main deadline `2026-10-20T23:41:43Z`, and absolute
deadline `2026-10-21T00:11:43Z`; the fresh ceiling is 3600 Cloud seconds with
90–1200 second builds, a 60 second queue envelope, and 240 seconds reserved for
package/verdict completion. R10 history, spend, and profile bytes remain frozen.

## Scope and preserved guarantees

R11 continues the checked caller/native P1 experiment protocol on the same
existing lane and owner. It binds a new profile SHA and protocol phase through
the existing coordinator environment, entrypoint, runner adapter, recipe source
closure, and control validation. Existing source applicability, caller,
admission, environment, evidence, proof-credit, and soundness gates remain in
force. Profile pins for files owned by other R11 workers may be refreshed by the
integrator after those changes are complete.

The R10 lossless source restore codec is reused only for the explicitly
R11-authorized phase. R11 preserves source payload SHA checking, exact restored
source bytes, source-input archive verification, the 191-source-substitution
ceiling, 3990-byte substitution chunks, nine reserved substitutions, ten-source
values per group, the 200-substitution Cloud limit, 4000-byte value limit,
8×3500 compressed-config bound, and the maximum coordinator-generated
dispatch-token length. No decoder or service contract is weakened. The delta
controls require exact round trips for representative JSON values and source
bytes, corruption rejection, and configuration sizing with a real maximum-length
dispatch token. Legacy phases continue using their existing gzip restore path.

This registration does not claim a proof result, change source inputs or the
verification predicate, or alter runtime algorithms, contracts, ownership,
posts, or tool semantics. It creates a fresh bounded authorization and resolves
it through existing dispatch consumers. The R10 profile, ledger, evidence, and
closeout records remain historical and unchanged.

## Validation limits

Validation is limited to static closure/hash inspection and small isolated
synthetic authorization, activation, transport, configuration-bound, and
service-path controls. No source extraction, compiler, verifier, full runner, or
Cloud Build is run as part of registration.
