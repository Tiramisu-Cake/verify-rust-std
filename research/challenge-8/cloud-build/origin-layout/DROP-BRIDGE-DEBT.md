# Nearest actual Drop / caller obligations

This is source-based dependency analysis, not a new proof run or an accepted bridge.
The concrete-u64 source-linked direct-copy/recovery witness remains the bounded consumer.
Actual CopyOnDrop::drop and natural cleanup/glue are different obligations.

## Frozen caller interface

Own assigned tool source src/rust_frontend/vf_mir_translator/vf_mir_translator.ml,
Drop terminator translation around2920–2971, lowers natural cleanup to
std::ptr::drop_in_place(&mut place). Rust forbids explicit destructor method calls,
so an invented direct Drop::drop runtime call is not an actual caller edge.

The frozen bin/rust/std/lib.rsspec drop_in_place<T> specification around597
consumes thread_token, typed guard points_to and T.own; normal and unwind posts
return the thread token and guard storage with unspecified value. It does not
return CopyOnDrop's source fraction, destination CURRENT value or copy effect.
The generated safe Drop prototype (gen_drop_contract around4411–4570) returns
fields/field owners/padding. Its canonical FBC includes fields and guard own.
An isolated strong functional body contract is not automatically dispatched
through this generic glue interface.

The earlier exact-source callee collector's count-n result is conditional and
historical on its profile, not a fresh result on8cb0121b or a root caller proof.
Its supplied guard bounds/separation premises and any own=false compatibility
vacuity cannot establish the actual caller's obligations.

## Guard physical layout

A full actual body/caller needs guard positive byte extent, alignment, object
bounds/no overflow and guard-vs-source/destination physical intervals. Neither
nonnegative sizeof nor points_to_limits alone proves all these facts.
Canonical unit0/align1 correction and concrete u64 byte extent do not provide
CopyOnDrop<u64>'s ABI or arbitrary generic local extent.

A future bridge must obtain layout facts from the pinned compiler/target and
qualified nominal type/representation, preserve them through translation, and
relate the same extent to physical storage and pointer geometry. Do not guess
sizeof(CopyOnDrop)=24, hardcode an unqualified user struct name, add a positive
size premise, or assume separation from retained chunks. ManuallyDrop erasure
only preserves an already qualified inner layout. ZST can share addresses.

## Conservation and next falsifiable boundary

The current scalar readonly protocol starts with an existing const half-share;
init_ref_readonly(...,1/2) splits it into two quarters and an end-token for one
quarter. Guard packaging/copy/recovery must conserve that exact source quarter
and recover CURRENT bytes, not replace them by entry snapshots.

After this bounded witness closes, an actual cleanup caller must derive its
guard physical frame and apply a same-source-version verified Drop effect through
a justified call/glue interface. A caller post failure against generic
drop_in_place is retained as interface debt; it is not repaired by assuming the
strong leaf post or restoring lost authority. Comparator/caller/user-Drop and
generic/ZST obligations remain open. No readonly transfer through arbitrary
comparator is proved here.

Within this session the useful bounded result is the canonical-unit patch plus
the concrete actual read/guard/FBC/copy/recovery witness. Generic glue effect and
qualified guard layout require substantial additional implementation/review;
they are not silently included in profile acceptance.
