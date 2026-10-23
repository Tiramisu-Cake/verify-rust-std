# R23 exact phase admission

Defect: the closed R22 client cannot authorize this fresh R23 task, and the
prepared-session generator refuses historical numeric zero credit fields in
the exact pinned profile. Preserve those profile bytes; use the existing
branch client's exact phase admission, without changing the shared generator.

Applicability: owner merge, phase MERGE-CALLER-ACCEPTANCE-R23-2026-10-24,
closed baseline733b6a7d, profile3fec93b5 diagnostic-only toolfc0208d4.
Tool worktree HEAD0f4e336b additionally contains prepared typed-NLL changes;
they are not selected by this profile. No proof credit or mapping established.

Invariants: historical ledgers/profile/mode/publication gate remain byte-exact;
coordinator v4 untouched; fresh14400 seconds, no carry, stable owner; full1200
second timeout plus60 queue, execute<=780, soft<=765, reserve>=420, nested
compile reserve140. T0 2026-10-23T10:45:00Z conservatively includes preparation;
main 2026-10-26T10:45:00Z, absolute 2026-10-26T11:45:00Z for tooling only.
No runtime/std/CFG/domain/resources/normal-unwind/control semantics change.

Registration binds exact profile, cumulative patch, provider module, provider
source tables, committed regular-file closure and worktree bytes. Provider
pin changes reflect only the three required runner fixes; old R22 authorization
and historical ledger remain unchanged. Every submit remeasures transport and
performs the unchanged R14 upload/publisher and execute budget gates.

Controls: fresh/old/malformed/wrong owner/phase/path/budget/deadlines/profile/
provider/source/recipe rejection; boundary checks before and after source
validation; upload guard and final reservation route; source-pin/runner service
tests. Actual preparation/compiler/proof runs only in Cloud after review.

Generator refusal: reused profile carries acceptance/admission/credit flags:
/r10_registration/independent_credit, /r11_placement/independent_credit.
Changing pinned profile or silently upgrading shared tooling was rejected.
