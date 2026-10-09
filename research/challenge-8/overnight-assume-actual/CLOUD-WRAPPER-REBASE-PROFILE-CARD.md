# O26 wrapper-rebase component 23 R2 (experimental, not accepted)

The canonical nine-body proof reaches the final checked selector and fails on
the ownership predicate indexed by the current `MaybeUninit` wrapper. The
source-only candidate saves ownership for both earlier wrappers, consumes both
old indexed predicates, and closes ownership for the two wrappers now held in
their cells. The hypothesis is that this reindexing supplies the final call's
existing precondition. A failed open, close, or call remains a proof failure.

Component 23 applies only after frozen components 1–20 and the reviewed
literal refresh components 21–22. It is a distinct, opt-in experimental
certificate. The pair `SORT4_WRAPPER_REBASE_REPO_ROOT=<exact proof root>` and
`SORT4_WRAPPER_REBASE_ADMISSION=1` must be present together; a partial pair,
wrong root, or missing existing nine-body owner/A1 opt-ins is rejected. With
both absent, the canonical nine-body and historical five-body certificate
paths remain byte-for-byte unchanged. The earlier component-23 profile is
preserved at its committed Git SHA; R2 is a distinct experimental certificate
for the Cloud 293435cf source-only capture, not a result of proof acceptance.

The source certificate reconstructs two insertion regions containing ten
single-statement ghost comments, at their unique positions before the first
storage open and before the final select comment. The two early assertions
bind the old wrappers in the enclosing scope; eight later commands consume
their indexed chunks and reclose the current wrappers. There is no nested
ghost block that could hide the old bindings. The certificate checks the
whole reconstructed item and tail, source spans, ordered ghost strings and
coordinates, nominal declaration, exact complete
unit and all nine body records. Only the observed source, unit and body-7
fingerprints differ from the canonical nine-body profile. The other eight
body fingerprints, five-body path, original source, std pins, signatures and
contracts stay fixed. Ghost stripping preserves runtime bytes and paired
NORMAL/readonly refinement succeeds. The observed outer body has 52 locals
and 35 blocks, rather than the canonical 42 and 25. The two new early ghost
calls are blocks 4–5; the eight new later ghost calls are blocks 21–28.
Forget is block 16 with `Move(_34)`, normal 17 and Cleanup 34; A1
assume_init is block 30 with `Move(_47)`, normal 31 and Cleanup 34. The
pointer-drop receiver is `_30`, and the unwind chain is resume 32, drop 33,
switch 34 on `_51`. Component 23 must conditionally check this exact
observed graph at every owner, pointer-drop, forget and A1 gate. The old graph
checks remain when opt-in is absent; no wildcard offset or relaxed count is
permitted. The two redirect counts, parser, kernel, specifications, runtime,
normal/unwind posts, memory validity, dead-code, leak and refinement checks
stay fixed. This pointer-specialized outer obligation does not prove
unrestricted generic std.

The outer contract still requires the thread token, returns exactly the
condition-selected input pointer with `raw_ptr_own<Element>(t, result)`, and
has `on_unwind_ens false`. The source change supplies no new pointee
permission and does not alter the checked callees' normal or unwind posts.

The separate Cloud recipe must capture fresh NORMAL and readonly MIR,
refinement, full nine-body inventory and all ten Marshal records before
refresh. It must compare the unchanged eight bodies and source pair to the
canonical capture. The old certificate must refuse the new source; that is
only an admission negative. The new profile needs a real positive stage with
all seven callees before the outer body, the generic nested Drop proof, full
resource checks, four isolated component-17 source/MIR negatives, and an
independent component-20 A1 `Move(_47)` to `Copy(_47)` TEST refusal reached
after owner admission. A setup failure, unrelated helper refusal, timeout or
wrong predicate/location is INCONCLUSIVE. A diagnostic collection result is
separate from actual full-proof acceptance; no TEST profile can establish the
production theorem.
