# R22 ghost repair: `merge_fractions` over the selected payload cell

**Defect.** Build `cfc83426` shows that positive, `no-retained-half`, `omit-selected-own` and `omit-unselected-own` all stop at `verified/lib.rs(212,14-29)`. The error is "Only predicate assertions and field-points-to assertions are supported here at this time". It comes from the transform's `merge_fractions *saved_guard.inner |-> _;`: VeriFast's `MergeFractionsStmt` (`verifast.ml:1554-1586`) accepts only `WPredAsn` or a field `WPointsTo`, and a deref points-to is neither.

**Applicability.** This one ghost statement of the owner-approved fractional candidate (`RETURNED_GUARD_HALF` in `r21_fractional_forget.py`). It occurs in all eight rows, because every control is derived from the positive.

**Change.** Replace it with `merge_fractions points_to::<*Element>(saved_guard.inner, _);`.
- In the Rust dialect, producing `*p |-> v` creates the precise chunk `points_to::<T>(p, v)`. Its input argument is `p` (`verifast1.ml:6730` `generic_points_to_symb = "points_to"`; `prelude_core.rsspec:213` `pred points_to<t>(p: *t; v: t)`).
- The new statement therefore names exactly the chunk the old one intended.
- `merge_fractions` takes no ownership the heap does not already hold. It only sums matching fractions with definitely-equal inputs and equates their outputs. With a single matching chunk (if production already auto-merged) it is a no-op.
- The following full `assert *saved_guard.inner |-> ?selected_payload` still has to be proved.

**Invariant.** The runtime source, all other ghost text, the callee contracts, the R20 repair and the control transforms are unchanged. No new predicate, lemma, axiom or ownership bridge is added. Line structure is unchanged; only columns move on line 212.

**Consequence.** The verified source of every fractional row changes, so the exact source/unit/body pins in `verifast-r21-fractional-forget-26.10.patch` (`fractional_rows`) and `FRACTIONAL-FINGERPRINT-INPUT.json` are stale. The same patch also hard-codes the old `merge_fractions *saved_guard.inner |-> _;` literal twice: in the `open_owner` certificate text and in the expected `ghost_stmts` list (review R22-merge-review.json). The proof revision must replace both and test that they byte-equal `RETURNED_GUARD_HALF`.
- This candidate runs only the mode-9 fingerprint stage, as R21 did in `c9feaf4f`, on the current tool chain: O26, branch, fractional and parser patches. No proof is attempted.
- The next candidate binds the new pins in a fractional patch revision and restores the proof stage.

**Distinguishing controls (for the later proof run).**
- Positive must pass line 212 and reach its posts.
- `no-retained-half` must fail without the retained half: the merge cannot yield a full cell, so the full assert or the release fails.
- `omit-selected-own` and `omit-unselected-own` must fail at the same-site final-select target.
- The four callee rows must keep the diagnostics observed in `cfc83426`.
