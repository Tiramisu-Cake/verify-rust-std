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

## Bound site (captured positive `verified/lib.rs` of 7e23e945)

Source: file ID `49642420…`, SHA-256 `96c929a8…`. Brief requests `5a98174fcf03`, `4b45a2679dc5`, `6c9a474fb629`, `4a11880e28ab`.

- Lines 155–156: `let mut true_val = MaybeUninit::new(true_val); let mut false_val = MaybeUninit::new(false_val);` (constructor chunks).
- Lines 173–174: `let true_ptr = true_val.as_mut_ptr(); let false_ptr = false_val.as_mut_ptr();`. The checked contract returns the cell and the same `MaybeUninit_pointer_own(t, value)`.
- Lines 175–176: owner-projection ghosts `open_MaybeUninit::<*Element>(true_ptr as *MaybeUninit<*Element>)`, then the same for false.
- Lines 177–178: `assert *true_ptr |-> ?true_payload;` and the same for false.

**Proposed candidate text.** Insert it immediately before line 175, once per side. It is not implemented and not reviewed.

```rust
/*@ assert *(true_ptr as *std::mem::MaybeUninit<*Element>) |-> ?true_wrapper; @*/
/*@ { open std::mem::MaybeUninit_pointer_own::<Element>()(t, true_wrapper);
     match std::mem::MaybeUninit::inner(true_wrapper) { none => {} some(p) => { open raw_ptr_own::<Element>()(t, p); } } } @*/
```

**Why this site.** Before `open_MaybeUninit`, the cell's value is exactly the constructor result. So the opened chunk is bound by value, not by a free pattern, and the later re-closed `MaybeUninit::new(payload)` chunks used by the final select are untouched.

**Soundness.** `open` and `match` are checked against the definitions. They only drop pointer-value ownership that holds no pointee permission. The leak check stays enabled.

**To confirm in Cloud.**
- The Rust ghost parser accepts a `match` statement inside a ghost block.
- The certified ghost-statement list of the fractional patch (`ghost_stmts` / `open_owner`) is extended for exactly these four new ghost texts.
- Line numbers shift, so all pins come from the next fingerprint.

**Translator certificates the repair must extend** (static read of `vf_mir_translator.ml` with the R22 fractional patch applied, translator `e9a953ca`). Both must change only under the existing `fractional` condition. The default and nine routes stay byte-identical.
- **Owner/nine source reconstruction** (about line 12639): the `wrappers` string. It rebuilds the expected source text around the `open_MaybeUninit` ghosts; the four new ghost texts go before it.
- **Ordered ghost list** (about line 12791): `expected_ghosts`. The new ghost statements are inserted before the two `open_MaybeUninit` entries.
- The older `Sort4SelectIntrinsic.projection_ghosts` (about line 734, `//@` form) belongs to the non-nine projection route. Check it, but it is not expected to change.

Add static tests that bind the transform text to both patch literals, as `test_fractional_patch_ghost_literals_match_transform_and_pins` already does for `merge_fractions`.

## Implemented R22b fingerprint candidate (unbuilt)

- **Transform** (`r21_fractional_forget.py`, SHA `8a23499c…`): inserts the four release ghosts after the 4-space indentation of the first `open_MaybeUninit` projection ghost, with no indentation of their own. Ghost stripping therefore keeps the runtime original byte-identical; the synthetic runtime and inversion tests check this.
- **Pin cascade:** helper `9cb4dee1…`; entry pins updated.
- **Runner:** its final stage is the mode-9 fingerprint stage, using the reviewed R22 tool chain (fractional patch `219f3dc0`, parser `dfdaff60`). Mode-9 refuses before certificate checks, so stale rows do not affect it.
- **Proof patch:** `verifast-r22b-fractional-forget-26.10.patch` (`9097d01a…`, translator `9cf03ca8…`) extends only the fractional `wrappers` reconstruction and `expected_ghosts`. Its `fractional_rows` are still the R22 values and **must** be rebound from the R22b fingerprint before any proof run. It is not on the runner yet.
