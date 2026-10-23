# Merge-R23 — NEEDS_FIX, early Build, owned-NLL stop-loss, source-level borrow route

Task ID: `merge-caller-acceptance-autonomous-2026-10-24-r23`; previous task: `merge-caller-acceptance-autonomous-2026-10-23-r22`.
Owner: **Merge**. Phase: `MERGE-CALLER-ACCEPTANCE-R23-2026-10-24`. Lane: `merge`.

## Mission

This is a bounded continuation of the previous task under a newly authorized window.

Runtime: Codex. This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the runtime profile [`RUNTIME-CODEX.md`](agent-workflow/RUNTIME-CODEX.md), the compact root [AGENTS.md](../../AGENTS.md), and the persistent repo guidance. Review executor and Build waiting follow that profile only.
The owner may proceed within this task and its bounds. Initial T0 NOT_SET: fix T0 once at actual work start, including preparation. Prepare fresh-session inputs with `/usr/local/bin/smallsort-session`, obtain required independent review and register the exact phase through the assigned branch client before proof work. Registration does not restart the clock.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-merge-origin` on branch `merge/incoming-origin-20261009`; baseline `733b6a7d68259787f1caf58177060589b6af779e`; source `6fd50c699500cbac5c65912174d4aa49b49db19f`.
Tool worktree `/root/verifast-merge-actual-glue` on `merge/r22-owned-nll-borrow-sites-20261023` at `0f4e336b52441e8f341a567250adba2b200c54d1`.
Profile `research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json` SHA-256 `3fec93b5237d534b69eb3be59d11ea4abde3588f07c6e9437b1c09bf8533ac88`. New ledger path: `research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R23-BUDGET-20261024.json`; previous closed ledger: `research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R22-BUDGET-20261023.json`.
Cloud budget: 14400 seconds. Wall window: 4320 minutes main + 60 minutes closeout (explicit window authorized by this task only; CORE main/closeout rules apply to these deadlines). Per-Build timeout ≤1200 seconds; report reserve ≥420 seconds. T0 remains NOT_SET until actual work starts.

## Goal and steps

R23 and Builds authorized. One-time extended window: close on goal, budget or a real boundary, not on time (R23-OWNER-DIRECTIONS). Goal: the plan's first end-to-end branch, the actual insert_tail caller (W3) with a real borrow lifecycle and W2 normal/unwind restoration. Stop-loss: two Cloud cycles on owned-NLL, then a source-level adapter.

1. Without Cloud: fix the three NEEDS_FIX findings (compile-profile translator pin; strip inherited VF_EXPORT_OWNED_NLL_FACTS from every copied campaign/placement env; distinct NLL eligibility flag for exact registered positive cases only) with service error-path tests; one delta review. Register R23 with HEAD profile 3fec93b5; re-measure transport; early full-envelope Build.
2. Stop-loss: at most two full Cloud cycles on owned-NLL capture; success = owned facts bound to the actual MIR body/location with an ESTABLISHED cross-stage mapping. Otherwise record the exact gap and switch to the source-level route of R20-CALLER-AND-CONTROL-FRONTIER (exact coercion/types/lifetime, checked array conversions, borrow/borrow_end encapsulation); no new trusted premise.
3. Then raw caller intended controls (F5 real resource negative, state context, index projection) and the CURRENT/backedge, false/true/panic/Drop/Resume matrix on compatible pins. Record self-chosen obligations in CHECKPOINT.

## Special bounds

- Window deadlines exist only for ledger/watcher. Envelope timeout1200/execute<=780/soft<=765/reserve>=420, nested compile reserve140, never shortened; compile error or no-proof-stage run fixed statically, same config never repeated. Review once per semantic candidate; progress note about every 2 h.
- RawPtr: same mutability/pointee/place/full origin; no RawPtr<->Ref, address-only ownership, broad placeholders or new trusted premises. Keep the R8 boundary, posts and controls. coordination.py v4 read-only. Raw, original and isolated-body claims stay separate; no B2 credit.
- Maintain cloud-build/origin-layout/TOOL-CHAIN.md (fork branches, heads, scope, gating, status) for the VeriFast maintainer; the maintainer takes no proof work and changes no pins. Fixes for a finished Codex worker go through a follow-up task.

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: Admission NEEDS_FIX (3 findings); no Build until fixed, reviewed, transport re-measured.
Next: Fix the three findings, delta review, register R23, early full-1200 Build; then owned-NLL stop-loss and the source-level route.

## References

- [Owner directions R23](cloud-build/origin-layout/R23-OWNER-DIRECTIONS-20261024.md)
- [R22 owned-NLL adoption review (NEEDS_FIX)](cloud-build/origin-layout/R22-OWNED-NLL-ADOPTION-REVIEW-20261023.json)
- [R20 caller and control frontier](cloud-build/origin-layout/R20-CALLER-AND-CONTROL-FRONTIER-20261023.md)

## Отчёт агента

**merge-caller-acceptance-autonomous-2026-10-24-r23 · merge · MERGE-CALLER-ACCEPTANCE-R23-2026-10-24 · ACTIVE**
Updated: 2026-10-23T19:29:09.007343Z. Baseline source/tool/profile: `6fd50c699500cbac5c65912174d4aa49b49db19f` / `0f4e336b52441e8f341a567250adba2b200c54d1` / `3fec93b5237d534b69eb3be59d11ea4abde3588f07c6e9437b1c09bf8533ac88`.
Dates: T0 `2026-10-23T10:45:00Z`; main `2026-10-26T10:45:00Z`; absolute `2026-10-26T11:45:00Z`; window 4320 min main + 60 min closeout (explicit). Budget 14400s: 8429s spent, 0s retired, 5971s remaining including reservations.
Active Build IDs: none recorded; unresolved: none recorded.
Blocker: P14 terminal FAILURE; Evidence Brief diagnosis pending.
Next: Read P14 Evidence Brief after accounting publication.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
