# CC4 cycle map — saved CC3 exports, static source, missing windows explicit

Worker14, 2026-11-13. Reference CC3 76a706f8f8c5b0471bd5c8e6b48cdaf45bab9b66.
Allowed saved artifacts: /root/kani3300-h1-ci/cc3-art/tmp.WJBbBrB7p1/mode-boundary-results/.
CC3-OBSERVATIONS.json pins inputs/exports/observations and copies selected fields.
All three saved inputs match the unchanged recursive.rs SHA256 ea297d80b8c0e9a0493ff65e586bc39da5cd7ceaa295ed4ed67b9380567f4bf0.
Exports report clean 02ad55099ce1df1e844de5e42393d4079a1833ac; local git diff
against CC3 changes only .github/workflows/. This binds source equivalence,
not independently authenticated binaries or formal proof credit.

## Per-root reported paths

1. recursive_check: exact root Item DefId(0:62 ~ recursive[131c]::recursive_check), args[].
   Frames: root → recursive_transfer (DefId0:8,args[],Source) →
   recursive_transfer::kani_register_contract (DefId0:16, MU<u8>,Closure0<…>) →
   closure0 (DefId0:20,<…>) → closure0::closure1 (DefId0:24,<…>) →
   closure0::closure1::closure1 (DefId0:26,<…>) → recursive_transfer (repeats frame1).
   No frames omitted in this saved reason; closure/register generic strings ARE
   truncated at192 characters. Caller MIR locations and selected snapshot origins
   are absent. Exactly one failed property, class unsupported_construct; covers0/6.
2. recursive_ordinary: exact root Item DefId(0:63 ~ recursive[131c]::recursive_ordinary), args[].
   Frames: root → recursive_transfer (DefId0:8,args[],Source) →
   recursive_transfer::kani_register_contract (DefId0:16,MU<u8>,Closure3<…>) →
   closure3 (DefId0:32,<…>) → closure3::closure0 (DefId0:33,<…>) →
   recursive_transfer (repeats frame1). Same missing generic/callsite/origin data;
   no omitted frames. Exactly one unsupported_construct failure; covers0/6.
3. recursive_simple_check: saved export COMPLETED/SUCCESS, failures[],
   checks365 (356 successful,9 unreachable), covers6 (4 satisfied,2 unreachable).
   No reported cycle or repeated key. Contract target is bounded_transfer; actual
   reached covers are bounded_transfer::closure2::closure1.cover1/2 and the two
   outer return covers. Source bounded_transfer contains no recursive call.
   The collector says companion_pass=false solely with PATH_COVERS_INCOMPLETE:
   it also requires the unreachable wrapper covers. This is an observation/
   generated-body-cover binding gap, not a recorded Unsupported. Do not change
   the collector here or rewrite the historical result as qualified PASS.

## Established / not established

Actual runtime-bounded recursion exists in recursive_transfer's source body;
the two saved roots demonstrably hit CC1's repeated-key guard. Bootstrap
RecursiveCheck and Assert closures contain the corresponding body closures.
The register resolver replaces the source panic with run_contract_fn using the
same generic arguments; delayed_ub selects only registration/discarded overrides,
others use instance.body(). ActiveCalls is freshly allocated per entry root.
These static facts and shortened paths support a source-recursion diagnosis.
They DO NOT close exact selected-body/callsite attribution or establish a
registration-only cycle, cross-root contamination, or an analysis cycle in
SimpleCheck. Classification of the full two cycles remains INCOMPLETE.

## Minimal missing-data request / diagnostic candidate

For each cyclic root request only the active entry and each listed call edge:
full owner Instance (kind/generic args) or its exact compiler symbol; selected
snapshot provenance and origin symbol; caller selected-owner symbol, MIR bb/index,
source span and typed call terminator. Include the repeated frame1 and the body
closure → recursive_transfer edge. Existing typed pre-delayed MIR windows suffice.
For SimpleCheck request entry → bounded_transfer → register → selected closure2
→ body closure1 and its relay calls, plus source↔cover binding; there is no
cycle key to request in its saved successful export. Compare isolated-bounded.

Candidate augments existing error text only: Source / RegistrationOverride(origin)
/ DiscardedClosureOverride, exact owner and selected-origin compiler symbols,
original Instance Debug and incoming caller bb/index/span. Snapshot identity is
(owner,provenance,origin) in one immutable map; it is not a MIR-content hash.
Synthetic CRATE_DEF_ID from internal_mir is deliberately not used as identity.
Root + last10 active frames + repeated frame; each frame≤4096 characters, with
explicit omitted counts / truncation markers. Truncated data never closes a path;
request the specific missing typed window from coordinator, not a full log/archive.
Caller locations do not participate in key equality. In a fixed map the new
provenance distinguishes exactly the same instances/bodies as the prior boolean.
No fallback/SCC, graph joins, analysis depth, seeds/checks/setters or schema change.
Candidate typecheck, diagnostic output and complete paths remain NOT_RUN/UNKNOWN.
