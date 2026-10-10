# Bounded native/c1 composition: strict-lifetime dependency

Decision at 2026-10-10 01:43 UTC: stop semantic implementation in the assigned
experimental frontend profile. Build4 is a source/MIR/pre-overlay-AST capture,
not a proof. The independent fresh review is
[`FRONTEND-FRESH-REVIEW.md`](FRONTEND-FRESH-REVIEW.md) and rejects both a
translator-only callback splice and treating the source
`end_lft_binding::<'cmp>()` command as `Noop`.

## Exact chain mismatch

Build4 `0904f144-a6dd-4ebe-b57c-79c2e2dc3433`, pinned proof/infra commit
`fa4c46d3955c59f4af6ce01e719864dd9894f083`, used the source- and
MIR-preserving capture translator SHA256
`4dc5f332d4c813fee966ef0724aa1f8ce0e6578ff1e15a0cb61bfb9719c6d14e`
and unchanged production `src/verifast.ml` SHA256
`adbf2c3de02cba7fbdb0b8e203a864e34c1b2ab16de4f6b153477106dbba04d0`.
The base production translator before capture was
`4d3a190fcec695415b41162ddf8d71aec6e2826d2b69e7692df306a568add98c`.
The capture hook checks the environment variable `SORT4_STRICT_LFT_CUT`, but
the production translator and verifier contain **no active implementation**
of `#strict_lft_binding_scope` or a strict lifetime-cut escape check. The
Build4 complete original helper AST hash is
`64c01593d890907756c2e707e09adb9da80c6a1d0967a6720d2200defacf8b06`;
its `'cmp` block closes lexically at source line 203 and still contains the
undefined `end_lft_binding::<'cmp>()` marker at line 202. Full VF first refuses
earlier at the deliberately unknown callback marker line 189, so it never
tests the lifetime marker or native entry.

The previous isolated experimental tool `/root/verifast-select-sort4-native-20261010`
has translator SHA256
`8e467ca535bfcead8555a717897ec0355261ee8ccb011f98441e2dba80b5984f`
and `src/verifast.ml` SHA256
`37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`.
Its historical strict-cut component is
[`verifast-strict-lft-cut-26.10.patch`](../../overnight-lifetime/verifast-strict-lft-cut-26.10.patch),
SHA256 `d557082b0c17771acd7386ad6caca7bc139877cf1ca513d9570da210b1b542d8`.
The old isolated worktree includes other experimental changes; these two
whole-file hashes identify it for comparison, **not** as an admissible patch
to copy wholesale. The historical strict component marks the scoped block
with `#strict_lft_binding_scope`, freezes entry outer type and bound metadata,
checks live heap type arguments and outer local/type/bound escapes on normal,
return and goto exits, avoids silently discarding scoped chunks, and preserves
heap terms while rebasing only entry outer bounds. Its implementation changes
both the translator and `src/verifast.ml`. The present `tool_overlays`
mechanism deliberately accepts translator-only deltas and freezes
`src/verifast.ml`; it cannot carry this dependency without a new trust/profile
decision.

## Why this stops the attempted splice

The helper's captured Func retains full normal and direct-unwind CURRENT
posts, and paired MIR identifies the one source-line-199 FnMut F/(&T,&T)
comparison with source cells 1 then 0. Its source-written marker has a debt
close within `'cmp`, followed by pair/four-cell/full-array recovery and T/F
leaks intended **after** lifetime exit. The AST splice cannot establish that
boundary merely by moving the eight callback temporaries and routing the
unwind clause to an outer epilogue. Stock lexical `BlockStmt` ends the type
name and frees locals, but does not perform the missing strict heap/outer-type
escape check. Translating the source marker to `Noop` would delete the
obligation; emitting only a translator marker without verifier support would
be undefined. Neither is an admissible proof path. The uninitialized tuple
temporary can allocate storage at its declaration, so a later proposed move
of all eight temporaries also needs an exact all-path allocation/free audit.

This session's authorized scope permits narrow frontend/internal helper work
but preserves the frozen verifier semantics and does not authorize a new
`src/verifast.ml` rule. No semantic overlay was written in
`/root/verifast-select-native-compose-20261010`; the capture-only patch remains
instrumentation. The bounded helper, native caller and actual std caller CFG
are **not proved** by Build4.

## Future decision and affected gates

A future separately authorized strict-cut profile would first need an exact
production-base delta, rationale and independent trust review, including the
heap/type/bound escape rule on normal, return, unwind and outgoing-goto paths,
the callback-local allocation/free correspondence, and the exact existing
pointer-add intrinsic lowering. It would need a **fresh** source/MIR/pre-overlay
AST capture under that patched chain before any callback splice, since
Build4's AST fingerprint belongs to a different semantic profile. Required
Cloud gates include default-off unchanged behavior; helper and native full
normal/direct-unwind posts and leak checks; a live `'cmp` heap chunk negative;
outer local/bound metadata escape negatives; missing debt and missing owner
negatives at their intended obligations; wrong cut/goto and duplicate token
negatives; paired normal/readonly MIR/refinement/source pins; and regression
of the existing C1/C2 mandatory refusals. A green verifier count alone
cannot admit a changed verifier rule. Until that decision, the project may
continue the independent, already-reviewed C2-bound prefix work without
claiming native/c1 composition.
