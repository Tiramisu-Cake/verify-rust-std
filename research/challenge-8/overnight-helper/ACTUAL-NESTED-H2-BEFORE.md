# Exact-nine qualified nested Drop linkage: before patch 18

Patch 17 proposes only admission of existing S6 rules to O24's exact
nine-body unit. The actual qualified nested Drop still contains an
unresolved generic pointer drop call. The already checked H2a/H2b local
component has the same generic runtime method and four-block Drop shape,
but its ADT and Drop DefPath are unqualified, so name substitution is
not enough to transfer its summary.

This separate default-off overlay is conditional on patch 17's exact
nine-body source, ADT, complete decoded MIR and std pins. It checks the
same-unit public unsafe sort4_checked_generic_drop<T> exact source
signature/body, three contract clauses, generic T input and typed MIR,
and the qualified nested Drop source/span, two ghost-command
terminators, one plain Move(_4) receiver, exact FnDef<T>, normal bb3,
unwind Continue and full four-block graph. It then translates only the
qualified nested call as an ordinary FnCallOutcome to that same-unit
checked method and selects the H2b optional pointee-cell tail for the
qualified ADT's generated Drop post. The generated tail is used on
both normal and unwind outcomes. It returns stock field, padding,
borrow and thread resources plus only *inner |-> _, never the old
initialized value or <T>.own after Drop.

The generic method consumes thread, initialized *slot cell and the
input <T>.own and returns thread plus optional *slot cell on normal
and unwind. The nested body must open the actual full borrow and
truthful nominal owner from source, then prove its real call and both
return/leak obligations. Neither an arbitrary guard owner nor an
Element pointee right is introduced. This overlay leaves the outer
SAFE forget, A1 transmute/assume_init, actual helper full normal post
and false unwind post untouched. Shared cleanup remains reachable
through all original predecessors.

Activation uses a separate exact-root environment flag after patch17
admission. A successful frontend gate or local H2 fixture is not a
proof of the actual nested Drop. Only a full same-unit verifier pass,
with every body checked and both nested outcomes returning/leak
checking, can qualify its summary. Direct typed-MIR mutants of the
nested receiver, generic substitution, normal/unwind target, ghost
span or extra block must reject at the exact unit/source gate; source
mutants must reject before proof. Missing optional cell, duplicated
cell, retained <T>.own and false post controls must fail at their
specific post obligations after the checked callee runs.
