# W0-A1 R2 — issue controls, upstream 0aac vs SEL1 (run 43772128176)

2026-11-16 ~02:05 UTC, coordinator (owner asleep). Fork run [43772128176](https://github.com/Tiramisu-Cake/kani/actions/runs/43772128176),
trigger `71b4a05915` (child of package `bf81a1f14f`). Jobs r2(baseline) and r2(sel1) both "failure" by design of exit codes;
per-case verdicts below are from each case's stdout/stderr (receipt `outcome` UNKNOWN, reviewed here).

| Case | Baseline upstream `0aac16ef62` | SEL1 `14bc57fdb9` | Reading |
|---|---|---|---|
| #5020 nonnull-negative (uninit field behind NonNull at nonzero offset) | **VERIFICATION SUCCESSFUL, 0 of 66** — false negative reproduced | **FAILED, 2 of 84**: "Reading from an uninitialized pointer of type `*const S`" and "`S`" | **fixed by C2** (slice 3 nested-Pat offset) |
| #5020 initialized companion | SUCCESSFUL 0/39 | SUCCESSFUL 0/54 | legal companion stays green |
| #4854 explicit-proof companion | **ICE** `relevant_instruction.rs:136:73` (unreachable) | **SUCCESSFUL 0 of 156** | **fixed by C2** for explicit harnesses |
| #4854 original autoharness repro | **ICE** same panic | **compiler error: "immutable masks: reset is absent from this model"** | ICE gone, but C2 rejects the autoharness model — **NEW FINDING, needs analysis before PR-02 publication** |
| #5151 empty-drop negative / initialized-slot companion | fixture compile error `E0433: cannot find core in the crate root` | same | **fixture defect** (edition: `use core::...` without 2021 edition); no verdict |

Follow-ups: (1) analyse the "reset is absent from this model" path (PR-02 immutable registry vs autoharness model) — static, planner;
(2) A1 reserve dispatch R3 may fix the #5151 fixture edition and re-run both pins (decide after R1). Ledger: item 1 used 2/18.
