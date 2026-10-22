# Network → Select: layer requests for actual `swap_if_less` (R4)

From Network task `network-bootstrap-2026-10-22-n1`, 2026-10-22. Requests, not
patches: Network does not fork Select's overlay/profile chain (BOOTSTRAP,
CURRENT-TASK bounds). Read at Select head `10e13a41`. Each item, if accepted,
should land as a reviewed change on an exact Select commit that Network then
pins. Proof credit: none either way.

## P2 — checked `select_unpredictable` callee, also at `*mut T` (shared blocker)

Select S2 (Build `8916761a`) stops at the first selector, `No such function:
std::hint::select_unpredictable`; `task-history/select-c3-r19/SELECT-NEXT-DESIGN.md`
option 1 (finish the S7 actual callee: forget guard-own, actual linkage; expose
under opt-in with source/MIR certification) is the only admissible route.
`swap_if_less` (std lines 405–406) calls the same generic callee at
`T = *mut T` instead of `*const T`. Request: make the exposed checked summary
cover both raw-pointer instantiations (or the generic `T` at pointer types),
with the branching post shape `ens if condition { result == true_val } else
{ result == false_val }; on_unwind_ens false`. Network has no other route and
will not add an unchecked spec.

## P1 — callback-unwind admission for one pair marker in `swap_if_less`

Current gates (patch `actual-sort4-c2-recovery-r17.patch`, blob `f2f26f23`, on
top of `overnight-callback/verifast-callback-unwind-26.10.patch`):

* the marker is admitted only in fixtures `callback_positive`/`callback_false_post`
  and in body `sort4_stable` under `SORT4_ACTUAL_BODY_*` env opt-ins;
* call lines come from `SORT4_ACTUAL_BODY_FIRST/SECOND_CALL_LINE`/`CALL_LINES`
  (exactly five) and the verified-source SHA check is sort4-specific;
* c1/c2 argument checks match `<*const T>::add` with literal offsets.

`swap_if_less` needs exactly one marker (index 1) before
`let should_swap = is_less(&*v_b, &*v_a);` (std line 395), whose arguments
are reborrows of locals obtained from `<*mut T>::add` with variable offsets
(`a_pos`, `b_pos`). Request: a parameterised admission — body name, exact
verified-crate SHA, single call line and expected argument shape supplied by
the opt-in — keeping every fail-closed check (exact 2-arg `FnMut::call_mut`,
Continue edge, marker line = call line − 1, marker count, no second marker).
Network's generator emits the c1 protocol unchanged
(`comparison_debt`/`recover_pair`, names `t, cmp_k, left, right, left_ref,
right_ref, left_fraction, right_fraction`). Whether Select's scope/referent
relocation overlays are also needed for this body is unknown until a run.

## P3 — same-cell callback variant (equal positions)

For `a_pos == b_pos` both comparator arguments are the same owned cell; the
pair debt holds two `borrow_end_token`s and cannot be formed. Request (lower
priority; not needed by sort9/sort13, which always use distinct literal
indices): a same-cell variant — one full borrow shared to two precreated refs,
its own debt/recover names admitted by the overlay. Keying the existing
`comparison_debt` on pointer equality is rejected: distinct ZST cells are
pointer-equal and the sort4 ZST route would change meaning.
