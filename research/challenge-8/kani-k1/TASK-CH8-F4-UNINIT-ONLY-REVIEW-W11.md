# W11 — independent F4 conditional clone review

ISSUED by owner14:14 to independent11 (/new), who did not author F4. W14 remains
on S2; do not interrupt it. Preserve current model/service tier, Fast OFF. No subagents.
Exact g0 package **a16ef717e18ca8263e360c24058b13a3ef4d4605**, directory
`kani3300/wave0/f4-uninit-only/`; source **ca1452227d6ad319f1b9bc1ad33bf618120733eb**,
tree **baedd51d92073ecb2b96991bae7dc562ee8f58a2**, parent **b5a9678fd7c2a0f67c3fcafd90057fc2afaf9b5d**.
Source worktree `/root/kani-f4-uninit-only-w15` read-only. Author packet names14 as
reviewer in planning metadata; owner now explicitly substitutes independent11,
so do not require author-plan churn solely for that label. Approval must name11.
Correctness verification, not security work; STOP only real blocker, not volume.
Contract TASK-CH8-F4-UNINIT-ONLY-W15.md; STYLE-UPSTREAM-RULES.md applies.

Narrow source delta from publishedb5a9678fd7c2a0f67c3fcafd90057fc2afaf9b5d,
tree8585336ed35a14fe0fc157a7ca4e0d52075c0e49. Inherit prior F4 lifecycle/source
review by exact byte invariance; no repeated full compiler audit. Predicate equals
DelayedUbPass::is_enabled/ExtraChecks::Uninit, independent of DumpMirPass presence.
On-mode whole transformer isolation remains; off-mode shared transformer and cache
lifetime match main, all pass/cache/loop metadata stay coherent. No unrelated
optimization or global check suppression. New source parent must be b5.

Review existing regression's both-mode arguments/env/feature validation, both cfg
call paths, singleton/paired semantic inventories, initialized SUCCESS and enabled
unsafe failures, ordinary disabled-mode expectations and unchanged checks. No
invented native baseline/runtime/causal/performance result. Python/static/oracle
checks only, no compiler/Kani/full runner. Runtime new head NOT_RUN.

Verify source/patch/hash binding, unchanged16standard workflows and resource/
dependency/toolchain scope; review full native push CI plan on the **new** final
head (kani/format/deny) and deferred upstream PR checks per owner's policy. No-skip
same-tree final head sibling of prepared candidate with parentb5, whole pushed-range
skip check. Old run44274306776 remains old-head evidence. Candidate/PR Testing
must not promote it to validation of new conditional clone/test revision.

New output `kani3300/wave0/f4-uninit-only-review-w11/`: REVIEW.md/json, exact pins,
validation/provenance/hash manifest,HANDOFF APPROVE/CHANGES_REQUIRED. Findings
original15 via coordinator; immutable new repair + same reviewer delta review;
don't edit author code/old outputs. If APPROVE/no blockers root prepares exact
GO-request prospective last item1 29/29; no CI or publication by reviewer.

No CI/push/PR/compiler/verifier/full runner/rerun/cancel/labels/source/ledger/
reservation/budget actions. Current28/29,item2 provisional10/14,total38/43 reference;
owner alone dispatch/accounting/publication. Paths from
`/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/`.
Exact ownpaths commit --only, `[skip ci]`, Tiramisu-Cake <igkharin@gmail.com>.
Final `READY <full g0 SHA> <verdict>`.
