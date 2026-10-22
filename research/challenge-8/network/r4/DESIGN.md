# R4 candidate: actual `swap_if_less` on the Select callback layer

Status **PREPARED / UNVERIFIED** (network-bootstrap-2026-10-22-n1). No proof tool,
compile or Cloud run happened. Proof credit 0. Not a verified Rust summary.

## Inputs (exact)

| Input | Identity |
| --- | --- |
| std `smallsort.rs` | upstream `cd371e03`, blob `40939f922bcb6fdc7ee0d30427fa861827043827`, SHA256 `85c75bc9…a175e1`; span 380–412 |
| Actual body bytes | SHA256 `f400911e90ac80f9a7d4ddac0b8e6e41b1aec7d67fa99dbb97da5c05b9c5f339` (span incl. trailing newline) |
| Tool base | `/root/verifast-network` `f76012fb518703b1d98e243ac4f487f16877cfcb` (stock specs read only) |
| Select layer (consumed, not copied into a second profile) | branch `research/night-select-sort4-cloud-2026-10-09` head `529b559e` (re-read at `10e13a41`; pinned blobs unchanged); `a1-actual-recover-pair.rs` blob `a29ad254…` (`comparison_debt`, `recover_pair`); ghost-strip regexes from `overnight-sort4/capture.py` blob `a7775d93…`; call protocol of `capture.py BORROW_PREFIX_FIRST_CALL` and `a1-actual-body-c1.py` blob `fd036cc0…` MARKER/NORMAL; translator overlays of the Select profile (`A1-ACTUAL-C3-R19-PROFILE-2026-10-22.json`, now `c7bbbc46…` at 3af7d37d) |

`swap-if-less-body.py construct` inserts ghost text only; `strip_ghost(crate)`
ends with the exact body bytes (checked). It refuses on any source SHA, span,
call-inventory, anchor or layer-blob mismatch, and refuses any
`select_unpredictable` text until P2 is published and pinned. From the layer
it takes only the `pred comparison_debt` and `lem recover_pair` ghost blocks
(as Select c1 does), never its fixtures or its failing negative case.
`test_swap_if_less_body.py` (unittest, Git blobs only, 10 tests) covers the
positive and the negative paths.

## Contract (safety/ownership; no ordering premise)

```
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*& type_interp::<F>() &*&
    a_pos != b_pos &*&
    *(v_base + a_pos) |-> ?a_before &*& <T>.own(t, a_before) &*&
    *(v_base + b_pos) |-> ?b_before &*& <T>.own(t, b_before) &*&
    *is_less |-> ?less_before &*& <F>.own(t, less_before);
ens / on_unwind_ens: same cells owned with current values, current F, thread, type_interp.
```

* Generic `T`, `F: FnMut(&T,&T)->bool`; no `Copy`/`Freeze`/purity/no-panic premise.
  No `0 < size_of::<T>()`: ZST admitted (distinct positions are two separate
  chunks even when the pointers coincide; no address-inequality premise).
* **Domain D1:** `a_pos != b_pos` (logical). All 25/45 sort9/sort13 calls use
  distinct literal indices (SOURCE-MAP), so this is the caller-needed domain;
  it is *not* the general helper theorem (equal positions: D3, OPEN).
* Normal post is ownership-level only, like Select's sort4 contract. The
  compare-exchange relation (which values end where, as a function of the
  callback result) is **OPEN (D5)**: the layer has no ghost link between the
  comparator `bool` and an order, and the post does not yet expose the
  post-callback values.
* Pointer facts: `v_base.add(k)` translates to `ptr_add_` (translator built-in
  without an in-bounds obligation); the candidate derives limits from the
  owned cells via `points_to_limits`. Caller-side in-bounds for sort9/sort13 is
  an integration obligation (W8), as for Select's `interior_pointer_limits`.

## Body ghost plan and frontier order

1. `let cmp_k = begin_lifetime()` / `let_lft 'cmp` around the actual `unsafe` block.
2. Comparator `is_less(&*v_b, &*v_a)`: exactly Select's c1 pair protocol with
   `left = v_b`, `right = v_a` (first argument first): full borrows → shares →
   `precreate_ref`/`init_ref_share`/`close_ref_own` → tuple own → fractions; the
   `__vf_callback_unwind_pair` marker block on the line before the call; normal
   path closes `comparison_debt`, `end_lft_binding`, `recover_pair`. Unwind path:
   the overlay attaches the same close/recover to the `call_mut` Continue edge,
   giving the unwind post (both cells owned, current F).
3. `hint::select_unpredictable(should_swap, v_b, v_a)` and `(…, v_a, v_b)` at
   `T = *mut T`: requires layer item **P2**.
4. `ManuallyDrop::new(ptr::read(v_b_swap))`: translator identity + typed read
   (`[f]*src |-> v`); the local holds a bitwise copy, the cell keeps its chunk;
   the own token stays with the value.
5. `ptr::copy(v_a_swap, v_a, 1)`: stock byte-level spec. Swap branch:
   `to_u8s_` on both cells, `exists(none)`; no-swap branch: `to_u8s_(v_a)`,
   `exists(some(0))` (self-copy needs write access, as the spec demands); then
   `from_u8s_` back (stock `to_u8s_` ensures `v == of_u8s_(bs)`, so the
   copied bytes read back as the source value).
6. `ptr::copy_nonoverlapping(&*v_b_swap_tmp, v_b, 1)`: `&tmp` is `create_ref`
   on the local (`precreate_ref` + `init_ref_readonly(…, 1/2)`), deref identity,
   reborrow; 1-element `array`/`array_` views for src/dst; afterwards
   `end_ref_readonly`. The `ManuallyDrop` temporary has no drop glue; the
   value's own token was never duplicated (one owner per cell at exit).

Expected first-run frontier: (2) passes only with **P1**; (3) fails without
**P2**; (4)–(6) are unverified ghost and the most likely place for repairs
(points_to vs points_to_ auto open/close, fractional `array` close, `ptr_add_(p,0)`
normalisation, ZST same-pointer chunk choice in the typed read).

## Layer gates (patch-candidate requests to Select; not implemented here)

* **P1 overlay admission.** The callback-unwind overlay chain admits pair
  markers only for its fixtures and the actual `sort4_stable` route (body-name /
  env gates). Needed: admit exactly one `__vf_callback_unwind_pair` marker in a
  body named `swap_if_less`, with the same fail-closed checks (exact 2-arg
  `FnMut::call_mut`, Continue edge, marker line = call line − 1, count match),
  bound to this source SHA/call line 395 (`let should_swap = …` in the std
  file; 1-based). To be a reviewed patch on Select's exact overlay commit,
  handed to Select; Network does not fork the overlay.
* **P2 pointer select.** No spec or body for `core::hint::select_unpredictable`
  exists in stock or in Select's actual route. Select R19 S2 (Build `8916761a`,
  head `10e13a41`, `task-history/select-c3-r19/SELECT-NEXT-DESIGN.md`) stops at
  its first selector with `No such function: std::hint::select_unpredictable`
  and rules out an unchecked spec (assumed summary); the gate is Select's
  option 1: finish the checked actual callee proof (S7: forget guard-own, then
  actual linkage) and expose it to actual-body routes under an opt-in with
  source/MIR certification. Select needs `<*const T>`; this helper needs the
  **`<*mut T>` instantiation** of the same generic callee proof — request to
  Select: cover/expose `*mut` too (no Network copy, no new trusted premise).
  The exposed checked summary must have the branching shape:
  ```
  req true;
  ens if condition { result == true_val } else { result == false_val };
  on_unwind_ens false;
  ```
  The conditional `ens` form is required so symbolic execution splits on
  `should_swap` (a `result == ite(..)` form would not match the cell chunks;
  otherwise a checked ghost case split lemma is needed). Until P2 is
  published the generator refuses any `select_spec`; admitting it is a later
  reviewed change that pins Select's checked callee by blob.
* **P3 equal positions (D3).** `a_pos == b_pos` has one cell, but
  `comparison_debt` carries two `borrow_end_token`s. Needs a same-cell callback
  variant (one full borrow shared to two precreated refs; marker/debt/recover
  names admitted by the overlay) — Select-layer extension request. Keying the
  existing predicate on pointer equality is rejected: ZST distinct cells are
  pointer-equal and Select's sort4 ZST route would change meaning.

## Required controls (generated by `matrix()`; run with the positive in the first Cloud task)

`python3 -B swap-if-less-body.py SMALLSORT_RS RECOVER_PAIR_RS OUT_DIR` writes one
crate per row plus `meta.json` (crate SHA and expected outcome per row) into a
directory that must not exist yet. Every negative is the positive with exactly
one ghost-only mutation (`strip_ghost` equal to the positive; std body exact),
except `equal-pos` (one synthetic-caller argument) and `own-drop` (helper
without caller, so the leak has one site); service-tested.

| Control | Variant | Expected |
| --- | --- | --- |
| positive | helper + generic caller `r4_caller_generic<T,F>` owning `v_base[..2]`, calls `(0, 1)`, rejoins | PASS; shows the precondition is satisfiable for all `T` (no size premise, so ZST included) |
| caller-zst | helper + caller at `T = ()` | PASS; ZST instance concretely; otherwise ZST domain is vacuous and must be reported |
| reach-before/after-generic, reach-before/after-zst | positive (or ZST) caller with `//@ assert false;` just before / just after the call | assertion failure at that line; a PASS means the caller state is inconsistent there and the positive callers are **not** evidence |
| equal-pos | caller calls `(0, 0)` | failure: precondition `a_pos != b_pos` |
| marker-off | marker block removed | overlay refusal or unwind-post failure at the call |
| unwind-no-recover | marker without `recover_pair` | overlay marker refusal, or unwind-post/leak failure at the call |
| swapped-roles | `left = v_a`, `right = v_b` | failure at the comparator call (ref/share mismatch) |
| copy-offset | `exists(some(0))` in the swap branch | `ptr::copy` precondition failure |
| own-drop | post drops `<T>.own(t, b_after)`; helper only | leak-check failure at the helper return |
| unchanged-claim | post adds `a_after == a_before` | postcondition failure on the swap branch |
| wrong-source / layer-blob / select-spec | constructor inputs | constructor refusal (service-tested, no Cloud) |

Every control is recorded by message and location (Evidence Brief), not by
exit code alone. The two positive callers guard against a vacuous contract
only together with the four reachability controls; a helper PASS without all
of them is not reported as R4 progress. The synthetic callers
are not std code; the caller's unwind post is stated on the two separate cells.

## HANDOFF for the first Network Cloud task

Not runnable now (budget 0, no Network lane). Prerequisites, in order: the
Cloud-readiness package (`../cloud-readiness/`) adopted by the owner;
**P1** (and **P2**) published by Select on an exact commit; a Network profile
pinning tool `f76012fb`, Select's overlay chain/patch SHAs from its current
profile plus P1/P2, this generator's committed SHA and the layer blobs above.
First Build: positive + controls on the same identities; accept nothing from
partial passes; report frontier by Brief message/location.
