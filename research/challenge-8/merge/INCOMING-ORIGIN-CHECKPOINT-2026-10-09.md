# Incoming MIR lifetime origin — frozen checkpoint

User continuation of a74d612731f41969e688326456b34b55a880c5a7 and publication
fbc063ce609cc549358e3bbc0f8b3a12b75b3945. Main window20:16:40–21:16:40UTC;
finishing only until21:46:40UTC. Owner merge. Policy revision
1fcd91eff1507fe0bd0620a23b578edb454f1c3e; instructions read at exact starting
checkpoint plus VeriFast AGENTS/WORKFLOW/STATUS/upstream build docs.

**Candidate6cb7b6736c4ef7978d2f3a80737952ac7148cccb is NOT_FOR_INTEGRATION.**
Origin implementation is repaired and independently source-reviewed, but the
requested origin semantic gate is OPEN. Generic runtime extent is unsupported.
Build SUCCESS and six matching mechanism controls do not establish acceptance.

## Ownership and versions

Proof worktree /root/verify-rust-std-merge-origin, branch
merge/incoming-origin-20261009, git-dir
/root/verify-rust-std/.git/worktrees/verify-rust-std-merge-origin, starting HEAD
fbc063ce. Own tool worktree /root/verifast-merge-incoming-span, branch
merge/incoming-span-lifetime-20261009, git-dir
/root/verifast/.git/worktrees/verifast-merge-incoming-span, starting HEAD75099c95.
Branch/HEAD/git-dir and clean tool status checked before edits. Root maintainer
and other proof worktrees not edited. Tool owner remains merge until explicit
transfer; VeriFast agent performs later review/integration in fork. No upstream
publication; separate owner review/approve remains required.

Tool code f55e3f8a27c5cb2fc69ad0859e87f5097d844470 changes private AST, MIR lowering,
AST printers/visitors and kernel lifecycle dispatch. Final6cb7b673 adds valid
native C test and removes frontend-invalid Rust-body marker test. Base f76012fb
with exact ordered baseline/profile patches, hashes and bundle in review packet.
Proof/infra first01c832b272ddfe45c0df8298a278761c6aae3aaa; corrected second
2bf268f792a5a8705292d4b7b8935eba82ca9847. Profile
experimental-merge-incoming-origin-onecell-v3, NOT_ACCEPTED.

## Origin boundary and conservation

Only MIR StorageLive/StorageDead lowering emits RustStorageLiveStmt/
RustStorageDeadStmt. Statements carry execution location, original MIR span,
raw local ID and translated local name. Source/extern/ghost calls remain ordinary
CallExpr; no name or expression shape grants lifecycle semantics. Kernel matches
private AST constructors. Ordinary diverging calls retain normal call/terminator
handling; no lifecycle shortcut creates a continuation. Original names are
unchanged, so this is not reserved-function renaming.

Path-local live/dead bindings, fresh address epochs and address reuse remain.
StorageDead invokes existing free_locals and must consume physical storage;
block/function cleanup and leak checks remain. Entry authority requires the same
surviving Chunk identity, with no automatic restoration after loss. Drop,
ownership and unwind obligations were not suppressed. Full path validation is
still required; static conservation review is not its substitute.

Independent read-only review found no remaining source-call lifecycle route or
localized conservation defect. Follow-up established exporter default in-memory
preprocessing matches verifier; on-disk source hashes stay checked at every
stage. Provenance correspondence is to verifier-preprocessed MIR. Retirement
audit binds exact raw IDs and same-block relative order. Broader origin-call audit
compares sorted event identities/lines and target operand dataflow; it does not
establish complete CFG/order equivalence or every local-name mapping.

## Fresh proof, replay, limits

Build6cf7f205-a3a0-46d3-9419-938c5b20d72b: FAILURE,394seconds; profile compiled.
Five prior controls matched; retirement INCONCLUSIVE because readonly standalone
MIR IDs differed from verifier-preprocessed MIR. Native verification succeeded
but link failed (exit2). Extern fixtures were frontend-invalid. Preserve this
archive/classification; no retroactive proof credit.

Buildf068379c-3849-4ed2-b593-00b9547ce617: SUCCESS,380seconds, corrected2bf268f7;
archive3d192ec6d346327987ce1736ab5a1ecbd91d9d224144bc6c9991e45781a7840a.
Fresh six controls: scalar span positive PASS; retired-local reuse, overlap,
arbitrary raw pointer, lost incoming authority and abstract zero extent each
EXPECTED_REJECTION at its intended assertion. Retirement raw tmp0=_2 dead at
line23 precedes tmp1=_12 live atline24 in block7 statements4/5, with matching
private AST events and names. Reuse remains possible; lost incoming authority
is not regained. Native reserved-name ordinary C prototypes pass (-c, exit0,
two statements). Source pins, stage logs and profile hash checks retained.

Additional origin controls: ghost reserved-name declaration is explicitly
FRONTEND_REJECTION at prefix admission, not a semantic negative. All six Rust
extern/diverging/baseline/resource/branch controls fail parsing at ghost fn
prototype line11 before the target. The attempted fixture repair did not work;
these failures prove neither a supported extern admission prohibition nor the
requested semantic negative. Local-death-after-leak EXPECTED_REJECTION reaches
StorageDead line15, with exact MIR/AST local binding and missing physical chunk.
Live-local normal/unwind case has ordinary CallExpr provenance and36matching
MIR/AST lifecycle events but fails missing points_to atline32. It is INCONCLUSIVE;
normal/unwind resource closure is not proved. Therefore origin gate remains OPEN.

Saved classifier replay reproduced all17classifications. Replacing private
storage tags with legacy CallExpr in copied evidence is rejected by retirement
gate. Replay is isolated classifier service testing; no local compilation,
extraction or proof, and no new theorem evidence. Both Cloud archives/config/
source/file inventory/upload receipts and external text index are verified;
external text chunks were not downloaded. Full Rust suite/full make test,
all Drop/loop/reentry paths and independent VeriFast acceptance are NOT_RUN.

## Runtime extent and actual consumer

Permitted geometry remains fixed scalar/pointer extents; u64 span proof is limited
mechanism evidence. Generic T, structs and arrays remain excluded. Actual scalar
consumer specialization was NOT_RUN and is not inferred from the scalar control.

Concrete unit ghost size_of::<()>()==0 fails intended assertion9; runtime
core::mem::size_of::<()>() result==0 fails intended assertion10, independently in
both builds (exporter/decode/refinement0, verifier1). These are MODEL_LAYOUT_FAILURE,
not origin negatives. Unit is modeled empty struct std_tuple_0_, but all Rust
struct sizeof values receive a strictly-positive axiom. Generic sizeof(typeid)
has no actual target layout bridge. Exporter has no serialized Layout::size;
FieldInfo.isZeroSize only recognizes PhantomData. Detailed source references
and minimal unit reproducers are in phase RUNTIME-EXTENT.md and controls.

Missing rule: typed physical storage, pointer arithmetic/object bounds and
interval geometry size term must denote actual Rust byte layout T on the pinned
compiler/target, preserve generic instantiation and ManuallyDrop<T> layout, and
admit zero-sized valid types without all-struct positivity contradiction.
Unsupported layouts remain unsupported. Removing positivity alone cannot prove
apartness. No extra supplied separation premise or speculative layout patch.

New-profile actual generic reproducer is NOT_RUN: origin-only repair cannot cure
the current separation refusal. Preserve prior actual positive source and log as
minimal reproducer: actual tmp=ManuallyDrop::new(tail.read()), guard src=&*tmp,
dst=tail,len=1, unchanged pre-FBC span assertion at diagnostic line69. No new
actual FBC/read/copy/Drop/ownership/end-reference obligations are reached here.
Generic proof and true caller/comparator remain separate. T=() enters actual
small_sort_general through size_of::<T>()*48<=4096; another insertion loop's ZST
skip does not eliminate this caller. No generic geometry is enabled.

## Accounting and handoff

New budget3600seconds create→finish, old remainder closed separately. Used774;
unused2826closed, not inherited. Both own builds terminal/accounted/download-
verified, active_build=null. Coordinator released reservations; merge ready
request withdrawn. No unresolved own builds. Ledger/phase docs and STATUS are
committed with checkpoint; review package preserves previous packages and carries
exact bundle/diffs/tests/driver/profile/evidence. Publication receipt follows in
separate organizational commit. No receipt, transfer, integration, consumer pin,
upstream approval or acceptance is implied.
