# M3 paired resource invariant — design before implementation

Experimental checked ghost dependency, no primitive or verifier semantic change.
Actual source remains pinned repository blob `40939f922bcb6fdc7ee0d30427fa861827043827`
(upstream cd371e03 and our branch have identical SmallSort blob). FreezeMarker
blob `e1977d79f32076488e37048d17be77e37a321b0c`; marker.rs blob
`64a67bbd11c12bc6dd03867cb5c479642dbec3a6`.

First close actual up/down full current-source/F ownership and option-scratch
posts under explicit valid-pointer C1 domain. Do not use their summaries before
same-source full callee acceptance. Then expose two indexed source cells from a
whole owned array, retain every other cell in a checked two-hole frame, and
restore potentially updated current values/owners after each callback. Within
one up/down call G2 implies left index < right index for positive stride; across
successive calls cursors can refer to previously visited cells, whose single
owners are recovered before reuse. No second own is minted by address equality.

Define owned-array and two-hole predicates by explicit stock initialized
points-to and T.own resources. Their logical list is an input parameter, not
an output parameter: this records the represented list without claiming
predicate precision. Extraction/restoration and list-update lemmas must have
checked recursive bodies, keep all cells/owners, and consume the two real
cells/current owners when filling holes. The old-value list lemma carries the
same selected values through recursion and only requires equality while an
index remains nonnegative; after an index passes below zero, that selected
value is irrelevant to the recursive list. The pure old-value list theorem
also handles indices beyond the list without requiring an unrelated length
conversion from the resource fixture's `usize` count. No ownership bridge axiom. Domain
n>=2, indices 0<=i<j<n, positive stride; ZST remains open. Full normal/unwind
resource invariant later keeps input array current valid owners, comparator
current state, and all destination option cells, including partial writes on
panic. A normal physical copy creates initialized scratch memory, never T.own.

This first resource dependency is generic safety, with arbitrary comparator
answers and lawful interior effects. It proves no unchanged entry values,
permutation or stable ordering. Actual bidirectional_merge has FreezeMarker;
stock VF has no Freeze model. Before functional/owner transfer, separately
justify direct-byte snapshot stability under this actual bound (not recursive
purity of indirectly referenced objects), then combine G2 terminal guard/A
occurrence multiplicity/B SWO+immutable-key+faithful-answer premises. The marker
source explicitly excludes UnsafeCell internally but allows indirection; F state
may change and answers may remain arbitrary for safety. Caller CopyOnDrop and
network scratch panic strategies are separate source-linked obligations.

Matrix for the two-hole dependency: arbitrary-index extract/restore preserving
all owned-array values/resources and unrelated frame; restored current values
and owners, exact list replacement; duplicate-owner and wrong-value restoration
at intended obligations. Full export/decode/refinement/body/return/leak/dead/source
gates. No concrete actual M3 claim until unchanged body, callback outcomes,
for-loop/guard/odd-copy and resource posts pass under the declared profile.

## Continuation scope repair (not a new semantic rule)

Recovered b04b1b6/run37717433930 fails typechecking the standalone invariant
at313 before bidirectional body entry. Kernel verify_block checks labelled-block
assertions using entry types before executing preceding ghost let declarations.
Pinned translator make_var_id_name_maps retains parameter `dst`, renames the
shadowing mutable program cursor `dst_1`, and explicitly does not substitute
ghost surface names. Remove ghost dst_base; use parameter dst for both original
option slots, dst_1 for current forward cursor, and unchanged dst_rev for reverse.
No pointer/resource equation is weakened and no address equality yields ownership.
Hosted source/AST gate must confirm this fixed name relation; whole iterator linkage
and ordinary for-loop invariant attachment remain experimental. Len2 cannot pass
strict wholebody acceptance while actual odd branch is unreachable.
