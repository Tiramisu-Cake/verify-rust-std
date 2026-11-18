# Terminal intake and owner-policy review

Native run44380273557/attempt1 is COMPLETED/FAILURE with matching push head,
branch, tree and event. Setup and stock compiler build are SUCCESS. Provider
and verified_control each independently exited 0 with one
`VERIFICATION:- SUCCESSFUL` marker and successful semantic properties.
Ordinary_stub exited 1 and emitted the exact error:

```text
error: Failed to find contract closure `__kani_recursion_check_f` in function `stub_contract_confirm::f`
```

The native fixture exhibits the reported compilation defect signature.
Producer classification remains **INCONCLUSIVE** with original reasons
`provider control failure` and `workflow status: failure`. Owner-policy
reclassified observation also remains **INCONCLUSIVE**: the authorized
count-only exception cannot establish every substantive requirement from the
retained evidence.

Three concrete limitations prevent DEFECT_PRESENT under the requested gates:

1. Both control exports were parsed and marked present/complete by the
   collector, but their documents were discarded when the count predicate
   raised. Digests and sizes remain; export configuration, check buckets,
   outcomes and actual export counts are unretained and UNKNOWN.
2. Complete stdout inventories contain provider89 = 88 SUCCESS + 1 UNREACHABLE,
   verified52 = 51 SUCCESS + 1 UNREACHABLE. The same `f.assertion.1` body property
   is unreachable in both. The frozen oracle independently requires every
   property to be SUCCESS and every unreachable bucket to be empty, beyond
   count equality. This is not independently established as pinned counts only.
3. Ordinary's complete error inventory includes the cargo execution wrapper
   `error: Failed to execute cargo (exit status: 101). Found 1 compilation errors.`
   and the standard cargo `could not compile` summary. Its text reports one
   compilation error and no other substantive compiler defect is visible.
   However, the frozen primary-error filter excludes only aborting/could-not-
   compile summaries, so it treats the execution wrapper as another primary
   error. The narrow count authorization does not change that predicate.

The source of the producer reason is preserved: `success()` stops at the
first failing count guard and never stores the export in the observation;
`observe()` classifies ordinary as unrelated/ambiguous under its header filter.
The job-level failure reason is also preserved. This packet does not make the
original strict oracle appear to pass.

Archive SHA256, result byte SHA256 and canonical payload SHA256 all match.
All four source snapshots match frozen stock/control/request/profile/workflow
and file inventory identities. Compiler/driver come from the separate stock
checkout and their before/after digests match; argv/env/cwd/features/selectors
and fresh targets are checked for each slot. These are compact collector
observations bound to native metadata, not an independent rebuild.

Pure-Python replay and synthetic mutations pass. The count exception is tested
separately and retains target, status, check flags, failed/unreachable-property,
error, presence, null, size and completeness guards. No verifier was executed.
See REPLAY.json, RECLASSIFICATION.json, COUNT-TABLE.md and SLOTS.json.

Native job duration is 208 seconds. Setup step is 71 seconds; build process
121.178 seconds (native step122), provider0.987 seconds, verified0.527 seconds,
ordinary0.229 seconds. Exposed verification times are provider0.101460256s and
verified0.06927465s. Build sampled process-group peak RSS2031894528 bytes;
provider211066880, verified209731584, ordinary181051392 bytes. Limits and scope
qualifications are in COST-AND-SCOPES.json. No new cost or ledger action.

ISSUE-DRAFT.md is a standalone English draft with the dependency-free fixture,
matching command options, actual diagnostic, native successful controls,
support-or-clear-diagnostic expectation and issue-specific AI disclosure.
Its external proofreading copy is byte-identical at
`/root/smallsort-pr-drafts/ISSUE-STUB-CONTRACT-DRAFT.md`. Publication is NOT_RUN.
