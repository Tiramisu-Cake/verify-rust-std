# Worker11 → Worker13

READY for integration, not P1 proof acceptance.
Frozen source: `3f469d3ba2e94d7129e66e53ea76df883ff9c946` on work/ch8-s1-model-w11.
Patch/hash/parent/tree: INPUTS.md and model-source.patch.
Accepted API/visibility: INTERFACE.md (worker13 accepted via internal thread).
Controls: CONTROL-MAP.json / CONTROL-MAP.md,12 opt-in rows, outcomes NOT_RUN.
Independent static review: REVIEW.json (Luna HIGH GO_WITH_NITS).
Types/width/lifetimes: TYPE-REVIEW.md. Scope: MODEL-SCOPE.md.
Local sanity evidence/limits: VALIDATION.md / synthetic-result.json.

Integration requirements owned by13:

- Only register model under cfg(all(kani,kani_smallsort_sorting)); inside verify use
  pub(super) mod sorting_model. Register controls with additional controls cfg.
- Add cfg-gated fn_traits feature; existing baseline has unboxed_closures and
  min_specialization. Do not add generic caller bounds or change runtime algorithms.
- Actual attrs explicitly guard !enabled||post, taking old(snapshot(v)) by VALUE.
  Bind exact same T/F/pre-state. No borrowed old(&v), Cell-after-mutation snapshot,
  trusted summary, panic stub, unchecked frame or invalid storage references.
- If old capture requires raw adapter or actual compiler rejects the interface,
  return a concrete finding to11, preserve guarantees, STOP at the assigned boundary.
- Integrate sequentially and freeze exact combined source/control/tool identities.
  Reconcile prospective source selectors against actual compiler inventory; only
  complete source-bound positives/named negatives + useful covers meet P1.
- Keep these controls out of ordinary inventory. Combine them with actual six
  PFC, default+override false-ensures attachments and bridge; no model-only dispatch.
  All costs/qualification are NOT_RUN; coordinator owns shared S1 cap2/Cloud$0.

No smallsort.rs, registration, old models, FnPtr comparator, leaf module, Kani
checkout, CI script or shared ledger changes were made by11. No push/CI/publication.
