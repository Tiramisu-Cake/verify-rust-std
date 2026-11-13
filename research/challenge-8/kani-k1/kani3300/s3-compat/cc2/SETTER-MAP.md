# CC2 setter map — prepared before the patch

Base b2e1a392ad27bd21758473bc208ff66c2d7d0405. Source analysis only;
selected CC2 MIR/model, dynamic witness and last setter are UNKNOWN until CI.
Prior bool/ref findings are source-reported in mode-findings/FINDINGS.md; no
saved raw artifacts were opened. Property descriptions alone are not witnesses.

| Source/MIR event | Storage and typed mask | Existing producer / missing edge | Consumer / obligation |
| --- | --- | --- | --- |
| `passthrough(value, initialized)` entry, and ordinary scalar helper entry | Local argument `initialized: bool`; scalar ABI data byte, not its truth value | ptr_uninit entry only loads union/MU arguments; delayed visitor has no entry event. Missing setter for ordinary argument storage | delayed `CheckRef(initialized)` on reads when field-insensitive aliases select it |
| Helper entry with `&bool` / `*const MaybeUninit<u8>` | Local pointer representation only; thin/fat pointer ABI data mask, no pointee traversal | Same missing argument-entry setter. Caller operand checks must run before entry; local visitor checks raw-deref reads independently | CheckRef of the pointer slot is distinct from CheckRef/Check of its referent |
| `Rvalue::Ref` / `AddressOf` and assignment of reference/scalar | Destination place, destination type's data mask | delayed visit_place(mutating) already emits SetRef(true, After); creating the address does not read its referent | Later source Copy/Move reads remain checked; invalid caller payload is not repaired |
| Generated aggregate captures `initialized` by `&bool` | Captured reference field is environment storage; enclosing closure requires its actual rustc layout | Aggregate destination already has delayed After SetRef; nonzero closure mask is currently Unsupported (CC3). Do not invent offsets or flatten | Ensures reads stored `&bool`, then `bool` referent; both need separate bound producers |
| `Use(Copy/Move)` of wrapper / tuple / environment | New destination storage, same supported typed data mask; padding excluded | delayed After SetRef already handles ordinary destinations. Parameter copy across a call additionally needs entry setter. Nonzero upvar layout remains CC3 | Source CheckRef stays Before; no replacement with assume, no removal of checks |
| `Call { destination, target: Some(..) }` normal return | Actual return destination, its typed mask | delayed mutating destination already yields After SetRef; MutableBody split_bb_after inserts it on the normal edge. No new return protocol needed | Reads of destination follow normal completion only; callee return read remains checked |
| MU/flat MU storage or ordinary union argument/copy/return | Existing false/preserve/whole-storage transfer masks | ptr_uninit owns existing paired protocol and copy rules; generic SetRef skips MU. New entry admission must reject union layouts and nested MU/union layout errors | Hole checks, Move clearing and argument pairing retained |
| Unsupported aggregate / nested union / closure | No admitted ordinary data mask | Do not seed, substitute all-true, or recurse through pointers; existing reached layout diagnostics remain | Unsupported is not a successful bool-init test |

Candidate: add an ordinary **argument-slot** entry event to delayed instrumentation,
restricted by the same `needs_set` alias criterion as writes and an existing
`PointeeInfo::from_ty` Sized data mask. No setter for return local 0, other locals,
union/MU storage, or unsupported aggregate layouts. Use SetRef to address the
argument slot, never Set (which addresses its pointee). Preserve pending entry
operations for an empty first basic block. Existing copy/normal-return setters
are retained rather than duplicated; CI must bind their actual selected sites.

The new capture-free tests isolate ordinary scalar/ref and supported wrapper
entry/copy/normal-return from closure layout. Original captured inputs remain
unchanged. Selected MIR/model request and exact reachability criteria are in
CI-REQUEST; absent binding stays UNKNOWN, not evidence that a setter ran.
