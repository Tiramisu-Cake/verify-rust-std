# Select-R24 — clean positive callee (103a34), full matrix, P2 *mut to PUBLISHED, then W4

Task ID: `select-callee-acceptance-autonomous-2026-10-24-r24`; previous task: `select-callee-acceptance-autonomous-2026-10-23-r23`.
Owner: **Select/sort4**. Phase: `SORT4-ACTUAL-SELECT-2026-10-24-R24`. Lane: `o26-select-callee-r20`.

## Mission

This is a bounded continuation of the previous task under a newly authorized window.

Runtime: Codex. This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the runtime profile [`RUNTIME-CODEX.md`](agent-workflow/RUNTIME-CODEX.md), the compact root [AGENTS.md](../../AGENTS.md), and the persistent repo guidance. Review executor and Build waiting follow that profile only.
The owner may proceed within this task and its bounds. Initial T0 NOT_SET: fix T0 once at actual work start, including preparation. Prepare fresh-session inputs with `/usr/local/bin/smallsort-session`, obtain required independent review and register the exact phase through the assigned branch client before proof work. Registration does not restart the clock.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-select-night` on branch `research/night-select-sort4-cloud-2026-10-09`; baseline `505aea0d8d48814d41918ecfc7d6f307a06d4727`; source `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db`.
Tool worktree `/root/verifast-select-sort4-c2-bind-20261010` on `challenge8/select-sort4-c2-bound-20261010` at `f76012fb518703b1d98e243ac4f487f16877cfcb`.
Profile `research/challenge-8/cloud-build/sort4-caller-entry-native/A1-ACTUAL-C3-R19-PROFILE-2026-10-22.json` SHA-256 `d4b1b7350d9a9966bedfd0ef50e4c7f7b4cc071ca1f6c4e08d44ba85c36ed622`. New ledger path: `research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-SELECT-2026-10-24-R24.json`; previous closed ledger: `research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-SELECT-2026-10-23-R23.json`.
Cloud budget: 21600 seconds. Wall window: 4320 minutes main + 60 minutes closeout (explicit window authorized by this task only; CORE main/closeout rules apply to these deadlines). Per-Build timeout ≤1200 seconds; report reserve ≥240 seconds. T0 remains NOT_SET until actual work starts.

## Goal and steps

R24 and Builds authorized. One-time extended window: close on goal, budget or a real boundary, not on time (OWNER-DIRECTIONS). Select is the critical path. Goal: clean positive of the checked actual callee select_unpredictable (W1) with the full matrix; then P2 (*mut T) to PUBLISHED; then W4 body C5.

1. Register R24. First Build: reviewed UNBUILT candidate a4737f9f (translator 103a34…) on fingerprint rows 739f982d, full 1200; no new fingerprint. If dead-code persists: bind exact diagnostic sites statically, next falsifiable hypothesis; never an exemption/suppression. Classifier and omit-* pins only after a clean positive.
2. On a clean positive: pin the seven control targets; normal/unwind/nested-Drop, ownership, leak/refinement, same-site omission controls; acceptance only on the full matrix. Then the mutable route: fresh exact *mut source/fingerprint, mutable certificates under closed opt-in, mutable positive plus refusal controls, review GO, P2-INTERFACE status PUBLISHED.
3. Then W4: dormant body route (BODY-C5-NEXT 168/191) after acceptance/linkage and count-five requalification. Record each self-chosen obligation and reason in CHECKPOINT mission_queue.

## Special bounds

- Window deadlines exist only for ledger/watcher. Timeout 1200 never shortened; compile error or no-proof-stage run fixed statically, same config never repeated. Review once per semantic candidate (CORE 2026-10-23); progress note about every 2 h.
- Keep the R16–R23 chain and strict R13 checks. Gate exemption, guard-own=true, broad forget summary or dead-code checker change are owner-reserved: opt-in experimental candidate without credit plus an open question. No address-only bridge. coordination.py v4 read-only.
- Publish the overlay chain (patch paths, SHA-256, translator hashes, gating) in task-history/select-callee-r24/TOOL-OVERLAYS.md for the VeriFast maintainer; the maintainer takes no proof work and changes no pins.

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: S3 positive fails dead-code check after outer return/leak-check; cause unresolved. [Build cf8405cc-d421-4e7a-a9cb-3fcb8b74b1c9]
Next: Register R24; Build reviewed unbuilt 103a34 (a4737f9f) on rows 739f982d at full 1200; on clean positive run the matrix, then mutable P2 to PUBLISHED.

## References

- [Owner directions R24](task-history/select-callee-r24/OWNER-DIRECTIONS.md)
- [R23 next-window handoff](task-history/select-callee-r23/NEXT-WINDOW-HANDOFF.md)
- [Ghost-CFG candidate pins](task-history/select-callee-r23/GHOST-CFG-PROOF-PINS.json)

## Отчёт агента

**select-callee-acceptance-autonomous-2026-10-24-r24 · select-sort4 · SORT4-ACTUAL-SELECT-2026-10-24-R24 · ACTIVE**
Updated: 2026-10-23T21:47:54Z. Baseline source/tool/profile: `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db` / `f76012fb518703b1d98e243ac4f487f16877cfcb` / `d4b1b7350d9a9966bedfd0ef50e4c7f7b4cc071ca1f6c4e08d44ba85c36ed622`.
Dates: T0 `2026-10-23T10:48:18Z`; main `2026-10-26T10:48:18Z`; absolute `2026-10-26T11:48:18Z`; window 4320 min main + 60 min closeout (explicit). Budget 21600s: 6830s spent, 0s retired, 14770s remaining including reservations.
Active Build IDs: none recorded; unresolved: none recorded.
Blocker: Reviewed partial-selector expectation fix unbuilt; P2 NOT_PUBLISHED.
Next: Submit9ffbd full1200; qualify all11controls/rootaudit, then P2 andconcreteW4.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
