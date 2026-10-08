# Actual nested guard and SAFE forget: integration boundary before patch

O17 (`37717092130`, `11d888ba`) passed the independent pointer-value
post-completion lemma and entered the actual helper under a compatible post.
Its first body error was missing `MaybeUninit::<T>::new` because that source
unit lacked the separately checked S6 callee bodies. This is a linkage
setup failure, not an ownership proof result. O16 showed the truthful
qualified owner exports in both MIR modes. The stock `safety_proof`
candidate retains the full pointer-value post; its linked O18 attempt
stopped during source preparation, before proof.

`prepare-actual-owner-linked.py` is a source-only step. It reuses the pinned
actual std body and existing source-certified S6 constructor, as_mut_ptr and
pointer-drop methods in one unit. It inserts the truthful nominal owner
projection, stock `safety_proof` and two qualified nested Drop opens, then
checks exact executable bytes under one deterministic ghost strip. The
hosted checker captures the full NORMAL/readonly outer/nested MIR and the
frozen S6 gate rejection. No verifier rule is active through this script.

O18 (`37745138207`, `bb9c46bc`) stopped before export: the preparer
counted a standalone unwind annotation that also occurs in two linked S6
callees, then rejected the actual safety-proof insertion as ambiguous.
The actual contract has a distinct adjacent annotation tail
`@*//*@ on_unwind_ens false; @*/` before its body. The preparer now selects
that exact tail. The next hosted capture still has to establish ghost-strip
identity, both MIR modes, refinement, and the frozen S6 gate's first refusal.
O18 supplied no complete linked owner graph or proof.

O19 (`37746579002`, `a6f9d5e0`) produced the missing linked capture:
NORMAL and readonly export/decode, refinement, ghost-strip identity and
source integrity all pass. The outer full-record SHA-256 is
`0bb582fcf2baf193c8a25267b74b34572c6b1bb6c701d920bba78634cad483be`
in NORMAL and
`7ff18621be59b543166b68ea05773b10a805ab1ef524dae27b4f61e306ca2b9d`
in readonly; nested Drop is
`5f31dc01e01a659b80fa90326d3dd2fc3f13f7db74ddb77a587416c29b73e8f3`
and
`6770a073b7315aa5ae0e708687ca3139cb40d040cc200e47ee8b6017490bb400`.
The normal outer body has 41 locals and 24 blocks, including shared cleanup
bb23 with nine incoming call-unwind edges; the nested Drop has four blocks.
The outer body's `ghostStmts` inventory has 12 ordered entries, including
the two source opens inside nested Drop at lines 95–96. Those opens export
in the nested body as consecutive `VeriFast_ghost_command` call terminators;
the nested body's own `ghostStmts` inventory is empty. The existing frozen
S6 gate rejects at
`actual SAFE contract/source signature`, before any body proof. These
fingerprints describe evidence only and are not a frontend admission rule.

The proposed complete decoded-body fingerprint must be audited before use:
the `vf_mir_decoder.ml` implementation is generated only on hosted builds,
so its return type, coverage of every `Body` field, and absence of lazy or
shared mutable references are not established by checked-in source. The
current project schema enumerates locals, blocks, spans, contracts, ghost
commands, generics, clauses and visibility. A diagnostic-only implementation
may compute and print a candidate digest, but it must reject before any
semantic redirect until the generated decoder and canonical representation
are reviewed. Raw source/MIR textual hashes alone do not authorize a rule.

O20's hosted generated decoder source fills that representation gap for
this pinned toolchain. Its `body` type is an immutable algebraic record of
all 26 schema fields; `decode_body` eagerly maps every field, including
all local declarations, all basic blocks, contracts, source spans and ghost
metadata. `decode_vf_mir` similarly maps ADTs, all bodies, global ghost
batches, modules, target and pointer width. No reader reference, mutable
field, lazy value or closure appears in these output types. This is an
inspection of the generated decoder, not a proof that Marshal bytes are a
stable trust certificate. `verifast-actual-owner-fingerprint-probe-26.10.patch`
therefore only prints a complete-unit and per-body diagnostic digest after
the exact O19 source/ADT checks, then unconditionally rejects before any
redirect. The hosted `--fingerprint-probe` mode can calibrate that
representation. It writes the complete `Marshal.No_sharing` bytes for the
unit and each of its five bodies to hosted evidence, reruns the same unit
with the same binary and source, and records SHA-256, byte lengths and
byte-for-byte repeat equality. This tests determinism within the pinned
profile; admission remains a separate reviewed change.

The first semantic overlay may extend only the *admission* of the existing
S6 constructor/as_mut_ptr/intrinsic/pointer-drop rules to that new exact
linked source unit. It must leave the accepted five-ghost mode unchanged.
Pin the complete verified and original source, std `hint.rs` and dependent
std source hashes, all callee bodies and contracts, the qualified local ADT
and owner declaration with source spans, every outer ghost statement and
contract (including stock `safety_proof`), and complete typed local/outer
MIR with statements, terminators, drop flags and all normal/unwind edges.
The new ghost statements alter block/local numbering, so the frozen S6
graph certificate cannot be reused by matching function names or selected
calls alone. Preserve the shared Cleanup block and every reachable
predecessor. A mismatch is an admission rejection, not a proof negative.

The next separate overlay is an **actual nested H2 mode**. The selected ADT
is `select_unpredictable::DropOnPanic<T>` with exactly one private
`inner:*mut T` field and the exported Drop DefPath
`<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop`. The owner
definition is exactly `*g.inner |-> ?payload &*& <T>.own(t,payload)`.
The source-written nested body opens its actual full borrow and this owner
before the unchanged `self.inner.drop_in_place()` call. A source-equivalent
generic pointer-drop callee must be fully proved in the **same unit** under
`thread + initialized cell + <T>.own` with normal and unwind posts
`thread + optional uninitialized cell`, then linked by exact typed FnDef,
generic substitution, receiver `Move`, source span and complete nested
MIR. H2b's selected generated Drop post must return only that optional
cell, the stock field/padding resources and thread on both outcomes. It
must not return an initialized value or manufactured `<T>.own`; ordinary
Drop bodies remain on the stock template. The local top-level H2 proof
does not establish this nested mode.

Only then may a **separate SAFE forget link** redirect the actual one-call
site to a same-unit proved exact generic unsafe forget body. The proof
requires the guard constructor to transfer the selected initialized cell
into nominal owner, the unselected cell to remain outside, the pointer
Drop to consume and return the unselected optional cell, and the selected
owner to be opened immediately before forget. Its callee contract needs
only the thread, preserving the selected cell as a frame. The call
certificate must check the actual nominal type/substitution, `Move guard`,
cleared drop flag before that move, exact std SAFE forget source, and
normal/unwind successors. A false-unwind projection is allowed only after
the same-unit callee proof and a complete CFG certificate; cleanup shared
with other predecessors remains reachable. Reclose the selected wrapper
after the call, then prove final actual `assume_init` preserves the full
selected pointer and returns the thread. No `Element` pointee permission
is introduced.

Admission controls should mutate source/ADT/owner spans, field visibility,
generic substitution, ordered ghost commands, call operand `Copy` versus
`Move`, projection, drop flag and cleanup targets. Each must reject before
proof. Resource controls should remove a selected cell, target the other
slot, duplicate cell/thread, require pointee rights, demand initialized
post-drop storage or value-own after Drop, and falsify normal/unwind posts.
Each counts only at its intended body obligation after all other setup and
callee proofs pass. Positive acceptance requires full same-unit verifier
exit zero, both MIR modes, refinement, every body return/leak, actual
nested Drop normal and unwind checks, actual helper normal and false-unwind
checks, and no disabled dead-code, validity or memory checks. Until the
complete linked source/MIR capture exists, there is no honest concrete
frontend patch for this new mode; a source-only fixture is the falsifiable
next checkpoint.

## Root review for O21 calibration only

Generated O20 decoder eagerly preserves every schema Body/VfMir field in
pure algebraic records, including full typed local/statement/terminator/ghost
spans and ADTs. No deferred reader/closure/mutable inference model is present
in this decoder layer. Stdint custom scalar serialization and compiler/OCaml
Marshal format remain pinned implementation dependencies; byte-repeat evidence
is required. No_sharing removes physical sharing from the representation.
Main approves diagnostic dump and repeat, not a serialized-digest proof rule.
MD5 printed trace is never a new semantic certificate; full byte files and
SHA256 are captured externally for independent review. Original/verified/std
source identity, source-to-MIR correspondence and ADT checks remain separate.
The probe always refuses before existing S6 redirect, so cannot certify a
helper or supply any rights. Default-off path uses the unchanged old S6 rule.
A later semantic gate needs a separately reviewed complete graph representation,
strong integrity check, exact input source/qualifiedowner/signatures, positive
resource proof and direct typed-MIR/source negatives; calibration is insufficient.

## O21 reviewed admission design, before implementation

O21 (`37750512251`) repeated the same NORMAL decoded unit and all five
decoded bodies with `Marshal.No_sharing`; each first/repeat byte stream was
identical. The complete unit was 60174 bytes with SHA-256
`3075b627aab5c0548f6f30a3727af5215bc6859a446009263de718b20a18d66e`.
The ordered constructor, as_mut_ptr, pointer-drop, outer actual helper and
nested Drop body digests were respectively
`6527c8df047e70602b40ec03b17614a3e278b19f23ef94a4aa5e87f6793c39b7`,
`396dcf5b5a509121fcaf9afc35c8b64bff04a866140bec59b03a2d8724db4db7`,
`5b495817c6ce57c0ff0bec146ffe0bde9f735900f75ac4f3cd72c13ead22a070`,
`e44b5f3aec64a0ccf97cbf473c0d5fb348e5dd4e68b597e63a03ef255245c1e9`,
and `70493e53b55743ead2f08035908d251656f3b55da123bee5c1ac2e93370e767f`.
The complete verified source digest is
`595e93c5c08ebd61a6ab4b7f7b98ed2f2d6765dbb8d903509a53391ea9a2b5b3`.
The independent pinned std `hint.rs` digest is
`ce89716d46b8060db2c2da1aef1d4bcccf90e0804fc021d4470c55203501315f`.
The full unit digest binds every eager decoder field, including ADTs, full
locals, statements, terminators, contracts, ghost batches, source spans,
drop flags and cleanup successors; body digests identify any mismatch.

The proposed opt-in gate checks these exact SHA-256 values, the five ordered
DefPaths, pinned hint source and its reconstructed runtime body with every
exact ghost insertion, full actual contract/safety proof/owner definition,
existing separate local-callee certificates, explicit local ADT identity and
typed pointer-drop receiver, intrinsic counts and shared cleanup. Its only
effect is to admit the existing typed S6 redirects on this exact unit. It
does not prove any owner predicate, nested Drop or SAFE forget. Default-off
and frozen five-ghost admission remain unchanged. The gate rejects any
changed source, representation or inventory before proof; a fresh source
variant needs fresh review and fingerprints. Negative controls will mutate
the source/ghosts, typed graph/cleanup, and admission opt-in and require an
exact certificate refusal, not merely a verifier error.
The three prepared ghost-only mutants exercise the verified-source SHA gate;
they do **not** exercise the decoded-unit SHA gate. A separately labeled
hosted negative must feed a valid altered Cap'n Proto MIR message with the
same source bytes into a disposable verifier invocation and require the
exact decoded-unit refusal. Such instrumentation is a control only and
cannot support a positive proof or change the accepted compiler profile.
`capture-actual-owner-mir-mutation.py` prepares three such hosted
controls: the actual `forget` operand in bb16 changes from plain `Move(_34)`
to `Copy(_34)`, or its cleanup successor changes from shared bb23 to valid
bb22, or the first qualified nested Drop ghost call's terminator source
span moves only its start line from 95 to 94. The third control checks the
compiler-origin ghost-call span bound by the same complete unit SHA. It
first runs the real exporter in NORMAL/readonly modes and the real
refiner, then a shadow console whose sibling exporter wrapper runs the same
real exporter, decodes one complete message, mutates exactly one typed field
and re-encodes it. The wrapper records canonical/mutated text and bytes,
binary hashes and tool identity. The classifier accepts only the exact
`owner complete decoded unit SHA256` frontend refusal before any target
body proof, with unchanged source, successful real frontend/refinement and
an exact recorded mutation. The shadow profile is never a positive proof.

The compiler, generated decoder, OCaml Marshal representation and host OS
`/usr/bin/sha256sum` binary are trusted correspondence dependencies pinned
to the hosted profile. The SHA command receives only quoted temporary paths,
checks its exit status and exact output format, and removes both files. The
hosted run must recheck NORMAL/readonly export, refinement and full verifier
under the new overlay. No disabled memory, validity, unwind, dead-code or
leak checks are permitted.
