# D0-P bounded semantic review

## Reviewed identities and scope

- Final candidate: `955cd015649aa79be511fe1732d48fdc8535741f`; tree `1c724bf33763251340efbdf9a8486a6278cafdc4`.
- Baseline: `a0a2386001a15fecfe2facc2f6cd87f3dee13b60`; packet inventory SHA256 `aa355b3ab5a8f4c123d73e74e95487431bad04f68fdf1d882a0bb670053ea830`; spec SHA256 `de7f7cf020fdf853b89f76405347719758a9e9a1eb20a562cd2cb15fb710e75a`; diff SHA256 `77b73efad3b4a5945b97d248d5d6f4817c3ae1120f8311d1ddab2993484d72c9`.
- Final delta inspected: `f3872f9ab3e44410b175defd5c5b2d1118b5c694..955cd015649aa79be511fe1732d48fdc8535741f`. `git diff --check` passes baseline..final; candidate checkout is clean.
- Script identities unchanged and verified: `curate_cbmc_trace.py` `7f446c7c44152caaf168afa4086c17bf891d12a87422dd43c920b27a27892f5f`; `test_curate_cbmc_trace.py` `4f71667f9537927f4149271add69bdd0763266fcbeaa067cbcfea4d302e4035f`; `capture_cbmc.py` `f9f896dc06fa55921d5743fd4b1b3b11e931cc4cbc2f183a81fe389cd5b464c9`; `test_capture_cbmc.py` `824c4441801fb4e75f2ddd32dc805aa796d054890e8da6da6ae74c2f5bc8f3e0`.
- Pinned API hashes match the earlier g1r/API-SOURCES.json verification.

## Findings and status

1. **Resolved — paired cases skipping prewarm.** AB/BA/D assert the normal export-worker prewarm path before the unchanged MostReachableItems ordering calculation. The actual order override remains after prewarm.
2. **Resolved — recursive stable Instance Debug.** The final delta replaces stable Instance/StaticDef debug payloads in prewarm, unit/order, harness-start, and points-to-root records with serde encoding. It narrows the unit record to encoded harness IDs, the existing machine model, and stub count, guarded by `assert!(unit.stubs.is_empty())`. Pinned `Instance` derives Serialize; its `InstanceDef` uses the pinned index serializer. These paths no longer call `Instance::Debug` (which formats `args()` and reaches `Ty::Debug`/`kind()`).
3. **Resolved — recursive MIR Ty/Span Debug.** Body, operation, Place, Terminator, LocalDecl, Ty, Span, and stable allocation/static snapshots use serde projections. Pinned `Ty` and `Span` serializers write only their numeric index; public `Body` and `Instance` derive Serialize. `cprover` includes the optional serde dependency. The type-codegen event serializes the existing stable Ty ID and formats the already-produced internal Ty/GOTO result inside the existing cache-miss closure, so it adds no stable-type conversion or body query.

A scan of added Debug formatting finds only rustc-internal graph/place data, the internal rustc type and CBMC GOTO values (including `goto_body`), and non-type source/layout metadata. Body snapshots serialize Span IDs opaquely; direct `Location`/source metadata Debug may format an existing Span for source coordinates, but does not expand a type or query/rebuild a body. No remaining new Debug formatting of stable MIR `Instance`, `Ty`, `Body`, `Place`, or `Terminator` was found. No model/check/operand/mask/state/CFG/runtime-call mutation or extra body query was found in the reviewed diff.

## Curator/capture and limits

- Curator validation is fail-closed for missing/null/wrong-type/partial trace data, source/hash identity mismatch, missing required symbols, incomplete failure traces, and output caps. It labels output as a curated subset, leaves causal claims false and causal data UNKNOWN, and preserves run statuses.
- Capture wrapper forwards stdout unchanged, records full-stream hash and retained/dropped counts, forwards TERM/INT/HUP, and uses Linux parent-death signaling with a race check. `COMPLETE` denotes drained stdout, not successful solver completion. The curator does not consume capture metadata; the current CI-REQUEST gates curation on COMPLETE metadata, no signals, complete/no-drop capture, and hash/exit/status consistency.
- Synthetic Python suites previously passed 23/23 (capture 8/8, curator 15/15); no real CBMC input was used. No unresolved concrete semantic findings remain for D0-P preparation. Rust compilation, model equivalence, actual ordering, runtime pointer/object bindings, causal attribution, and formal verification remain NOT_RUN. No runtime or proof credit.
