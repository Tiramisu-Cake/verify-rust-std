# O26 wrapper-rebase admission profile (experimental, not accepted)

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
paths remain byte-for-byte unchanged. Cloud capture 347068de supplied the
source, decoded-unit and outer-body-7 SHA-256 values. They are admission pins,
not proof results.

The source certificate reconstructs the two complete ghost blocks at their
unique positions, before the first storage open and before the final select
comment. It checks the whole reconstructed item and tail, source spans,
ordered ghost strings and coordinates, nominal declaration, exact complete
unit and all nine body records. Only the observed source, unit and body-7
fingerprints differ from the canonical nine-body profile. The other eight
body fingerprints, five-body path, original source, std pins, signatures and
contracts stay fixed. Ghost stripping preserves runtime bytes and paired
refinement succeeds, but MIR represents the two new annotations as ghost
calls: the outer body has 44 locals and 27 blocks rather than 42 and 25. The
new ghost calls are blocks 8 and 20; forget is block 15 with `Move(_33)`,
normal 16 and Cleanup 26, and A1 assume_init is block 22 with `Move(_39)`,
normal 23 and Cleanup 26. Component 23 must conditionally check this exact
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
independent component-20 A1 `Move(_39)` to `Copy(_39)` TEST refusal reached
after owner admission. A setup failure, unrelated helper refusal, timeout or
wrong predicate/location is INCONCLUSIVE. A diagnostic collection result is
separate from actual full-proof acceptance; no TEST profile can establish the
production theorem.
