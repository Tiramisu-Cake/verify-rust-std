# Actual `sort4_stable`: first comparison recovery boundary

This is a design checkpoint, not an active verifier patch or a proof result.
O16 (`37715395739`) verified the checked four-cell split, two stock shared
borrows, reference creation, and tuple `Args.own` through the first actual
`FnMut::call_mut` in `sort4_stable`. Its direct `Continue` unwind then failed
the unchanged source-array/`T.own` unwind post: the first two cells are still
borrowed. The diagnostic's normal destination post remains partial; this
note does not promote that result to a sort4 safety or ordering theorem.

## Source and typed-MIR fact to preserve

The runtime first call is `is_less(&*v_base.add(1), &*v_base)`, immediately
followed by the second comparison. The O16 typed-MIR export has five
`std::ops::FnMut::call_mut` calls, 50 basic blocks, no cleanup blocks, and a
direct `Continue` unwind at the first call. Its only `ghostDeclBlocks` entry
starts at the `let_lft 'cmp = cmp_k` at verified line 88 and ends at the
original unsafe-block close brace at line 140. The first call has normal
successor 2 and consumes the tuple assembled from its two source references.
Before admission, audit the complete NORMAL and readonly call operands back
to `v_base+1` and `v_base`, their provenance and permissions, all five call
sites, every successor, and every unwind action. The O16 graph inventory is
still labeled `UNREVIEWED_COMPLETE_GRAPH_CAPTURE`; a summary count alone
is not a source/MIR certificate.

A direct read of O16 readonly blocks 0–1 supports the first operand chain:
`_10 = copy _1` (the `v_base` input), followed by
`std::ptr::const_ptr::<impl *const T>::add(_10, 1)` into `_9`; the block-1
reference construction feeds the tuple's first field `_7`. The second field
`_11` follows a shared dereference of `_1`. The two fields are moved into
tuple `_6`, which, with the mutable comparator reference `_5` from input
`_3`, is passed to the first `FnMut::call_mut`. This is a manual local trace,
not yet a complete machine-checked graph admission gate.

The exporter recognizes `let_lft` as a ghost declaration block only at the
start of a **real Rust block**. Inserting ghost-only braces between the two
calls cannot shorten this scope. A real Rust brace would change the exact
runtime source bytes and is outside the authorized exact-body route. Moving
`let_lft` after other ghost statements already failed parsing in O15. The
existing entire-unsafe-block lifetime therefore cannot be ended after the
first call by source annotations alone on the stock frontend.

## Candidate semantics and trust boundary

The earlier experimental `verifast-end-lft-binding.patch` gives an explicit
`//@ end_lft_binding::<'cmp>();` cut before the Rust closing brace. Its
translator relocates the block end to the marker and treats the original
brace marker as a no-op; its kernel change strictly checks for surviving
`'cmp`-typed heap chunks and rebases outer type-parameter bound metadata on
all normal, return, and outgoing-goto exits. It was accepted only on a pinned
26.09 profile and insertion fixture. It cannot be treated as an accepted
26.10 component or applied by hash substitution. Porting it would add a new
trusted translator **and kernel** semantic component, requiring fresh
before-review, source/MIR admission, compatibility review with the current
callback/tuple patches, and hosted positive/negative regressions. A narrower
26.10 implementation with the same strict exit property may be preferable.

For the first call, the desired normal sequence is: use the stock FnMut
normal post; close the exact two-reference `comparison_debt` from the
`ref_initialized` fractions and borrow-end tokens; cut `'cmp` at a unique
marker before `c2`; recover the reserved lifetime half; run the checked
`recover_pair` steps (`close_frac_borrow`, `end_lifetime`, both `borrow_end`,
both `open_full_borrow_content`); and run a checked `join_four_owned_cells`
lemma to restore `v_base[..4] |-> current_values` with exactly one current
`T.own` for each value. The untouched third and fourth cells and owners are
framed from the verified split. The recovered values may reflect comparator
interior mutation; no equality with input values is assumed.

The direct unwind must execute the source-written debt close, exit the exact
shortened lifetime scope, execute the **same checked** recovery and join, and
then perform the original `ReturnStmt(unwinding())`. It may not execute `c2`
or any normal-only Rust operation. The fixture-only callback hook currently
matches only `callback_positive`/`callback_false_post` and appends its epilog
after their real block. Extending it to `sort4_stable` needs a separate exact
first-call certificate, a source-written recovery marker and debt, and an AST
check that the synthetic unwind goto crosses only the ghost lifetime scope,
preserves any reachable real cleanup/Drop, and returns through the original
unwind action. Its current name-based fixture admission is insufficient.
Source-written normal and synthetic unwind sequences must be checked against
one another; neither may fabricate `T.own`, `F.own`, references, tokens, or
cells. The remaining comparisons need independent repetitions of this
protocol with aliases resolved from their pointer choices.

## Falsifiable hosted gates before acceptance

First capture the complete new source and MIR after adding only ghost
annotations. Require exact ghost-stripped runtime body/signature, original
source hash, NORMAL/readonly export and refinement, all five call identities,
first-call operand alias/provenance, no lost or new cleanup paths, and a unique
cut/debt marker at the intended source coordinates. Run the checked recovery
and join lemmas independently with false owner/value post controls. On the
combined path, require full VF exit 0 for the first-call normal and unwind
continuations, exact trace order at the cut, original return/leak/dead-code
checks, and unchanged full unwind post. A missing fraction, reserved lifetime
half, borrow-end token, source cell, wrong pointer, duplicate token, moved or
duplicate cut, ghost use after cut, and second lifetime end must fail at their
intended obligations. Ordinary `FnMut`, direct unwind, non-Continue unwind,
and shared-cleanup/Drop controls must remain unchanged outside this admitted
source shape. If the cut or unwind goto skips a Rust cleanup, the candidate
is rejected regardless of proof success.

Until all of those gates pass, the current result is only a verified prefix
to the first callback in the positive-size, non-ZST diagnostic domain.
