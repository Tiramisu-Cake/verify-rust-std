# R21 payload identity across actual forget: owner decision proposal

## Observed blocker

Build `1bbfc87e-8b0a-4042-b54f-71acb3690dd6`, candidate `a1be60b6`, admitted and executed the branch-selected unit. Both certificate controls report intended refusal. The positive passes the prior wrapper-ownership obligation and fails its normal post at `verified/lib.rs(143,45-47)`: `Cannot prove result6 = (condition ? true_val : false_val)`. Exact Brief log lines566–577, file `3fb25ee4ce631333a21b9c283ab9939e37c0517f0044f2ba6781a49725564f78`, SHA256 `3b81cdde5381d756191ed2350d5468226aa8935c274dac0619daa78ad5bf339a`.

The current guard own(t,g) hides its pointee payload existentially. Passing the whole chunk through the checked generic owner-preserving forget contract loses the relation to the original input. Closing fresh wrapper ownership does not restore that equality.

## Proposed bounded candidate (not authorized or implemented)

In a new opt-in same-unit callee candidate only, change the unsafe exact-std-body `checked_forget_owned<T>(t:T)` contract from requiring/returning the full `<T>.own(tid,t)` to requiring/returning **exactly one half** of that same predicate. Keep its exact `let _ = ManuallyDrop::new(t);` body, thread token, no-unwind post, source/MIR/one-call correspondence and validity/leak/refinement checks. Do not change the global SAFE std forget summary, guard-own definition, algorithms, actual std signatures or memory model.

At the one exact guard call, split the existing truthful full guard-own chunk. Open and retain one half of the selected-cell points-to chunk in the caller; give only the other half to the checked callee. After forget, reopen the returned half and merge it with the retained half. The two fractional permissions to the same logical selected cell must agree on the payload, preserving its equality to the selected original input. This uses existing permissions, not an address-only ownership bridge, assumed purity, Copy/Freeze or guard-own=true.

This is a proposed checked fractional-resource proof, not an established proof. The half-ownership callee and every obligation must verify in Cloud before use. If the existing ManuallyDrop lowering or predicate rules do not admit the half contract, retain that failure rather than add a trusted premise.

## Required controls and boundaries

Fingerprint and certify exact changed callee/outer source and MIR under a new narrow opt-in, including typed actual forget Move, normal target and shared cleanup. Retain default full-owner route and certificate refusals. Add same-site missing retained-half / wrong payload / duplicate half or lost half controls, callee false post / duplicated ownership / leak controls, and the full normal/unwind/nested-Drop/refinement matrix. An omitted wrapper close still requires a final-select failure rather than certificate refusal.

R21 explicitly says a broad forget summary requires an owner decision. Although the call-site exposure would remain the single source-pinned guard call, this changes the generic adapter's accepted ownership pre/post; authorization is therefore requested before implementing or building that extension. Existing R21 T0, deadline, ledger and budget remain unchanged. If declined, the proof remains open at normal-result equality; independent transport/source work can proceed.

## Owner decision received

The owner explicitly answered “Разрешить узкий fractional-кандидат” in this R21 session. This authorizes implementing and Cloud-testing this bounded candidate within the existing window and budget. The implementation retains the half cell before the first guard predicate close (closing a full existential guard would already hide the payload); no new trust/model premise is authorized. It remains unverified until the checked same-version callee/body/controls pass.
