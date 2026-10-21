# A1 R12 S4 P-dispatch owner/span design

## Defect and applicability

The bounded P-dispatch trace has two identical threshold dispatch rows, one from the original `quicksort` caller and one from the diagnostic `a1_guard_observer`, plus one `small_sort` row. The existing classifier requires one global threshold row and has no source owner or call location to distinguish these calls. Separately, the structural collector skips MIR/AST caller binding for P-dispatch, so its caller AST field is absent and the matrix cannot validate the actual source callsites.

The current C patch already translates each source call with `State.body_name`, `call_loc` (the AST `CallExpr` location), and `fn_loc` (the MIR call span) in scope. Static source inspection confirms that `translate_fn_call` decodes `FnCallData.call_span` into `fn_loc` and passes it separately from the terminator `loc`; `translate_fn_call_rexpr` constructs `Ast.CallExpr` with `call_loc` and uses `fn_loc` for MIR operand translation. The source does not assert that the two span ranges are equal. Emitting both is diagnostic-only: it changes no resolver choice or verifier semantics. P-dispatch’s certificate binds its byte-identical positive source pair and separately keyed unit; the source inventory contains the exact quicksort signature and unique renamed observer. The collector joins every trace record to exactly one `(owner, callee)` compiler/AST call, checks each trace span against its own AST or MIR span, and requires both starts to be on the independently source-certified call line.

## Required fail-closed behavior

Accept only the exact three P-dispatch calls: one threshold and one `small_sort` call in `quicksort`, plus one threshold call in `a1_guard_observer`. Each record must have the exact compiler/source/AST owner, exact AST span, exact MIR span, and matching certified call line; original and translated common item names must be equal and `redirect=false`. The AST and MIR ranges are compared to their own records and are not assumed equal to each other. Missing, extra, duplicate, malformed, stale, redirected, wrong-owner, wrong-span, or unbound records remain inconclusive. There is no global-name count fallback. These observations remain structural and grant no proof or native-contract credit.

## Expected implementation surfaces

- `checked-threshold-contract.patch`: append owner and AST/MIR source spans to dispatch trace rows using existing translation context.
- `a1-call-binding.py`: add a P-dispatch-specific paired binding for the two certified source owners while retaining exact normal/readonly MIR equality, source call lines, generic identities, and direct argument roots.
- `a1-runner.py`: construct each owner’s AST call gate and perform strict trace-to-MIR-to-AST joins.
- `a1-matrix-classifier.py` and synthetic tests: require the complete three-call join; reject all ambiguity and identity mutations.
- The parent owns R12 profile refresh for C patch/final translator/helper/runner hashes. Do not rewrite historical profiles, evidence, or ledgers.

## Controls and scope

No fixture bytes change. No proof/model/domain/runtime semantics change. Existing Cloud source-preflight/compile and regressions must precede targeted rows. This patch’s static review must confirm the added fields come from the actual current caller state and the exact source call spans. No local compiler, verifier, full preparer, or full runner is invoked for this design/implementation task.

## Early diagnostic persistence

P-dispatch previously reached `persist_progress()` only after the structural collector returned and later matrix/report work could still exhaust the shared deadline. Immediately after its actual trace classification, the runner now writes `dispatch-join-observation.json` under that invocation’s existing evidence root. It contains the classifier result, Build/profile/source-pair/source-unit identities, verification exit and log digest, AST digest, and explicit non-credit/non-admission flags; it does not copy MIR, AST, or log content. A write error preserves the classifier outcome as `observed_classification` but forces the returned dispatch classification to inconclusive, so the matrix cannot admit it. Synthetic success, I/O-failure, and pre-existing inconclusive controls pass.

## Implemented and statically checked

The dispatch line now includes `State.body_name`, `Ast.string_of_loc call_loc`, and `Ast.string_of_loc fn_loc`. For P-dispatch only, the collector separately observes the original `quicksort` and `a1_guard_observer` bodies in both paired MIR modes, retains exact call spans, and checks each AST body/call against the certified source line and caller. The classifier accepts only the exact three owner/callee keys and compares each trace row’s AST and MIR span to those independently collected bindings, including the source line and untranslated common item identity. Any mismatch returns inconclusive; proof credit remains false.

Synthetic controls cover the complete triplet with distinct AST/MIR ranges on the same certified source-call line, zero/missing/duplicate rows, unknown owner, redirect, wrong AST or MIR span, stale source/log identities, missing caller bindings, and malformed span leaves. Matrix controls also cover wrong owner/source and missing/duplicate trace rows. The focused validation passed 106 tests across dispatch-diagnostic persistence, dispatch trace join, call binding, matrix classifier, AST gates, C-patch integrity, R11 dispatch, runner context, and runner lifecycle. A static replay from the exact pre-C translator SHA `f9d1097efa321b7c6496810990aae1f09584eb13da3a494d1c56641776c19f4d` produces translator SHA `570b7ac92e4c7f0a63097d28ea018033da2f5afeb4a0f7206d20dc8a11a73a71`; reverse replay restores the exact pre-C SHA. The resulting C patch SHA is `3549e93e80aa20f3827c821db60d7ce366557155b8b203a8acaff552c04f5cb6`. This is static source evidence only; Cloud applicability and runtime trace shape remain unverified pending the authorized Cloud lane.
