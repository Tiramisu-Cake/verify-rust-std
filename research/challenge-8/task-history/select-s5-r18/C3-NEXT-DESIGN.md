# c3 next step: design note (unverified, not implemented)

## Defect

With S5 the actual sort4 body passes c2 and stops at the c3 call `lib.rs:299` `let c3 = is_less(&*c, &*a);`: `aliasing.rsspec(88)` cannot consume `ref_precreated_token<T>(ptr_add_(v_base, 2 + 1), _)` (Build `0ee7f658`, `S5-evidence.json`). c3 has no lifetime, borrow, share, precreated-ref, tuple-own or debt setup; c1/c2 annotations end before it. This is the expected next frontier, not a regression.

## Applicability

The c3–c5 operands are selected pointers, not fixed slots: `c = v_base + 2 + c2`, `a = v_base + c1` (c3); `d`, `b` (c4); `unknown_right`, `unknown_left` from `select_unpredictable` (c5). On each verifier path these are concrete offsets (the log shows `2 + 1`), so the c2 pattern generalises:

- Use a fresh `cmpN_k`, split the four owned cells, `close_full_borrow_content` and `borrow` all four, then `share_full_borrow` **all four**. S5 showed that every borrowed full_borrow must be consumed. Then `precreate_ref`/`init_ref_share` only the two selected pointers, close the ordered tuple own, and open the two fractions.
- Close `callback_four_debt` with the same four end tokens on the normal and direct-unwind paths, then `recover_four_sources`.
- This is the same checked rules and the same debt predicate with no new premise. The selected pointer is a symbolic offset that equals one share address on each path; if Redux does not equate `ptr_add_(v_base, 2+1)` with `v_base + 3`, an explicit checked case split on `c2`/`c1` is needed, not an assumption.

## Tool overlay changes required (translator, R17 c2 overlay)

`actual-sort4-c2-recovery-r17.patch` hard-codes indices 1 and 2: `index <> 1 && index <> 2` → fail, marker inventory `2`, argument-call counts per index, `left2_ref`/`right2_ref` names, a single `__vf_callback_scope2` start marker, `SORT4_ACTUAL_BODY_*_CALL_LINE` keys for 1/2 only, and the indexed six-typed-local groups for the 2 calls. A c3 step needs:

- an explicit expected call count N (3, later 5);
- an `__vf_callback_scopeN` per index;
- line keys for each call;
- per-index ref names;
- a marker inventory of N;
- `strict_relocation_insertions` = N.

Every unknown index, count or shape must still be refused. This is a new tool overlay with new manifest/profile pins, so it needs a new profile (not 87a0bfe5) and an independent review.

## Invariants and controls

- Runtime bytes and CFG are unchanged (`strip_ghost` equality); ordered operands are bound by checked equality on the receipt; no address-only or assumed bridge; no leak statement or relaxed leak check.
- Per-index negatives, as for c2: missing unselected share (must leak), missing end token, wrong ordered pair, wrong ref resource, wrong or displaced marker index, missing fourth debt token. Also an index-N+1 marker with no call (must be refused).
- Read each control by message and location in Brief, not by exit code.

## Estimate

The translator generalisation, constructor, tool-r17 checks, manifest/profile pins, review and one Cloud iteration need more than the remainder of R18's main window. They were not started in R18.
