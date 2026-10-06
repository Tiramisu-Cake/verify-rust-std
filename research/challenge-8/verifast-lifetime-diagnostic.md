# Insertion comparison lifetime recovery

This records a source-level limitation of the current normal-path proof
strategy, not an Actions-confirmed failure before tail.read or a SmallSort
counterexample.
VeriFast source is pinned to `809de4596839b739dd999f9e462242c835e3af46`.
Run37406214235 reached tuple2 ownership folding, both actual reference
expressions and actual FnMut preconditions. Its first failure is the
comparator unwind branch's resource leak, before normal tail.read is reached.

The actual `insert_tail` unsafe block contains both the initial comparison and
the subsequent `tail.read()` (smallsort.rs:543-555). The proof binds
`let_lft 'cmp = cmp_k` in that block. `src/verifast.ml:2629-2675` reserves half
the lifetime token until the containing Rust block's normal/return continuation.
This reservation was separately localized by checked token assertions in
Actions run37399825118 and earlier lifetime diagnostics; see README chronology.

The remaining half can support the two references using quarter-token accesses.
After the call, closing both reference-initialization chunks and invoking
`close_frac_borrow` returns those two quarter shares
(`bin/rust/rust_belt/lifetime_logic.rsspec:275-283`). That recovers only half a token.
`end_lifetime` requires the full token (lines76-79), then `borrow_end` requires
the resulting dead token and each borrow-end token (lines122-125). Only this
route recovers the borrowed full content: points-to and generic `T.own`
(`bin/rust/rust_belt/general.rsspec:198-204`). `share_full_borrow` has already consumed
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

## First actual comparator unwind obligation

In run37406214235 at source45487efb5c9fda8ed4aa32d848dd179d946eb83c,
`Executing return statement` maps to the call at verified line103, not source
`return;`104. `vf_mir_translator.ml:2473-2483` translates
UnwindAction::Continue to `ReturnStmt(unwinding())`; lines2552-2573 branch
FnCallOutcome into returning/unwinding. Missing on_unwind_ens defaults to emp
(`rust_parser.ml:575-586`). The call precondition is satisfied, then unwind
leakcheck reports real remaining F/thread/range-prefix resources and the
half token, both open initialization fractions, close-fractional-borrow and
borrow-end tokens. No normal-path restoration or completed callback proof
follows from reaching this continuation.

FnMut consumes Args.own but leaves each reference-initialization fraction
with the caller: close_ref_own needs thread_token and persistent T.share,
not ref_initialized (general.rsspec:194-196); actual create_ref consumes and
returns its initialization fraction (aliasing.rsspec:87-90). Each fractional
borrow also retains its matching close token. Closing those two accesses can
restore the other half. Executing such ghost cleanup only after the normal
call would leave the synthetic unwind branch untreated. The next diagnostic
must specify and recover or explicitly return genuine unwind resources;
ignoring unwind, discarding chunks or an opaque restoration lemma is invalid.
