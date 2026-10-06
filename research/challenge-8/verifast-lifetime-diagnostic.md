# Insertion comparison lifetime recovery

This records a source-level limitation of the current proof strategy, not an
Actions-confirmed failure after the comparison or a SmallSort counterexample.
VeriFast source is pinned to `809de4596839b739dd999f9e462242c835e3af46`.
The tuple2 parser diagnostic must first reach the actual `FnMut` call.

The actual `insert_tail` unsafe block contains both the initial comparison and
the subsequent `tail.read()` (smallsort.rs:543-555). The proof binds
`let_lft 'cmp = cmp_k` in that block. `src/verifast.ml:2629-2675` reserves half
the lifetime token until the containing Rust block's normal/return continuation.
This reservation was separately localized by checked token assertions in
Actions run37399825118 and earlier lifetime diagnostics; see README chronology.

The remaining half can support the two references using quarter-token accesses.
After the call, closing both reference-initialization chunks and invoking
`close_frac_borrow` returns those two quarter shares
(`bin/rust/lifetime_logic.rsspec:275-283`). That recovers only half a token.
`end_lifetime` requires the full token (lines76-79), then `borrow_end` requires
the resulting dead token and each borrow-end token (lines122-125). Only this
route recovers the borrowed full content: points-to and generic `T.own`
(`bin/rust/general.rsspec:198-204`). `share_full_borrow` has already consumed
the full-borrow chunks (lines225-228), so they cannot simply be opened early.

There is no supported ghost command that ends a `let_lft` binding before Rust
block exit. `docs/rust-reference/src/func-body-annots.md:1-40` explains that
each ghost annotation becomes one dummy Rust statement; a ghost block cannot
surround the following real comparison and shorten its lifetime scope.
The documented technique uses a nested real Rust block, then calls
`end_lifetime` after that block (`lifetime-logic.md:90-107,185-197`). Adding
such a Rust block here would violate the experiment's exact-source constraint.

The readonly reference shortcut applies to ordinary points-to resources, not
arbitrary generic `T.share` with interior mutability. It cannot replace the
required generic ownership reasoning. Treating shared resources as exclusive,
assuming a token, or adding an unproved ownership bridge is not a valid fix.

Next determine the actual post-comparison failure in Actions. If it agrees
with this audit, investigate a verifier feature that explicitly ends a ghost
lifetime binding and checks resource validity, or a different sound borrowing
strategy. A verifier-source enhancement needs its own review and evidence;
it is outside the tuple2 parser patch. Comparator unwind and early-return
restoration remain separate obligations, even with the current weak `ens true`.
