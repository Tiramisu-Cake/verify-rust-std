# R10 deliverable-native phase registration rationale

## Applicability

R9 is closed with its unused balance retired, so its authorization, ledger,
profile, and dispatch binding cannot be reused for a new proof attempt. R10 is a
separately authorized bounded phase on the same existing recovery lane and the
same A1 experiment protocol. It needs a distinct authorization ID, ledger
identity, profile, entry adapter, and runner adapter so coordinator-provided
phase/profile bytes and the published source closure identify R10 explicitly.

## Scope and guarantees

Keep the protocol phase `SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17`,
the existing lane and owner, the R9-published source/tool inputs, and all source,
caller, admission, profile SHA, environment, and proof-credit gates. Register
R10 consumers at the entrypoint, runner adapter, focus backend, shell branch,
recipe source closure, and isolated activation/dispatch/profile-binding tests.
The R10 profile has its own authorization phase and budget account; it does not
inherit R9's spent/retired accounting or historical proof claims. The R9 profile
and evidence remain unchanged.

This registration adds no proof result and changes no core theorem, source
inputs, verification predicate, runtime contract, or trust assumption. The
shared core runner and control/ledger changes are maintained separately. The
R10 timeout registration must agree with the separately maintained coordinator
ceiling before any submission. These edits only make the authorized new phase
resolvable through the existing dispatch chain; they do not establish
applicability, successful delivery, or proof acceptance.

## Validation limits

Validation is limited to static source closure/hash checks and isolated
synthetic authorization/profile/dispatch tests. No local preparation,
extraction, compiler, verifier, full runner, or Cloud Build is performed as
part of registration.

Main integration also registers R10 in a1-tool.FOCUS_PROFILE_NAMES: reconstruct mandatory focus controls resolve the authorization-specific profile there separately from a1-focus-backend. Its helper pin is advanced only in R10; old profiles stay frozen. Active focus regression test now checks current R10 core/tool pins.
