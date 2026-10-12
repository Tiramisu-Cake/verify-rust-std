# Executed and NOT_RUN matrix

| Gate | Actual result on own new tool | Evidence / reason |
|---|---|---|
| C0 input/source/settings closure | PARTIAL: input/source/tree/compiler pins checked; runtime settings/source controls NOT_RUN | Both Cloud archives contain input-closure and assembled-tree; no completed console exists |
| C1 changed components | FAILED, partial exporter built on c232 | First run exporter exit101; corrected second run exporter exit0, console exit2 while generating decoder; official refiner NOT_RUN |
| C2 lifecycle/layout positive and controls | NOT_RUN | Setup/component failure, not intended assertion or admission refusal |
| C3 combined actual glue | DEFERRED_BY_USER | Next stage; F1 preserved, no new qualification |
| C4 selector/C4 composition | NOT_RUN | Shared translator/kernel/AST changed; C0–C2 prerequisite not closed |
| C5 strict freeze/retained MD/pointer rights | NOT_RUN | Shared freeze/storage/tracked-MD changed; C0–C2 prerequisite not closed |
| C6 native/ZST/default isolation | NOT_RUN | Shared context/schema changed; C0–C2 prerequisite not closed |
| C7 as_mut_ptr | NOT_RUN | Shared translator/schema changed; C0–C2 prerequisite not closed |

All eleven C2 source pairs and layout/compiler/source/type/binding mutations are
NOT_RUN: prefix-positive, overlap, missing-source-right, readonly destination
safety-proof refusal, source marker call, changed source digest, strict-survivor,
reconstructed-origin, consumed-origin, fresh local incarnation and retired reuse.
Their intended gates remain in C2-GATE-MATRIX.md. None receives credit from a setup
failure. No proof body ENTRY/TARGET, intended first diagnostic, lifecycle retirement,
strict reconstruction, normal/unwind posts, leak checks or actual callee verification
was reached. New-tool unsupported-case rejection is likewise unobserved.

Diff selects the affected C4–C7 rows in FUTURE-GATES.md; unchanged math/network,
ordering/permutation/stability, older Kani and unrelated entrypoints are excluded.
No historical green count is replay evidence for this new candidate. No new
experiments after08:56:41UTC. Both budgets/reservations are accounted:277+305=582
Cloud seconds. Unspent3018 are retired, no carry-forward/automatic continuation.

Run1 d02ccd21-5328-4880-87a8-ab2ffd7e04ef at project1c1be000/tool059687:
compiler API errors at exporter-build. Its original evidence_complete=false due
to missing audit is preserved. Run2 70085ccc-e0b7-4099-98bb-7d206f2fc635 at
projectfc11cdfc/toolc232: evidence_complete=true but diagnostic_complete=false,
runexit2, accepted=false, component/setup failure. Full archives, all listed member
hashes and text log chunks were independently downloaded/verified. RESULTS.json
records exact durable GCS prefixes, SHA-256 and source/tree closure records.

Next work requires a new authorized session: resolve the pinned decoder's scalar
list compatibility (schema encoding or separately reviewed decoder extension),
repin all inputs and perform fresh Cloud C0–C2 before any C4–C7 credit. This is a
checkpoint, not permission to run, adopt, merge or submit upstream.
