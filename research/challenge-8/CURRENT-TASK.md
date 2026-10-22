# Select-R18 — S5 c2 borrow recovery and actual sort4

Task ID: `select-s5-unselected-borrow-autonomous-2026-10-22-r18`; previous task: `select-actual-c2-autonomous-2026-10-21-r17`.
Owner: **Select/sort4**. Phase: `SORT4-ACTUAL-C2-2026-10-22-R18`. Lane: `o26-sort4-c1-current-recovery`.

## Mission

This is a bounded continuation of the previous task under a newly authorized window.

Runtime: Claude Code. This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the runtime profile [`RUNTIME-CLAUDE.md`](agent-workflow/RUNTIME-CLAUDE.md), the compact root [CLAUDE.md](../../CLAUDE.md), and the persistent repo guidance. Review executor and Build waiting follow that profile only.
The owner may proceed within this task and its bounds. Initial T0 NOT_SET: fix T0 once at actual work start, including preparation. Prepare fresh-session inputs with `/usr/local/bin/smallsort-session`, obtain required independent review and register the exact phase through the assigned branch client before proof work. Registration does not restart the clock.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-select-night` on branch `research/night-select-sort4-cloud-2026-10-09`; baseline `68e4537989f688a8b29e99a301257a523928b0af`; source `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db`.
Tool worktree `/root/verifast-select-sort4-c2-bind-20261010` on `challenge8/select-sort4-c2-bound-20261010` at `f76012fb518703b1d98e243ac4f487f16877cfcb`.
Profile `research/challenge-8/cloud-build/sort4-caller-entry-native/A1-ACTUAL-C2-R17-PROFILE-2026-10-21.json` SHA-256 `87a0bfe586b40a33bdf840164aec8748872c8fdd11b3faad421d3860d1f2a091`. New ledger path: `research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-C2-2026-10-22-R18.json`; previous closed ledger: `research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-C2-2026-10-21-R17.json`.
Cloud budget: 3600 seconds. Wall window: 120 minutes main + 30 minutes closeout. Per-Build timeout ≤1200 seconds; report reserve ≥240 seconds. T0 remains NOT_SET until actual work starts.

## Goal and steps

R18 и Builds разрешены. Автономно продвигай actual sort4 normal/unwind по CORE; ближайшая цель — S5 (a6550c20): checked consumption невыбранных c2 full_borrow и c2 resource recovery без leak, с controls и точной call-site attribution. Дальше продолжай по миссии в оставшемся окне.

1. Independent review of S5 a6550c20 against S5-review-spec.json by the smallsort-reviewer subagent (review packet + expected candidate/spec identities); fix concrete findings, then register R18 phase/ledger through the branch client.
2. Cloud S5 on exact reviewed pins with the missing-unselected-share negative and retained wrong order/ref/index/debt/marker controls; wait via smallsort-session wait; read results via Brief and establish whether c2 recovery passes the leak check.
3. When justified, advance c3–c5 and selector/copy composition; after target gates pass run required controls/mini7/fresh26 on final pins, then stable Freeze caller. Report partial progress without full-body credit.

## Special bounds

- Effective tool is the full R16/R17 overlay/spec/profile chain, not base SHA alone. Preserve R13 limits and strict entry/exit/escape/init/leak/unwind checks; keep all5 calls/8selects/4copies. No leak statement or relaxed leak check.
- Tool WT contains foreign edits: use pinned Git objects; develop in project/isolated WT. Kernel resource equality may prove binding; independent receipt still attributes exact ordered calls. No address-only or assumed bridge.
- First Claude Code proof session: record reviewer identity/decision, wait job/event IDs and any runtime friction in task-history; report it separately from proof progress.

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: Function leaks heap chunks: unselected c2 full_borrow(cmp2_k, full_borrow_content(T,t)) at v_base+1 and v_base; full actual normal/unwind OPEN. (verified/lib.rs(314,1-2), actual body leak check) [Build 27e8bfac-eb5f-4cf4-ae89-18bacd16eb90]
Next: Review S5 a6550c20 with smallsort-reviewer, register R18, then Cloud S5 with missing-unselected-share control; Brief on the c2 leak check.

## References

- [S5 defect and fix rationale](task-history/select-actual-c2-r17/S5-UNSELECTED-BORROW-FIX.md)
- [S5 review spec](task-history/select-actual-c2-r17/S5-review-spec.json)
- [Callback protocol and kernel binding qualification](task-history/select-actual-lifetime-r16/NEXT-CALLBACK-PROTOCOL.md)

## Отчёт агента

**select-s5-unselected-borrow-autonomous-2026-10-22-r18 · select-sort4 · SORT4-ACTUAL-C2-2026-10-22-R18 · HANDOFF**
Updated: 2026-10-22T12:50:00Z. Baseline source/tool/profile: `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db` / `f76012fb518703b1d98e243ac4f487f16877cfcb` / `87a0bfe586b40a33bdf840164aec8748872c8fdd11b3faad421d3860d1f2a091`.
Dates: T0 `2026-10-22T12:12:06Z`; main `2026-10-22T14:12:06Z`; absolute `2026-10-22T14:42:06Z`. Budget 3600s: 0s spent, 0s retired, 3600s remaining including reservations.
Active Build IDs: 0ee7f658-50fe-4928-a7c9-3da5e56c95f2; unresolved: none recorded.
Blocker: Function leaks heap chunks: unselected c2 full_borrow(cmp2_k, full_borrow_content(T,t)) at v_base+1 and v_base; full actual normal/unwind OPEN. [Build `27e8bfac-eb5f-4cf4-ae89-18bacd16eb90`]
Next: WAITING S5 Build 0ee7f658 via wait; ack, then Brief: c2 leak check and controls by message/location.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
