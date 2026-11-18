# W14 — F4 conditional clone review

PREPARED_NOT_ISSUED. Exact committed author/package/source/tree/parent pins follow
READY15. Finish active S2 review, don't reset it; review this distinct package when
idle. Preserve current model/service tier, owner toggles Fast. No subagents.
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

New output `kani3300/wave0/f4-uninit-only-review/`: REVIEW.md/json, exact pins,
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
