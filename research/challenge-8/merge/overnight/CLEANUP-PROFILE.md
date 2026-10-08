# Callback cleanup profile — draft before hosted acceptance

Base VeriFast 26.10 `f76012fb518703b1d98e243ac4f487f16877cfcb`;
apply `wrapping.patch`, `callback.patch`, `copy.patch`, then the separately
hashed `cleanup.patch`. The latter modifies only
`src/rust_frontend/vf_mir_translator/vf_mir_translator.ml` and
`src/verifast.ml`. The exporter, decoder, refiner, Rust prelude, source std
runtime body and generic signatures are unchanged by this dependency.
Current cleanup patch SHA-256:
`4968245de17d887e840e161bd2f113e78061efbdd651488b601d32ee8bb5d1f0`.
After the full W1/M2/C1/cleanup chain, `src/verifast.ml` SHA-256 is
`100eebae92c770a0b8cd57e2639588761f881316dd522fc3b9a9b1ec6fd91cd6`;
the translator SHA-256 is
`4d25e806f58dc1b9f3b885a2717a45cfa7184822ce9de50a4c65a290ac436d8e`.

## Exact opt-in syntax

Immediately after the one actual `FnMut::call_mut` statement, emit three
whole-line ghost annotations before any selected copy or cursor update:

```rust
//@ { callback_close::<'cmp>(); close [left_ref_frac]ref_initialized_::<T>(left_ref)(); close_frac_borrow(left_ref_frac, ref_initialized_(left_ref)); close [right_ref_frac]ref_initialized_::<T>(right_ref)(); close_frac_borrow(right_ref_frac, ref_initialized_(right_ref)); }
//@ callback_scope_end::<'cmp>();
//@ { callback_recover::<'cmp>(); end_lifetime(cmp_k); borrow_end(cmp_k, <T>.full_borrow_content(t, left_src as *T)); open_full_borrow_content::<T>(t, left_src as *T); borrow_end(cmp_k, <T>.full_borrow_content(t, right_src as *T)); open_full_borrow_content::<T>(t, right_src as *T); }
```

The markers and ghost blocks use existing parser syntax. The first commands
close the actual fractional ref-initialization borrows on both call outcomes.
The middle dummy closes the uniquely matched local `let_lft 'cmp` scope while
preserving every heap chunk. The final commands run after the lifetime-token
half is returned, recovering current source values and their `T.own` resources.
The panic branch executes the same explicit commands using a proof-only Goto
past the binding, followed by the original `ReturnStmt(unwinding)`. It does not
copy, move cursors, equate values to entry snapshots or assume callback purity.
An `assert false` before the epilogue label rejects accidental normal fallthrough.

The frontend requires one compiler-origin HRTB `FnMut::call_mut` with a checked
`Output=bool` projection, a normal successor and `UnwindAction::Continue`.
It rejects unmatched/duplicate markers or calls, incorrect marker order,
unsupported cleanup actions, extra non-ghost MIR calls inside the binding,
and ghost commands beyond the source-reference protocol. The pre-cut protocol
has two full-content closes, borrows, shares, precreated references, shared-ref
initializations, fraction opens, ref-initialization opens and ref-own closes;
one tuple-2 ownership close and the callback-close block. An optional third
ref-own close exists only to expose a live `'cmp`-typed chunk to the strict
escape rejection control.

The strict kernel mode is opt-in only for the reconstructed sole-let-lifetime
block. Stock blocks retain their original behavior. The strict exit retains all
heap chunks, rejects a live binder-dependent type in chunk type arguments or
visible variables and bound metadata, restores outer lexical environments and
rebases learned outer type-parameter bounds to their entry snapshot. Physical
`cmp_k` tokens survive the binding exit for explicit `end_lifetime` and
`borrow_end`. The frontend's closed command protocol excludes arbitrary local
predicates or lemma-pointer captures; unsupported commands fail before proof.
There is no ownership introduction rule or assumed cleanup post.

## Admission and remaining evidence

Static preparation: patch applicability against the pinned W1/M2/C1 chain and
`git -c core.whitespace=cr-at-eol diff --check` passed. No compilation,
verification, extractor, or test ran locally. Hosted acceptance must inspect
the generated proof AST and exact MIR outcome edges, prove the full normal and
unwind posts on the unchanged actual callee, and keep source stripping,
refinement, leak, dead-code and native/old-Rust compatibility checks enabled.
The new `cleanup-cases.rs` supplies positive, false-unwind, mismatched fraction,
escaped typed-resource and wrong-marker controls. A setup or frontend failure
is not an intended proof negative.
