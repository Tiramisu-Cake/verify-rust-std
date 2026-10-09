# Actual tmp-to-tail span diagnostic — CONFIRMED PREFIX BLOCKER

Consumer: actual insert_tail550–551; CopyOnDrop immediate diagnostic copy is
literal-one, while actual557 copies sift→gap and558 updates dst. This report is
for VeriFast review preparation only; no external message/tool application sent.
Runtime std and signatures unchanged. Positive-size generic/no-callback adapter,
not ZST/full insertion/Drop/glue/comparator proof; profile NOT_ACCEPTED.

## Reproduction inputs

Preserved checkpoint83b22ba6576c0a4441d2bdf90dd9419eb527aff6. Source std
SHA25685c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1,
blob40939f922bcb6fdc7ee0d30427fa861827043827; VFf76012fb518703b1d98e243ac4f487f16877cfcb,
nightly2026-09-25/compilerf7575a9da8e4a4fca3b5668d5a2ea7476db44b3f,
x86_64-unknown-linux-gnu. Full frozen hashes are in PROFILE.json and
cloud-build/src-align-recovery/MECHANISM-AUDIT.json; no new trusted patch.

Exact proof/infra334c837991ec3d034a375807219b8648dfcbb611; Cloud Build
b3234929-e691-47c1-905c-dffbffafc9b5. Use the existing merge recipe,
pinned-objects mode, owner merge and an independently authorized live account.
Do not reuse this session's closed budget later. Source preparation and verification
must remain Cloud-only. prepare.py generates the SmallSort-pinned full-post input;
no local extractor/compiler/verifier is required or allowed.

Minimal source-linked causal prefix is the exact two adjacent std statements:

```rust
let tmp = ManuallyDrop::new(tail.read());
// real initialized immutable storage, tracked precreation/init, complementary share
let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };
// checked actual src == held_ref and actual dst == tail
// existing to_u8s_/from_u8s_ lemma preserves real source fraction/value, derives alignment
// existing points_to_limits derives source object bounds; assert no address overflow
// assert numeric byte-span disjointness HERE, before any own/FBC close
```

The complete generated input retains own/canonical FBC close/open, the original
post-FBC alignment/bounds/separation assertions, literal-one copy, reference end,
complementary tmp merge, lifetime end, held-owner recovery assertion, and full
normal/applicable unwind posts. The new early assertion does not delete or replace
any target check. Source/MIR/AST/refinement/evidence bind its actual constructor
and immutable tmp/shared-derived src. It tests initial geometry without the FBC
existential field abstraction; no convenient alternate runtime pointer.

## Established alignment and distinct obligations

Build6f00cfdb-c587-4d4a-b2ab-f18b92d7f4f6 /7e19788b93b2299a0d383e2b266d336ae37fdaad
checks constructor src identity52, own/FBCclose54/open55, storage-preserving alignment
lemma57, source nonnull59, alignment60, object limits61, no-overflow62. Both
positive and recovery-false stop separation63 beforecopy64. All exporter/decode/
refinement stages0, verifier1. This proves a prefix, not full posts/recovery.

Exact existing prelude d1079bc94ceafe6595c7ce216f9c93e3436d22d849bd31bcb0cf442dd183e751:
to_u8s_349–351 consumes [f]points_to_(p,optionvalue), returns same fractional bytes,
alignment of that p and value==of_u8s_(bytes); from_u8s_345–347 consumes those
bytes using derived alignment and restores the same typed option value/fraction.
The fully-bodied initialized_storage_alignment opens/closes points_to(some(v));
its normal post/leak and both later calls are checked. T.own remains framed.
points_to_limits247–249 provides object bounds only. None of these creates a
logical owner or implies numeric separation. Reference bookkeeping alone supplies
no initialized bytes/permissions. init_ref_readonly consumes real tmp storage;
create_ref/reborrow preserve actual pointer identity before packaging. Canonical
mutable FBC hides exact field/value witnesses, so the external held_ref equality
is not exposed after opening; alignment after open uses its returned source storage.

## Frozen model audit and candidate missing rule

Saved patched kernel100eebae92c770a0b8cd57e2639588761f881316dd522fc3b9a9b1ec6fd91cd6
at1115–1119 allocates an address-taken local by get_unique_var_symb_non_ghost and
produces its real typed storage fraction. Pinned verifast1.ml6687–6714 makes a fresh
uninterpreted pointer with its own pointer_within_limits; Rust does not invoke the
C assert_mk_pointer path. Pinned assertions.ml362–367 adds nonnull on points-to
production; generic chunk matching/merging281–321 exposes no cross-object numeric
interval exclusion. Prelude include closure (core_core/list/nat/listex), patched
core and std expose no applicable generic local-vs-caller span lemma. Box/Vec
specific APIs do not establish stack tmp versus this arbitrary incoming tail.
Fresh symbolic identity and differing provenance are not numeric span proofs.

Required rule for maintainer review, **not an implemented axiom**: a newly created
live, address-taken Rust local of positive byte extent must expose a numeric
allocation interval disjoint from pre-existing live allocations covering the
incoming writable tail region. Tie this fact to allocation/liveness identity
and transfer the same address/extent through the actual initialized shared
reference and field packaging. An applicable verified region-resource projection
would also suffice. Mere pointer inequality, fresh symbol names, type or distinct
provenance must not imply it. Do not grant arbitrary raw pointers the property.

The rule must preserve all physical fractions, source value encoding, reference
initialization/end tokens, complementary storage, guard fields/padding and sole
CURRENT logical owner. It grants a pure geometry fact, no points-to/byte authority,
no new T.own, no initializedness or validity. Aliases of one allocation retain
possible overlap; overlapping readonly fractions remain legal. ZST has separate
alignment/logical occurrence obligations and must not be excluded from project
safety by this positive-size diagnostic. Trust review/regressions and separate
owner authorization are required before any tool semantics change.

## Work remaining after geometry

Even a span rule does not prove destination geometry after abstract FBC, full
copy/sole-owner transfer, ending the matching held reference, complementary actual
tmp storage reconstruction, guard/local cleanup, complete target normal/unwind/
return/leak, or actual Drop/glue. A proof-only guard resource interface may need to
carry genuine ref_readonly_end_token/ref_initialized keyed to current src and
preserve tmp/held/destination anchors; it may not mint or assume them. This is
DESIGN_ONLY, not a checked summary. Actual caller still owes CURRENT tail/sift
owners, thread/type/frame and borrow closure after first comparator. Readonly
quiescent protocol cannot cross legal interior-mutating later comparator callbacks.

Final constructor-span evidence: Buildb3234929 terminalSUCCESS342s, archive2824d5c5e7ca176d86c00ddff295dbfd77faac927ab9d95534251b9d0f7be36f,
complete archive/external text integrity verified. Both cases exporter/decode/
refinement0, verifier1; src==held_ref52 and dst==tail53 pass, genuine storage
alignment54/object limits55/no-overflow56 pass, sole failure constructor span57
before own58/FBCclose59. Current pointer terms are actual reference outcome and
tail0, not abstract reopened field witnesses. This confirms the initial geometry
blocker independently of FBC information loss. No copy/full recovery/post/actual
Drop or first-shift credit. The exact logs/source/AST/classification hashes are in
[receipt](../../../../cloud-build/src-align-recovery/EVIDENCE-b3234929.json).
