# Merge-R20 — accept the checked raw caller cleanup, then original borrow/unsize

Task ID: `merge-unwind-acceptance-autonomous-2026-10-23-r20`; previous task: `merge-unwind-cleanup-autonomous-2026-10-22-r19`.
Owner: **Merge**. Phase: `MERGE-UNWIND-ACCEPTANCE-R20-2026-10-23`. Lane: `merge`.

## Mission

This is a bounded continuation of the previous task under a newly authorized window.

Runtime: Codex. This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the runtime profile [`RUNTIME-CODEX.md`](agent-workflow/RUNTIME-CODEX.md), the compact root [AGENTS.md](../../AGENTS.md), and the persistent repo guidance. Review executor and Build waiting follow that profile only.
The owner may proceed within this task and its bounds. Initial T0 NOT_SET: fix T0 once at actual work start, including preparation. Prepare fresh-session inputs with `/usr/local/bin/smallsort-session`, obtain required independent review and register the exact phase through the assigned branch client before proof work. Registration does not restart the clock.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-merge-origin` on branch `merge/incoming-origin-20261009`; baseline `e278869253e5a1e553d0ac0c1bc7adb5221b681e`; source `6fd50c699500cbac5c65912174d4aa49b49db19f`.
Tool worktree `/root/verifast-merge-actual-glue` on `merge/actual-glue-instance-20261011` at `39f6b0cacd00575c8ca2d39e9f15632723bf1227`.
Profile `research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json` SHA-256 `1404842fc70c2fbc4d422d63ff3035edeacd22ac64cdf02382b2300e94fd57bb`. New ledger path: `research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R20-BUDGET-20261023.json`; previous closed ledger: `research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R19-BUDGET-20261022.json`.
Cloud budget: 3600 seconds. Wall window: 120 minutes main + 30 minutes closeout. Per-Build timeout ≤1200 seconds; report reserve ≥420 seconds. T0 remains NOT_SET until actual work starts.

## Goal and steps

R20 и Builds разрешены. Принять prepared R19 cleanup на actual raw caller: normal/unwind + controls. Затем исходный caller с as_mut_ptr/unsize, borrow/lifetime и CURRENT matrix. Tool 39f6b0ca уже опубликован, Cloud UNVERIFIED.

1. Prepare/register fresh R20, adapting client/recipe admission to the new ledger/window; no old-phase dispatch. Reuse published 3a587cb7/39f6b0ca and R19 review; review changed admission/recipe deltas. Existing Cloud preflight, then raw caller normal/unwind plus all five R19 controls at their intended sites. A static shape refusal is separate from a verifier resource negative; close the F5 unwind-copy coverage gap if needed before acceptance.
2. After the raw caller gate, return to the original as_mut_ptr/unsize caller: source-bound metadata, actual borrow/reference lifecycle and checked resource conversion in the same admitted domain. Keep RawPtr LocalAddressTaken and index-projection controls; an unsupported/setup failure is INCONCLUSIVE, not an intended negative.
3. Then CURRENT/backedge and false/true/panic/Drop/Resume on compatible pins; final required matrix after the target. Use remaining main time for implementation, service tests, review and an exact HANDOFF candidate if another full Cloud cycle does not fit.

## Special bounds

- Keep timeout1200/execute<=780/soft<=765/report reserve>=420 and nested compile reserve140. Respect the existing transport cap; recipe pruning needs a closure inventory and review, no cap increase. Fix T0 once at actual start; closed R19 carries 0.
- Preserve the pinned R8 concrete allocation/domain, array11/R9 gates and full posts. RawPtr needs same mutability/pointee/place/full origin; no RawPtr<->Ref or address-only ownership, broad placeholders, new borrow/trusted premises. Adopted v4 coordination.py is read-only.
- Raw caller, original caller and isolated body are separate claims; bounded PASS is not B2/generic/R5/sorting/profile qualification. Missing bindings stay INCONCLUSIVE. Continue useful work in main; an early stop lists each independent task checked and its real boundary (CORE).

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: Published R19 cleanup candidate remains Cloud-UNVERIFIED; original caller borrow/unsize and full normal/unwind remain OPEN.
Next: At actual T0 prepare/register R20; Cloud preflight, then the published raw caller normal/unwind and five R19 controls.

## References

- [R19 checked cleanup design](cloud-build/origin-layout/R19-UNWIND-CLEANUP-DESIGN-20261022.md)
- [R19 independent review and remaining nits](cloud-build/origin-layout/R19-REVIEW-20261022.md)
- [Original caller borrow boundary](cloud-build/origin-layout/R16-CALLER-DESIGN-20261021.md)
- [R18 RawPtr controls](cloud-build/origin-layout/R18-PROOF2-RESULT-20261022.json)
- [R19 accounting closeout](cloud-build/origin-layout/R19-CLOSEOUT-20261022.json)

## Отчёт агента

**merge-unwind-acceptance-autonomous-2026-10-23-r20 · merge · MERGE-UNWIND-ACCEPTANCE-R20-2026-10-23 · ACTIVE**
Updated: 2026-10-22T20:47:17Z. Baseline source/tool/profile: `6fd50c699500cbac5c65912174d4aa49b49db19f` / `39f6b0cacd00575c8ca2d39e9f15632723bf1227` / `1404842fc70c2fbc4d422d63ff3035edeacd22ac64cdf02382b2300e94fd57bb`.
Dates: T0 `2026-10-22T20:08:00Z`; main `2026-10-22T22:08:00Z`; absolute `2026-10-22T22:38:00Z`. Budget 3600s: 938s spent, 0s retired, 2662s remaining including reservations.
Active Build IDs: none recorded; unresolved: none recorded.
Blocker: Raw caller exit0 and5R19 controls matched; F5 resource negative/original caller OPEN.
Next: Review/run F5 and state controls; preserve pins; then original caller metadata/lifetime.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
