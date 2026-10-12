# Narrow I storage/layout prerequisites — design before implementation

Session started 2026-10-11T23:37:59Z; main deadline 2026-10-12T01:37:59Z;
finishing-only absolute deadline 02:07:59Z. Owner verifast; new Cloud ceiling3600s.
Start98bd08b1; policy6e1a8e59 (normative revisione3db6b5e), ADOPTION already carried
by start; effective v3 coordinator retained, peers untouched. Own worktrees:
/root/verify-rust-std-i-actual-glue and /root/verifast-i-actual-glue.

## Actual obligation and boundary

Base I b6cb276afd13107c2a90ca50acbb12ff0a992dd8; reference glue a158398e336edce9817f62a55733a3470a986d7b.
Actual std source is this project's SmallSort at the pinned start; concrete
nongeneric guard source is the independently saved natural_onecell extraction
from project6283377b/Builda9613c24. The consumer is the constructor/resource prefix
of natural_onecell: incoming legal u64 tail, tmp=ManuallyDrop::new(tail.read()),
CopyOnDrop{src:&*tmp,dst:tail,len:1}, physical fields/padding and readonly source.
No new entry premises: especially no assumed numeric src/dst separation.
C3 generated glue/selected method and actual insertion cleanup are NOT_RUN by scope.
No selected-method/refiner rewrite is necessary for a prefix gate; the official
refiner still must build and check the matched prefix pair. A diagnostic prefix
is never declared the full Drop theorem.

## Proposed rules and justification

B-ORIGIN: rustc f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f MIR syntax.rs
StorageLive contract explicitly allocates fresh uninitialized stack storage;
StorageDead deallocates. step.rs dispatches to stack.rs storage_live_dyn/dead;
stack.rs uses LocalValue Dead/Live and deallocates the old indirect allocation.
Only parser-inexpressible translated MIR events in this opt-in unit may create
receipts. Fresh *incarnation*, not local name, is authority. A local storage span
is separate from still-live positive-size incoming storage with positive legal
points_to permission, and from another actually allocated live incarnation.
This is the bounded allocation rule, not generic array/T/ZST or arbitrary-raw
pointer disjointness. A receipt supplies occupation/origin, never read/write
permissions. Existing I production and free_locals retain all validity and rights
checks. Unsupported local extents and duplicate live events are explicit refusals
(the latter conservatively unsupported rather than pretending MIR forbids them).

Incoming origin admission initially references the exact incoming chunk object.
New chunks from consume/open/close/produce never acquire it through matching
addresses/predicates/value/type or physical similarity. At strict scope exit only
an explicit old->new mapping made by the existing checked heap freeze may
transport the association, for unchanged predicate/coefficient/terms/size and
frozen/rebased type arguments. The old object must still be in the current heap.
The mapping is continuation-scoped and restored on return/branch backtracking;
no shared global mutable provenance table leaks between paths. Consumption loses
that incoming association; unsupported transformed-lineage cases refuse to supply
allocation geometry. Local receipts occupy the owning local's lexical scope and
are retired on StorageDead/free_locals/loop cleanup. Dead->Live creates a fresh
symbolic incarnation; numeric address reuse remains possible, no assumptions
against retired storage. Pure facts about the old incarnation confer no authority
for the new one. Fresh pointers alone do not imply numeric separation.

B-LAYOUT: only rustc's pinned PostAnalysis layout_of of the exact concrete guard
and u64 on x86_64-unknown-linux-gnu/64 is allowed. Keep all I empty Rust structs
size0 and C positive-size rules. Transfer only metadata schema/AST/model portions,
not v8 selected-effect/general memory rules. Add compiler commit and whole source
SHA256, using rustc_span SourceFileHash::new_in_memory(Sha256, full source bytes),
to the internal receipt. Bind source allowlist to committed profile fixture pins,
nominal DefPath/hash, exact nongeneric field names/types/mutabilities/shape, target,
ABI width, layout size24/align8, field sizes8 and actual recorded offsets (not an
assumed Rust repr order). Exporter/translator/kernel reject foreign metadata before
asserting model facts. DefPathHash is corroboration, not a cryptographic source pin.
Actual exporter/compiler/schema/binary hashes and paired original/verified source
receipts remain mandatory; a self-declared compiler field is not compiler admission.
No source annotations can fabricate the internal attrs. Duplicate attrs reject.

B-FREEZE: retain I's entire strict entry/exit inference/type/bounds freezing,
rebase and scoped-escape checks. Safe mapping follows a legal surviving resource,
not structural equality. Test survivor vs consumed/reproduced, nested scopes,
missing rights, wrong identity and branch-locality. The bounded tmp allocation
precedes tail.read in MIR, so source-tail separation need not follow the consumed
chunk through that read; no general resource-transform transport is proposed.

B-DEFAULT: one exact opt-in profile setting plus source admission; absence leaves
I semantics and emitted paths unchanged. Invalid/0/partial/mixed native/selector/
glue settings refuse before execution. Tracked immutable ManuallyDrop references
are narrowed to admitted concrete u64 prefix units. Internal markers require the
same active profile; source calls with marker spellings cannot construct AST nodes.
Preserve I MDnew CFG, slice as_mut_ptr, certified pointer-drop, selector seals,
FRAME/Bool/native behavior. Reuse F1 classifier, no wholesale merge chain.

## Validation decision

First C0 source/settings closure, C1 changed-component build plus official refiner,
C2 positive bounded resource prefix and exact gate controls: forged/foreign layout
and source/compiler/target/type/hash, overlap, raw/missing permissions, strict
survivor/reconstruction, consumed/retired receipt and reused storage. A negative
counts only at intended metadata/rights/assertion gate with body entry evidence,
never incidental setup failure. Record unsupported cases and all NOT_RUN.
Only after C0-C2 proceed to affected C4-C7 I routing/resource/regression gates.
C3, B1/B2/O23 remain open; no profile adoption/merge/upstream PR.

Rule rejected: local-name inequality as numeric-span disjointness; it lacks an
allocation/liveness witness. Rule rejected: structurally/equal-address rebuilt
chunk origin; it can regrant consumed permissions. Rule rejected: disabling strict
freeze or importing whole v8 chain; it discards I trust and unsupported consumers.

## Explicit consumer-closure addendum before implementation

Preserving the actual CopyOnDrop implementation may require the existing checked
selected-effect/gen_drop_contract branch from a158398e. If so it is an explicit
prerequisite dependency, not an unreported metadata-only change: the source method
body and its canonical safety_proof must both verify with full resources and
normal/unwind posts. No generated glue, Instance observation, Drop terminator
redirection, official refiner semantics, or receiver/end adapters are imported.
The optional effect augments the concrete canonical post only from a checked
body/source-specific proof, not an assumed summary. Exact source/type/profile
admission applies to it, and arbitrary predicates or types fail closed. The
constructor/resource prefix keeps the same source statements and entry premises;
its suffix may invoke the separately checked concrete method for CURRENT/tail
recovery and forget the guard to avoid executing the deferred C3 edge. Such a
suffix remains a diagnostic harness, not actual compiler glue. If that prerequisite
can't be justified or verified, record consumer branch NOT_RUN/blocked. Never
remove the actual Drop impl, skip its proof, or weaken constructor resources to
claim C2 closure.

Independent CONDITIONAL GO reviewed before tool implementation (REVIEW-DESIGN.md).
Accepted conditions: require/check known positive extents and within-address-space
no-wrap bounds before numeric interval assumptions; retain entry type/heap freeze
and map at each actual heap reconstruction only when current old Chunk survives.
The added rule does not infer bounds from a raw address or turn a receipt into
permissions. Unsupported/resource-transform lineages explicitly refuse geometry.

## Implementation boundary resolved before tool assembly

Static I gen_drop_contract inspection confirms that the intact safety_proof closes
CopyOnDrop_drop_effect while the stock canonical post contains fields/padding only:
that effect would be left as a leak. The independently reviewed minimal normal
effect-post addition is therefore a concrete C2 callee dependency; no selected
Drop routing or generated-glue semantics are imported. C2 suffix uses ordinary
ptr::copy_nonoverlapping plus ManuallyDrop (explicit Drop::drop calls are illegal
Rust), with the real method body/safety proof retained and checked separately.

Follow-up independent review approves resource-checked use of I's existing
TRUSTED points_to__limits summary, not a new bounds axiom. Fresh u64 invokes this
summary ordinarily. The compiler-qualified guard has a liveness receipt but NO
new numeric span exclusion: C2's actual geometry consumer uses tmp versus tail,
not guard-address disjointness. Full guard24 numeric limits and generic storage
remain unsupported until a checked whole-resource derivation exists.
