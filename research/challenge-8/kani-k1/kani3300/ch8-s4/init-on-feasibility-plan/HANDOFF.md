# w14 — PLAN ONLY handoff

Planning stage complete. **Conditional feasibility; exact partial-init theorem BLOCKED on the current pin.** No new proof result or provider was admitted.

Read [PLAN.md](PLAN.md), [HELPERS.md](HELPERS.md) and [CONTROLS.md](CONTROLS.md). Exact pins, unchanged cap snapshots and immutable dependencies are in [INPUTS.json](INPUTS.json); hashed source ranges in [SOURCE-CITATIONS.json](SOURCE-CITATIONS.json); static checks in [VALIDATION.json](VALIDATION.json). [MANIFEST.json](MANIFEST.json) seals the files other than itself.

* Tool is `0aac16ef62da9e9d5645782d458593e5d78143ba`; std is `8faf8e62af8f82b5c46af020086f8df591b6757e`. G0 starts at admitted network-r2 `8896f60ae9e0ea1c706c6b8693d00e2500190676`. Repository default Kani pin differs and was not substituted.
* ON support exists by source trace, including a u8 state oracle that does not load payload. Mandatory unsupported MU/union/pointer routes remain blockers. Copy rebasing can subtract decreasing unsigned offsets; the other branch blesses one element even for count0/count>1. Fixes require a new reviewed candidate and exact lowering checks.
* Minimal positive writes/reads cell0 while leaving cell1 unwritten. Minimal negative intentionally reads cell1 and must fail its **native uninit-read property**. Oracle sensitivity, zero/bulk/downward/overlap copy and raw-address controls are specified separately; no ghost assumption substitutes for checking.
* Every scoped helper has initialized/read/write/post-init obligations; actual partial merge L/R masks are retained. Full negative-space mask equality needs checked store/state coupling. Positive Init assertions alone do not prove untouched holes.
* Separate proposed ON profile only; existing OFF flags/parser/lane, numeric caps, historical records and ledgers are unchanged. Bounded leaves do not become provider summaries. Generic/ownership/panic/Drop/full-matrix/independent AST-MIR/B1-B2 credit stays OPEN/NONE.

Validation was Git/blob/range hashing, cap-data parsing, concrete set arithmetic and documentation scope checks only. Compiler, cargo, rustc, Kani, CBMC, native verification, CI and push were NOT_RUN. No raw logs/archives were read. No source/tool/control/flags/caps/ledger changes. No subagents. Commit uses `[skip ci]` and author/committer `Tiramisu-Cake <igkharin@gmail.com>`; delivery SHA is the containing commit reported to the coordinator.

The shared branch advanced through concurrent research commits while planning (validation snapshot `c0de8471801ac22b38e3290c7a6b75742135af6b`). Their committed files and unrelated untracked paths were preserved. This delivery adds only this output directory; input identities remain frozen at the starting admission and exact source/tool pins.

Next step, only under a new assignment: review these blockers and prepare a versioned implementation package preserving OFF and caps, then independent semantic review and separate coordinator execution authorization. Stop here as requested; no budget/reservation/phase or GO is created by this handoff.
