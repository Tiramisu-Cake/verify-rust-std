# Networks: independent Challenge 8 checkpoint

2026-10-07 — IN PROGRESS, separately authorized by the owner.

Branch `challenge-8/networks`, worktree `/root/verify-rust-std-networks`.
Frozen entry `origin/challenge-8/research`:
`bea62488b44f8c557e45e04cb4eb259b0173422f`.
This phase is independent of sort4/select/VeriFast development and its stops.
Do not merge automatically or overwrite the main direction's STATUS/PLAN.

Own budget: **769/1800 summed hosted job seconds**, preparation included;
**1031 remain**. No active run. Latest N9c run
[37638843477](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37638843477),
source `910c183c678785224074d24dbee03ca8397bee44`. Previous N9b run
[37637872959](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37637872959),
source `70eaa2d9499a47d45d2c9af74de4ef643f74ed0c`.
Previous N9 run
[37636248489](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37636248489),
source `d433216f635c58d84ed9b9cde7bcab95c2c38549`.
At most one hosted networks experiment, with at most two total
across the two branches. Server: reading/editing/orchestration only.

Current work: specify actual swap_if_less; establish source-linked abstract
network composition for 9, then 13 wires on official stock VeriFast 26.09.
Rust helper safety/ownership/callback/unwind proof remains OPEN.
Conditional network composition is not a completed public Challenge 8 target.

Binary N9 PASS (83 statements, full symbolic Boolean domain, 496 return/leak
paths). N9b arbitrary-decision identity permutation PASS216 statements, with
checked local helper and whole25-step sequence. Both intended negatives and
14 classifier rejection controls PASS. N9b threshold helper body PASS but
whole general-rank theorem TIMEOUT180s at first adjacency: final-expression
threshold creates expensive SMT unfolding. No general-order theorem yet.
Original N9 timeouts/classifier INCONCLUSIVEs remain preserved.

N9c same binary/permutation/negative controls PASS, threshold composition still
TIMEOUT180s: first adjacency completes45 paths, no whole theorem. Remaining
branching in inline Boolean assignments duplicates expensive rank context.
Next permitted action: verified binary model summary plus pure Boolean
fixpoint composition, NEW N9d run; only after acceptance advance to N13.
Generated binary/identity files are universal ghost assertion harnesses:
their final assertions carry the theorem; `ensures true` is not a reusable
callee summary. No Rust summary is claimed.
See [plan](PLAN.md), [journal](EXPERIMENT-LOG.md),
[source correspondence](SOURCE-MAP.md) and [helper contract](SWAP-CONTRACT.md).
