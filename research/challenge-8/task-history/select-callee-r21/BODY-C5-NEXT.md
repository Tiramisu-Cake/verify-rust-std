# R21 body c5 continuation plan (source-only)

This note records the smallest next step after the R21 actual `select_unpredictable` callee is independently accepted. It does not enable a route, request a Build, or claim proof credit. The exact R21 body profile remains inactive (`cloud_build_enabled: false`; acceptance, admission, and credit fields false).

## What is already present

The dormant R21 body profile and copied constructor already select five indexed comparator groups: `actual_indexed_calls: 5`, with the five-call constructor dispatch in `a1-actual-body-r21.py` (`construct_c5`) and exact c1–c5 source coordinate checks. The full source gate still requires exactly 5 `is_less(` calls, 8 `hint::select_unpredictable(` calls, and 4 `ptr::copy_nonoverlapping(` calls. The profile pins the R19-reviewed c5 recovery overlay (`actual-sort4-c2-recovery-r17.patch`, SHA-256 `4aa15fdc36925d69903244526f2fd80100c7f1a8e0b9433e4b40017884b5f532`, result `b5ea96a19481383a2cbc82fb8f479095d9fdabeecd531b3a2e02cb1b59ba180d`), the four-copy component, the pure selector permutation component, and their manifests. `a1-actual-body-r21.py` wires the `actual_indexed_calls == 5` branch to `construct_c5`, emits c5 coordinates, and adds the c5 resource-control set.

Thus no new count-five profile edit or second c5 patch is justified in the current R21 candidate. If integrating from an earlier count-three profile instead, the minimal profile delta is `actual_indexed_calls: 3 -> 5` plus the exact c5 overlay/result/manifest pins and refreshed profile/recipe/closure hashes; do not alter source hashes or relax the 5/8/4 gates.

## Required sequence and gates

1. Close and independently accept the actual `select_unpredictable::<*const T>` callee under the same toolchain. Acceptance must cover the actual selected branch, checked normal and unwind ownership posts, forget/guard ownership, and the call linkage used by this body. The branch-selected R21 row alone is not enough: `S3-branch-selected-evidence.json` reports that it reached normal-result equality but the full-owner forget lost the selected-payload relation. A certificate refusal, parse result, `NOT_RUN`, or selected-branch-only row cannot be treated as callee acceptance.
2. Only then prepare a separately reviewed body-route candidate that carries the accepted callee's exact source, body, and unit certificate pins and an explicit checked linkage into all eight call sites. Do not install an assumed summary or enable an unverified intrinsic route. Keep the default-route pins and same-site omission controls exact.
3. Keep the R21 c5 focus at 5 and require source-bound coordinates for c1 through c5. Re-run the count-independent c1, c2, c3, and c4 control families at count 5, then the five-group c5 controls (positive no-deferred-suffix case; escape, missing marker, and cross-scope-read negatives). Each negative must fail at its intended scope validator. A c5-only pass does not replace lower-layer control requalification.
4. Preserve the body-wide source counts 5/8/4, complete runtime-byte equality after ghost stripping, normal and unwind posts, resource/leak inventory, and the checked copy-component route. The four-copy component and selector-permutation component remain useful independent gates, but neither is an actual callee proof nor a substitute for the full body result. Continue to report the selector component as Boolean/index algebra only until source-to-pointer/call binding is proved.
5. Keep every partial result classified as diagnostic/inconclusive. Require the complete actual body and all applicable controls/matrix rows to terminate successfully before any body acceptance is considered. The route profile, recipe, closure, and lane remain inactive until exact registration/review under the existing R21 phase window and ledger; this note grants no new budget or authorization.

## Historical C5 decision

Historical `select-c3-r19/C5-review.json` records the count-five candidate `34e37669ba138e3a815465bf06704bcf0f905413` as `GO_WITH_NITS`, but explicitly says its prerequisite was not met: S2 stopped at the first `select_unpredictable` selector, so the c5 positive and c5 resource controls would fail before reaching that layer. It was correctly not submitted. Its count-five translator work is reusable only through the current exact pin in the R21 profile; it does not discharge the callee blocker, establish body proof, or justify activation.

The historic review also requires transport-cap rechecking and count-five requalification of c3/c4 controls. Current R21's focused closure is a separate source candidate; do not infer current payload size from the historical 192-chunk figure. Measure/review the exact closure after any authorized route integration.

## Evidence boundary

This plan is a static reading of the dormant R21 profile/body source and the historical C5 review/candidate. No preparation, reconstruction, compiler, exporter, verifier, Cloud Build, or proof-credit action was performed. No source or profile was changed by this plan.
