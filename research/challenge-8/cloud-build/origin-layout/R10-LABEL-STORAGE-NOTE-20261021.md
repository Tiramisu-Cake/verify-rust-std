# R10 label invariant / annotation temporary boundary

Build5 compiles and parses the checked invariant. Exact bounded log1330-1337
shows invariant consumption, dummy/empty cleanup and leakcheck, then production
and StorageDead failure at verified/lib.rs276:44-45. This is limited observed
initial-path progress, not Continue/backedge/break/unwind proof. Native decoded
Body receipt binds insert_tail / Runtime(PostCleanup) fingerprint e1f455a3ed9fb435,
real cycle97<-151, head source275 let_lft. Generic label-invariant handling is
involved; no While-only gate receipt was found. No-match alone is not NOT_RUN.

Bounded decoded MIR fragments identify local _117 as tuple=[] (unit), its
StorageLive at source276, VeriFast_ghost_command call with bare destination _117,
and following StorageDead at source276:44. These are source observations, not
established parser-input binding or causal proof; see Build5 result identities.
Kernel verify_block/goto_block (verifast.ml~3193-3297/~3080-3122) checks a label
invariant and separately produces its body from the enclosing block env.
RustStorageDead (~1046) requires the actual runtime local binding, introduced by
checked StorageLive (~1052ff), not merely a tenv declaration.

Next exact obligation: bind _117's annotation-only instrumentation lifetime and
reconstructed label/body placement; preserve the real Live/Dead pair and checked
resource state across the invariant boundary. The earlier exact lateNoop
normalization did not establish this routing. Review any fix against ordinary
non-annotation locals, real physical StorageLive/Dead, cleanup and default-off;
do not make StorageDead a no-op, fabricate live receipts/ownership, replay a
fresh allocation, or weaken leak/invariant checks. Unit instrumentation may admit
a source-preserving placement fix, but none is established or implemented here.
Read-only diagnostics for generic label invariants would be a useful next gate.

No sixth Build: remaining735 gives maximum timeout675, work_seconds605 and
runner deadline590. Observed complete cold attempts599/621/644 (latest577) do not
establish safe current target+teardown margin under that envelope. No cold
compile-only budget probe. BeforeLive/prefix independent source tasks and current
freshness provenance work were completed separately; no new storage/model bridge.
