# First-comparator provider-pin fix session

Phase MERGE-FIRST-CALLBACK-PIN-FIX-2026-10-18; stable owner merge.
T0 2026-10-18T08:41:55Z; main cutoff10:41:55Z; finishing-only11:11:55Z.
New separate budget960 Cloud seconds, one Build, timeout900 +60 queue envelope.
No carryover/retry. Historical103/960,857retired account remains CLOSED unchanged.
Existing v3 coordinator schema3/max3/one per owner; current reservations empty
at initial read. No raw audit for the new Build. Results only smallsort-brief.
Policy read: WORK-POLICY/COMPLETION-PLAN; Evidence Brief revision2026-10-17,
policy commit584891be87db5c056bf9082c1ad24665eea74e69.

## Source contract and hypothesis

Fix commita3b8029a changes only the expected base run.sh SHA in the production
adapter; all18 strict checks remain. Hashae0aa063624630f651fc4b466bc2e39c0ad017be75652a43ae2130eea672ca54
binds run.sh Git bloba7db3efdec43759d491d679e0237fbe9734646a9 at
08b61d8162b1c01c840ed573847622a004232a05. Other104 proof recipe paths unchanged;
all18 adapter inputs present in the exact proof recipe. Adapter and inputs come
from the same selected proof SHA. Three regression tests and independent source
review GO preserved in PROVIDER-PIN-FIX-REVIEW-20261018.md; no rerun required
without input changes. Session registration alone is new admission code, separately
synthetically tested and independently reviewed before submission.

Falsifiable setup hypothesis: committed corrected pin and same-source closure
pass provider validation; this does not imply any later stage ran or passed.
Keep same concrete-u64 FnMut/F effects/panic domain, actual three-cell caller,
CURRENT normal/unwind posts, source-bound prefix cut before tail.read, separate
full-body diagnostic with unchanged final posts. Actual std/runtime unchanged.
Full original obligations, resource provenance, exact source CFG, controls,
oracles and outcome mapping remain in FIRST-CALLBACK-SEMANTIC-CARD-20261017.md.
No semantic implementation changes authorized in this session.

Tool d928cb1d7ac60c257daa537fa65577f41135f832.
Profile experimental-merge-first-callback-u64-v1, SHA256
300fd8a7172c1644552b43c5bfda51a7c8a620f505012abd3760772df55102e3.
Patchb7bf867409fbf6fc6c0a9dcc25d3b286a94365380c30e4b3081dbd3f5708929d.
Compiler nightly-2026-09-25/f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f.
Semantic source files and all controls identical to failed campaign08b61d81.

## Required campaign and decisions

Preserve mandatory B1, ordinary normal/unwind, helpers, receiver/end/retirement,
default-off and generated-glue admission regressions. Source-bound first callback
requires concrete-u64 FnMut/HRTB (not mere registration), false/true normal CURRENT
resource restoration, first Continue panic recovery of loans/initialized array3/
owners/CURRENT F/thread/type/lifetimes/caller frame. Prefix partial theorem and
full-body diagnostic separate. Official first-unwind refinement, intended mutant,
resource/HRTB/binder controls and late-Cleanup refusal remain mandatory.
Existing prerequisite skips must be reported, never negative proof credit.
Late Cleanup→guard Drop→Resume cannot be replaced by first Continue recovery.

After terminal Build use only Evidence Brief. Report every target separately as
source-reported result or UNKNOWN if absent. No stage/cause inference from duration,
exit or absence of cases. If incomplete, checkpoint exact missing data and request
separate admin audit; no raw fallback or retry. If verifier exposes a semantic
blocker, checkpoint for owner decision; do not change semantics within this scope.
B2 stays open until full actual body/shift/gap/latepanic/cleanup/Drop/caller posts.
Release binding will name exact published proof/infra SHAs, hashes and preflight.

Admission review: independent GPT-6 Luna High GO after exact fresh used=0/remaining=960 guard. Six isolated service tests PASS; real/historical ledgers unchanged. Receipt: PIN-FIX-SESSION-REVIEW-20261018.json.
