# Experimental FnMut higher-ranked output projection

This experiment patches only the pinned VeriFast MIR translator at
`src/rust_frontend/vf_mir_translator/vf_mir_translator.ml`. The upstream source
commit remains `809de4596839b739dd999f9e462242c835e3af46`; the unmodified
translator file has SHA-256
`7319d2638c3fc49a1663b50925d565ca2e10d95754933ed58e37f27239936803`.
The patch is [verifast-fnmut-hrtb.patch](verifast-fnmut-hrtb.patch), SHA-256
`c35c4b438563f5a9da0f79c658ac7450ca429c91ed91207f6caa1ee267d09758`.
This is an experimental source-built verifier, not the pinned release binary.

The [compiler MIR evidence](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37408278446)
exports the actual `smallsort::insert_tail` predicates as follows:

- `for<'__23, '__24> F: core::ops::FnMut<(&'__23 T, &'__24 T)>`;
- `for<'__23, '__24> <F as core::ops::FnOnce<(&'__23 T, &'__24 T)>>::Output = bool`.

The same exported call is `core::ops::FnMut::call_mut` with substitutions
`[F, (&'<erased> T, &'<erased> T)]` and one method lifetime. The ghost
substitutions at that actual call are
`[F, (&'cmp T, &'cmp T), 'cmp]`. The release translator registers
non-higher-ranked projection equalities at function entry but filters out
projections with nonempty `boundRegions`. Consequently the verified call
currently reaches its actual result and fails type checking because its
`FnOnce::Output` has not been resolved to `bool`.

The patch records only a two-bound-region, shared-reference tuple projection
whose exported right-hand side is `bool` and whose matching `FnMut` trait
predicate is also exported by rustc. At a matching `FnMut::call_mut`, it
checks the MIR substitution's `F` and both referent `T` parameters against
the ghost substitution, requires both ghost reference lifetimes and the method
lifetime to be the same explicit lifetime, and requires exactly one matching
projection. It then uses VeriFast's existing
`#register_type_projection_equality` immediately before that call. This is
the particular `'__23 := 'cmp, '__24 := 'cmp` instance of the compiler's
universal predicate; it does not rewrite the call's return type from the
expected destination type. A missing, different, or ambiguous predicate emits
no equality. The bound list is scoped to one body and the pending equality is
reset for each call, so nonmatching calls retain their original behavior.

The resulting equality is true for both normal and unwind branches. The patch
does not alter Rust source, generic signatures, memory contracts, verifier
assumptions, unwind checking, or the tuple ownership parser experiment. It
does not establish `insert_tail` safety: after this type issue, the existing
comparison-borrow lifetime and later move/Drop obligations still need proofs.

Acceptance on GitHub-hosted Actions:

1. Build the pinned source with this one patch and the separately recorded
   tuple parser patch; retain source/input hashes, build log, and binary hash.
2. Run the source-exact `insert_tail` range probe with normal and unwind
   checking enabled. Require refinement success and evidence that the verifier
   passes the comparator result type and reaches the next real body obligation.
3. Check that a call with no matching exported projection, a different
   projection result, mismatched `F` or referent type, unmatched bound regions,
   or an ambiguous projection does not gain a `bool` equality. A comparator
   with a genuine non-Boolean output is a useful negative regression. Keep
   source-level body and signature fidelity checks in every probe.

Only static patch applicability and whitespace checks were performed locally.
No verifier, compiler, or executable test ran on the user's server.
