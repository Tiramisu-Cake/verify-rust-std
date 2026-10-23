# Next obligation: function-end leak of two pointer-value ownership chunks

**Evidence.** Build `7e23e945` (candidate `dbaf41e6`, fresh fractional pins), positive row; see `FRACTIONAL-PROOF-LEAK-EVIDENCE.json`.
- With the fresh pins, every row is admitted; there is no certificate refusal.
- The positive passes the checked half-owner callee, the repaired `merge_fractions` (line 212), the full payload assert (213), and the final wrapper-select and `assume_init` calls (228).
- It fails only the leak check at `verified/lib.rs(230,1-2)`: `MaybeUninit_pointer_own(Element_typeid)(t, __result0)` and `(t, __result)`.
- The normal post produced no diagnostic before the leak check. It is still UNVERIFIED as a whole, because the run did not complete.

**What leaks.**
- `std::mem::MaybeUninit_pointer_own<Element>` (`lib.rsspec:440`) is a checked definitional predicate with no pointee permission: `none => true`, `some(p) => raw_ptr_own(t, p)`, where `raw_ptr_own` = `true` (`general.rsspec:109`).
- The checked local constructor `sort4_checked_maybeuninit_new` ensures `MaybeUninit_pointer_own(t, result)` (translator text, applied line 422). The symbolic names `__result`/`__result0` are the shape of call results.
- The R20 branch-selected repair and the owner projection close fresh `MaybeUninit_pointer_own(t, MaybeUninit::new(payload))` chunks for the wrapper select through `close_MaybeUninit_pointer_own` (req `true`).
- Working hypothesis (UNVERIFIED until the exact source lines are bound): the two leaked chunks are the constructor results, which are never consumed.

**Admissible repair directions.** Both are ghost-only and checked. Neither relaxes the leak check or adds a lemma, axiom or trusted step.

1. **Consume the constructor chunks by exact value.**
   - Open them with checked `open` statements: open `MaybeUninit_pointer_own`, then a `match` on `MaybeUninit::inner` that opens `raw_ptr_own`.
   - Bind to the exact constructor-result values, not a free pattern. While the re-closed wrapper chunks are live, a free `?w` pattern is ambiguous.
   - First bind the source lines and locals of the two `MaybeUninit::new` calls from the captured nine-body `verified/lib.rs`.
   - Precedent for open-old/close-current: `overnight-assume-actual/prepare-wrapper-rebase.py`.
2. **Reuse instead of re-close.** Make the wrapper ghosts consume the constructor chunks instead of closing fresh ones. This edits the reviewed R20 repair text and its pinned certificates, so it is a larger delta. Prefer 1 unless 1 cannot bind exact values.

**Costs (same pipeline as R22).**
1. Transform edit, with SHA cascade into helper and entry.
2. Fingerprint-only Build.
3. Bounded Brief read of the new record (the R22 walker took about 420 requests and about 20 minutes).
4. New fractional patch revision (`fractional_rows`, plus any certified ghost-statement list that names the new text, in the same way as finding 1 of `R22-merge-review.json`).
5. Proof Build.

That is two Builds of about 6 minutes each, plus reviews. Plan the proof Build's full 1200s envelope inside main.

**Controls after the repair.**
- Positive: verified, with no leak.
- `no-retained-half`: still at line 213, the intended full-cell assert.
- The four callee rows: unchanged diagnostics, ready to pin. The candidate targets are in the evidence.
- `omit-selected-own`/`omit-unselected-own`: they fail at the wrapper-select lemma precondition `lib.rsspec(462/463,47-48)`, not at the verified/lib.rs final-select target the classifier expects. Before the matrix can be complete, pin that target with a review (source file, line, column and message), or show that the classifier's same-site target is wrong for this route.
- The normal/unwind/nested-Drop gates stay required.

**Static binding note (std source, `library/core/src/hint.rs` pinned `ce89716d…`).**
- The two constructor results are the shadowed locals `let mut true_val = MaybeUninit::new(true_val); let mut false_val = MaybeUninit::new(false_val);`.
- The checked `sort4_checked_as_mut_ptr` contract (`*storage |-> value &*& MaybeUninit_pointer_own(t, value)` in pre and post) hands each constructor chunk back unchanged.
- The constructor post only states `MaybeUninit::inner(result) == some(val)`, not `result == MaybeUninit::new(val)`. So the re-closed `MaybeUninit_pointer_own(t, MaybeUninit::new(payload))` chunks used by the final select are symbolically distinct from the constructor chunks, and the latter leak.
- Direction 1 can therefore name the leaked values through the storage cells' recorded values at the `open_MaybeUninit` ghost sites of the owner projection. These must be bound and reviewed on the captured source. They must not be guessed.
