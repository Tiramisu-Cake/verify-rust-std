# Select-R19 — c3 callback recovery and actual sort4

Task ID: `select-c3-callback-autonomous-2026-10-22-r19`; previous task: `select-s5-unselected-borrow-autonomous-2026-10-22-r18`.
Owner: **Select/sort4**. Phase: `SORT4-ACTUAL-C3-2026-10-22-R19`. Lane: `o26-sort4-c1-current-recovery`.

## Mission

This is a bounded continuation of the previous task under a newly authorized window.

Runtime: Claude Code. This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the runtime profile [`RUNTIME-CLAUDE.md`](agent-workflow/RUNTIME-CLAUDE.md), the compact root [CLAUDE.md](../../CLAUDE.md), and the persistent repo guidance. Review executor and Build waiting follow that profile only.
The owner may proceed within this task and its bounds. Initial T0 NOT_SET: fix T0 once at actual work start, including preparation. Prepare fresh-session inputs with `/usr/local/bin/smallsort-session`, obtain required independent review and register the exact phase through the assigned branch client before proof work. Registration does not restart the clock.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-select-night` on branch `research/night-select-sort4-cloud-2026-10-09`; baseline `69a54645a7f63cdd26b931b69956b99f09b4efd3`; source `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db`.
Tool worktree `/root/verifast-select-sort4-c2-bind-20261010` on `challenge8/select-sort4-c2-bound-20261010` at `f76012fb518703b1d98e243ac4f487f16877cfcb`.
Profile `research/challenge-8/cloud-build/sort4-caller-entry-native/A1-ACTUAL-C2-R17-PROFILE-2026-10-21.json` SHA-256 `87a0bfe586b40a33bdf840164aec8748872c8fdd11b3faad421d3860d1f2a091`. New ledger path: `research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-C3-2026-10-22-R19.json`; previous closed ledger: `research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-C2-2026-10-22-R18.json`.
Cloud budget: 3600 seconds. Wall window: 120 minutes main + 30 minutes closeout. Per-Build timeout ≤1200 seconds; report reserve ≥240 seconds. T0 remains NOT_SET until actual work starts.

## Goal and steps

R19 и Builds разрешены. Автономно продвигай actual sort4 normal/unwind по CORE; ближайшая цель — c3 по C3-NEXT-DESIGN: обобщённый на N вызовов overlay, c3 setup с share всех четырёх borrow, recovery без leak, controls и точная call-site attribution. Дальше c4–c5 и composition по миссии в оставшемся окне.

1. Implement C3-NEXT-DESIGN: explicit N-call indexed overlay (unknown index/count/shape still refused), c3 constructor and per-index controls incl. index-N+1 marker without call; new profile/pins; smallsort-reviewer review; register R19 through the branch client.
2. Cloud c3 on exact reviewed pins; read each control by message and location in Brief; then c4–c5 and selector/copy composition when justified. Required controls/mini7/fresh26 and stable Freeze caller only on final pins; no full-body credit for partial progress.
3. Maintenance, reported separately from proof: make test_a1_r11..r18_registration clock-independent (inject a fixed now instead of wall clock) so expired windows do not fail them; keep every client gate and refusal; run them as service tests.

## Special bounds

- Effective tool is the full R16/R17 overlay/spec/profile chain plus reviewed R19 deltas, not base SHA alone. Preserve R13 limits and strict entry/exit/escape/init/leak/unwind checks; keep all5 calls/8selects/4copies. No leak statement or relaxed leak check.
- Tool WT contains foreign edits: use pinned Git objects; develop in project/isolated WT. Selected operands are symbolic offsets: use checked equality or an explicit checked case split, never an address-only or assumed bridge.
- Use the whole main window: if a full Cloud cycle no longer fits, finish Cloud-free stages (implementation, tests, review, pins, committed HANDOFF candidate) instead of closing early (CORE).

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: c3 has no callback setup: No matching heap chunks ref_precreated_token<T>(ptr_add_(v_base,2+1)); translator overlay supports indices 1/2 only. (aliasing.rsspec(88,9-29) via verified/lib.rs(299,26-29) c3 call) [Build 0ee7f658-50fe-4928-a7c9-3da5e56c95f2]
Next: Implement C3-NEXT-DESIGN (N-index overlay, c3 constructor sharing all four borrows, per-index controls, new profile); review; register R19; Cloud c3.

## References

- [c3 design](task-history/select-s5-r18/C3-NEXT-DESIGN.md)
- [S5 Cloud evidence](task-history/select-s5-r18/S5-evidence.json)
- [R18 registration note (R17 routing literal)](task-history/select-s5-r18/REGISTRATION.md)

## Отчёт агента

**select-c3-callback-autonomous-2026-10-22-r19 · select-sort4 · SORT4-ACTUAL-C3-2026-10-22-R19 · ACTIVE**
Updated: 2026-10-22T14:43:00Z. Baseline source/tool/profile: `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db` / `f76012fb518703b1d98e243ac4f487f16877cfcb` / `87a0bfe586b40a33bdf840164aec8748872c8fdd11b3faad421d3860d1f2a091`.
Dates: T0 `2026-10-22T13:50:26Z`; main `2026-10-22T15:50:26Z`; absolute `2026-10-22T16:20:26Z`. Budget 3600s: 652s spent, 0s retired, 2948s remaining including reservations.
Active Build IDs: none recorded; unresolved: none recorded.
Blocker: c4 has no callback setup: No matching heap chunks ref_precreated_token<T>(ptr_add_(v_base,2+0)); overlay count limited to 3. [Build `2b55f6a5-076a-4fd6-92e9-c42aae9ba500`]
Next: S2: count-4 overlay + c4 layer (operands d,b) + c4 controls; delta review; Cloud c4.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
