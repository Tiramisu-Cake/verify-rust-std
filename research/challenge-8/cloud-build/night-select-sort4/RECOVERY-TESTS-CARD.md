# O26 recovery diagnostics, one hosted build

## Scope and hypothesis

Use the same fresh Cloud build to establish the canonical O26 source pair,
complete nine-body normal/readonly MIR and refinement capture, and the
unchanged refreshed full-proof baseline. Then run four changed diagnostics:
nested Drop proof order, actual sort4 AST scope print probe, strictCUT
declaration relocation with translated local IDs, and wrapper rebase source
capture. The first three use separate `/workspace` tool copies and record
production source/binary comparison. The fourth regenerates only the exact
source pair and fingerprints with the existing wrapper-rebase preparation;
it does not run a verifier profile or wrapper control. None changes the
production verifier, std runtime, specifications, kernel or proof acceptance
rules.

The nested TEST asks whether moving exactly the existing nested Drop AST
declaration before the outer body exposes the actual nested proof and its
first normal/unwind resource barrier. The AST PROBE prints the actual sort4
item/scope structure while retaining the stock reserved-marker refusal.
The relocation TEST asks whether the mapped-ID declaration change, after
strictCUT, moves the positive callback beyond the original first lifetime
barrier without weakening strictCUT or a normal/unwind post. The wrapper
capture asks whether a new source version has the expected source-pair,
cardinality and graph fingerprint needed to derive fresh exact component-17
metadata before any profile-23 or comp19 run. All four are diagnostic,
including a zero verifier exit in any isolated tool copy.

## Exact work and dependencies

The entrypoint enables only `O26_WITH_NESTED_PROOF_ORDER_TEST`,
`O26_WITH_SORT4_AST_PROBE`, `O26_WITH_CUT_RELOCATE`, and
`O26_WITH_WRAPPER_REBASE_CAPTURE` after the canonical baseline in
`run-o26-refresh.sh`. Owner controls, A1 isolation, coordination regressions,
wrapper profile/comp19 controls and actual sort4 full capture are disabled.
The recipe transports the full O26 source/capture and
patch chain, nested TEST patch/card, AST PROBE patch/card and first-call source
helpers, plus the strictCUT, relocation and mapped-ID patch chain and the
callback capture's proof inputs, and the wrapper-rebase preparation and card.
It also transports each diagnostic runner,
auditor and provider-overlay helper. The source bundle must contain committed
versions of these paths; a working-tree-only correction is insufficient.

There is one production source build and three isolated console rebuilds;
the AST probe additionally performs its required actual-source baseline.
These stages can consume substantial Cloud time and payload. The recipe adds
no new dependency download or separate control matrix. A missing or stale
pin, timeout, provider refusal, capture mismatch or packaging failure is
inconclusive; it is not a negative proof result.
The 79 selected proof files contain about 1.78 MB before compression.
Concatenating all selected current proof/infra file bytes compresses to about
489 KB, close to the source-input transport's roughly 572 KB encoded-payload
ceiling; Git-object metadata and per-object compression make this only a rough
estimate. The actual committed payload must pass the controller's bounded
transport check before dispatch. A payload refusal requires a narrower recipe,
not an unchecked transfer.

## Outcome and boundary

Preserve each helper's complete logs, source/MIR/refinement identities,
isolated source and binary audit, and raw exits. The nested result is useful
only if nine serialized declarations are preserved and the seven prefix
headers precede nested then outer; the first nested barrier or complete nested
normal/unwind proof must be reported. The AST result is useful only with the
unchanged source/MIR pair, exact print-only AST trace and retained baseline
reserved-marker refusal. The relocation result is useful only with exact
strictCUT plus the two declared relocation patches, mapped six-removal/
one-insertion trace and unchanged source/MIR, followed by its actual first
barrier or full exit zero. The wrapper source capture is useful only when the
new canonical source pair, source order, body count and graph fingerprint are
recorded; no old component-17 or profile-23 pins transfer automatically.
All four remain `accepted=false`; a full target
acceptance still requires the separately pending ownership, alias, lifetime,
bound, heap, unwind and negative gates.
