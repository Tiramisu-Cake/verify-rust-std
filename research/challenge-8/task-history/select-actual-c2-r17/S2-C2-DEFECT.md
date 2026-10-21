# R17 S2 c2 constructor defect and controls

## Defect and applicability

The R16 full-body constructor provides c1 recovery only. The actual second comparator call uses ordered source operands `(v_base + 3, v_base + 2)`, and R16's c1 resource setup does not precreate references for that call. Reusing the c1 scope or its `recover_pair` debt would leave the c2 callback without an explicit resource path for its two ordered references and the current four source owners.

The change applies only to a source-only wrapper constructor layered on the existing c1 constructor result and pinned `a1-actual-recover-four.rs`. It does not certify that the source annotation was consumed by the exact MIR call; the fresh source/MIR receipt remains open.

## Parser constraint and invariant

The pinned preprocessor accepts `let_lft` declarations only immediately after the real `unsafe {` body opening. A c2 lifetime declaration placed later in the function is parsed as an ordinary command and cannot bind a strict lifetime. Keep the existing c1 declaration and append c2’s declaration to that same exact header comment. At the c2 setup point, emit `__vf_callback_scope2()` after creating `cmp2_k`; the translator consumes this ghost marker to split the header lifetime declarations into distinct strict scopes at c1 and c2. Both edits erase as ghost syntax and preserve runtime bytes.

After c1 recovery, c2 establishes a fresh lifetime and a fresh split of the current four owners. It retains all four borrow-end tokens, shares only slots 3 and 2 in source operand order, precreates the two reference resources from those slots, and forms the reference and tuple ownership required for the typed c2 call. Normal and direct-unwind recovery close the same four-source debt for `base=v_base`, end only the c2 lifetime, and invoke the checked `recover_four_sources<T>(v_base)`. The emitted runtime remains byte-equal to the original full body: five comparator calls, eight selectors, and four copies.

## Distinguishing controls

Provide source-only annotation controls that preserve `ghost.strip_ghost(verified)` exactly:

- Wrong ref resource: precreate c2's left reference from slot 2 while the call's first operand remains slot 3.
- Wrong marker index: change `__vf_callback_unwind_four(2)` to index 1.
- Missing debt token: close the negative four-debt predicate without the `v_base+3` borrow-end token, then attempt the normal four-source recovery.
- Displaced marker: move the c2 marker away from immediately before the actual c2 call.

Each control is a constructed input for later Cloud qualification only. Its metadata must remain proof-ineligible, and neither construction nor static inspection establishes proof success or exact MIR call attribution.

For every control, recompute the actual-body focus/end coordinates, both c1 and c2 comparator lines, and the required lemma rows from that candidate source. This matters for the missing-token control, which adds a declaration before the actual function and shifts all later line coordinates.

## Translator correspondence and checked binding

The new opt-in is restricted to exact source-bound R17 sort4_stable with c1/scope/HRTB prerequisites. It parses the original c1 marker and indexed c2 four-cell marker separately; retains the original typed add(1) and c2 typed add(3),add(2) operations and their successors; requires direct Continue unwind, enabled unwind paths, adjacent source marker, ordered unique call index and exact source coordinates. The real call is unchanged. Added receiver/ordered tuple equality assertions must be discharged by the existing precreated-reference and FnMut kernel rules; they grant no ownership themselves. Receipt lines explicitly say CHECKED_ASSERTIONS_REQUIRED rather than proof acceptance.

Two lifetime declarations originate in one parser-accepted unsafe-header BlockDecls annotation. The translator requires exact ordered declaration/witness names, exact two cut markers, and one separate source scope2 marker strictly between cuts. It removes only that second declaration from the first scope and places it at the scope2 ghost-command location with the second cut as its close. The original unsafe block and runtime nodes/edges are unchanged. Both scopes retain strict entry/exit gates and current-owner recovery.

MIR erased callback cells are selected from compiler decoded types and exact source spans at the five ordered source call sites, with one receiver, one tuple and four reference cells per call (exact30, distinct original raw/translated identities). c1/c2 receive separate strict-scope declaration sets; remaining c3-c5 cells are confined to the final normal suffix. Complete-AST use containment rejects cross-call uses, escape, address exposure, shadowing, duplicate/missing declarations, wrong types and unknown constructors. Source nodes/labels/gotos and their order remain conserved by the existing wrapper validator. Seven new synthetic indexed-scope controls run only in Cloud alongside existing scope controls. Unknown inventory or CFG shape fails closed.

These are candidate invariants, not execution/proof claims. Full c1/c2 branch receipts and actual normal/unwind remain OPEN until Cloud evidence, and required wrong-receiver/call-order qualification must be evaluated separately from coordinates or source metadata.
