# Exact c1 entry and static conservation review

This is source/static review, no new proof. Actual Build3c845267 pins
e878dcf21e382935a1b31fe39a17f40fbb5bde5d; runtime SmallSort unchanged.

Direct current source consumers are small_sort_general_with_scratch lines254–255
and sort8_stable665–666. Both have T:FreezeMarker in this std; non-Freeze
specializations route to insertion fallback, network does not call sort4.
These source facts do not add Freeze to the generic diagnostic precondition.
Actual caller &mut[T] plus separate MaybeUninit scratch is a candidate source
of ownership/separation, but caller-to-predicate proof is OPEN. Raw readable4 /
writable4 do not derive exclusive current T.own, optional destination array_,
F.own/thread/type resources. Diagnostic requires positive-size T, source4/four
owners, optional dst4, current F cell/owner and thread/type; permits legal
interior mutation and compatible F aliases. Legal shared-entry and ZST/generic
applicability remains OPEN, even after conditional c1 success.

Pinned original Ast.Func/hash, source and paired complete MIR bind the sole c1
call to ordered refs1/0. Eight unchanged c1 local declarations move once into
strict child;24 later ref/tuple declarations move once after child;102 remain
in outer original order, including c1 and $_35. Normal assignment remains exact.
Pre-splice graph has three original gotos: outer bh0, internal label2, final54.
No prefix use of delayed vars; later normal uses occur after delayed declarations;
c1 unwind uses no delayed var. Only c1 direct Continue arm gets source debt+goto.
Normal original suffix ends in returning() before appended unwind label; epilog
is reached only by the new c1 unwind goto. Full header/posts identical by hash.
Remaining calls/copies/selects preserved:FnMut5/select8/copy4.

This is a structural argument for the exact pinned AST, not general translator
admission. Post-splice verifier scope/storage state and execution/label resolution
remain subject to fresh actual evidence. Tuple DeclStmt may allocate storage;
address_taken=false alone proves no storage theorem. Strict kernel retains chunks;
future alias/escaped-storage/label mutants and general profile qualification
remain OPEN. Isolated typed-survival/debt and false-post controls are prerequisites
for this diagnostic, not arbitrary FnMut recovery proof or accepted profile.
