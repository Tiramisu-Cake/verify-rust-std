# R23 runner fixes — design note (2026-10-24)

## Defects and applicability

1. `prove.py`'s source-pin check handles two R22 paths: the owned-NLL diagnostic profile and the compile-only profile. In the latter branch it currently expects the NLL translator digest, although compile profile 65f is pinned to `R22_TRANSLATOR_SHA256`. This rejects the previously admitted compile-only route. Only the compile-only expected translator digest changes; the NLL route keeps its own digest and reversible profile chain.
2. `first-callback.run` copies the caller environment for campaign execution but leaves inherited `VF_EXPORT_OWNED_NLL_FACTS` intact. Callback dispatch removes it before setting per-case flags, while direct R11 placement derives a child environment from the campaign environment and passes it to `_tool_tree`. An inherited `=1` can therefore enable owned-fact export in direct placement runs. Remove it from copied campaign, placement, and direct replay environments; never mutate the caller's mapping.
3. Owned-NLL capture currently follows `actual_callback_case`, which also means “eligible for existing callback trace” and is passed for mutation controls and derived body-isolation cases. Keep that trace behavior unchanged, but carry a separate capture-eligibility bit that is true only for the registered positive full-body, original-local-caller, or raw-local-caller target execution.

## Invariants

- Profile source pins and registrations remain exact; no profile, source, or tool pin is changed. Both 65f and owned-NLL source-pin routes remain independently checked.
- `VF_EXPORT_OWNED_NLL_FACTS` is opt-in per authorized exact positive target execution. Inherited values are stripped from copied campaign/placement environments, and the caller's original environment is unchanged.
- The campaign's `full_body` execution is the original local caller target and is eligible only for its named positive case. The raw local caller is eligible only through its exact source-gated diagnostic dispatch. Body-isolation derivations and controls remain ineligible.
- Existing R9/R11 trace, label placement, native placement, control dispatch, classification, source identity, exit-code, timeout, receipt, and proof-credit behavior is preserved. NLL eligibility does not imply acceptance or proof credit.
- Mutation controls and derived body-isolation executions cannot receive owned-NLL capture, even when they remain actual callback cases for the existing trace path.

## Distinguishing controls and tests

- Exercise main's exact source-pin checker against compile profile 65f and owned-NLL profile 3fec; mutate a translator pin in each route and require rejection.
- Start with caller environment `VF_EXPORT_OWNED_NLL_FACTS=1`; show campaign, placement, and direct replay child environments omit the inherited value, while the caller mapping remains unchanged. Separately show the authorized exact positive case gets `=1`.
- Show exact positive capture eligibility independently from `actual_callback_case`: false for R7/R9 mutation-control dispatch and body-isolation-derived cases while the existing trace flag remains operative; true only for registered full-body and caller targets.
- Preserve service failure semantics for nonzero exits, exceptions, timeout, partial/missing/null/wrong-type receipts, explicit `NOT_RUN`, and source-stage-target mismatch; affected cases must remain inconclusive or retain their existing error classification without gaining acceptance or proof credit.
