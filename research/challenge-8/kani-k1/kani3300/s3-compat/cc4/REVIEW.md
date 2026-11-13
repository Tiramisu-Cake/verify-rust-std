# CC4 author static review — independent review pending coordinator

Scope: metadata on the existing CC1 failure path, two exact supplied expectation
corrections, three diagnostic extraction/order fixtures, descriptive limitation.
No nested agents; coordinator retains independent review, push and CI ownership.

Static audit checks existing body selection, exact call-transfer equivalence after
removing metadata plumbing, unchanged dataflow/result/error boundary, immutable
per-root map and fresh ActiveCalls. The provenance enum is fixed by the same
registration/discarded predicates, so repeated-key equality has the same result
as (Instance,overridden). Origin resolves RunContract with the same function-map
entry/args as contracts.rs. It is metadata only; analyzed body remains body_ref.
No runtime body is newly selected or recursively instrumented by this change.

Symbols precede long Debug identities. Incoming callsite prints bb/index/span;
parent frame supplies owner identity. Diagnostic truncation is explicit and
never treated as attribution. InternalMir uses a synthetic CRATE_DEF_ID, so it
cannot establish selected origin; the explicit provenance carries that identity.
The existing error remains latched and rejects every partial graph. Successful
callee joins and normal return/copy/argument behavior are unchanged.

Preservation audit covers all3517 existing test files except the two approved
expectations; old Rust inputs, other goldens and8 strong-oracle bindings match
CC3. Fixture extraction is token-identical after removing comments/whitespace;
only sibling removal and harness order differ. No new failure golden, collector
acceptance change, graph summary/cache/cutoff or schema expansion.

Python/static audit15/15 and existing offline Python oracle checker21/21 PASS.
Scratchpad rustfmt and git diff --check PASS. First formatter scratch attempt
could not resolve child modules; reran formatter only with skip_children=true.
No compiler/build/test runner was invoked. Rust typecheck,8 helper Rust units,
fixture execution, new diagnostic/model/complete failure binding: NOT_RUN.

Review risks for coordinator: pinned rustc/stable API compilation, origin resolution
and symbol rendering, metadata bounds and source spans, selected MIR binding,
actual root grouping/order, complete inventories and useful cover/assertion
reachability. Source equivalence of saved exports is established; exact binary
provenance and independent proof credit are not. Remaining two cyclic paths
need exact typed windows. Saved SimpleCheck has no recorded cycle; its collector
cover gap is separate and is not repaired or waived here. Part1 remains NO-GO.
