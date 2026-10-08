# O17 callback result: narrow higher-ranked output instantiation candidate

2026-10-08. This is a proposed semantic frontend component for the pinned
VeriFast `f76012fb518703b1d98e243ac4f487f16877cfcb`, nightly 2026-09-25
and std `cd371e035c7e573760c43bf934d53e8118ee3e7d`. No hosted run of
this component is claimed. It follows the exact O17 chain S6, CFG, A1 assert,
A1 pointer transmute, A1 linkage, tuple-2 own, H2a, callback unwind and H2b.

## Actual obligation and falsifiable hypothesis

O17 run `37717092130`, commit `11d888ba8ff2231a80c759148194aa9ae6b9d30e`,
verified the checked `recover_pair` body and reached the real generic
`FnMut::call_mut`. The callback unwind arm consumed the full current two-T-cell,
F and thread post, then passed the leak check. The positive and false-normal
cases first failed on the normal arm at `verified/lib.rs(96,22-83)`: actual
`<F as FnOnce<(&'cmp T, &'cmp T)>>::Output`, expected `bool`. Both NORMAL and
readonly MIR export/decode, source identity, alias audits and refinement passed.
This is not a green full callback.

The exported MIR for that body has a `FnMut` trait clause and a matching
`FnOnce::Output = bool` projection clause, each over distinct bound regions
`'__11` and `'__12`. The 26.10 translator currently registers only projection
clauses with `bound_regions = []`; it drops this higher-ranked equality. The
hypothesis is that instantiating this one universal Boolean equality at the
actual call's concrete `'cmp` tuple type resolves the normal-arm type mismatch.
If it does not, record the exact new first failure; do not rewrite the call
result, change the contract, or widen the matcher speculatively.

## Domain, trust and exact lowering

The unchanged target is `T` and `F: FnMut(&T, &T) -> bool`, unrestricted by
`Copy`, `Freeze`, purity, comparator state change or nonpanic. Both normal and
unwind posts return the *current* values and one `T.own` per input cell, one
current `F.own`, storage, thread and type interpretations. The source real
call, signature, proof annotations, stock `FnMut` contract and direct-unwind
recovery remain unchanged.

The candidate reads compiler-origin clauses of the same body. It accepts
exactly one projection whose canonical def-id is `std::ops::FnOnce::Output`,
whose left side is `F` applied to a two-reference tuple of the same generic
`T`, whose two shared-reference regions equal two distinct bound-region IDs,
and whose RHS is `bool`. It also requires a matching exported `FnMut` trait
clause. At one actual decoded `FnMut::call_mut` with source substitutions
`F, (&T, &T)`, it matches the explicit ghost call substitutions to the same
`F,T` and a single concrete lifetime shared by both references and the method
parameter. Only then it emits the existing stock
`#register_type_projection_equality` for
`<F as FnOnce<(&'cmp T, &'cmp T)>>::Output = bool` immediately before that
call. The equality is a valid instance of the matched universal projection;
no function result is retagged or owner fabricated. The code must hold no
pending equality across calls. Zero, multiple, mismatched or absent clauses
emit nothing. The normal body must still consume all post resources through
ordinary typing and proof rules.

This adds trusted frontend interpretation of compiler-origin higher-ranked
clauses. It does not change the verifier kernel, alias/lifetime model, prelude,
stock `FnMut` specification, exporter, decoder or refiner. The old 26.09
transfer is design history only; this 26.10 patch is independently written
against the active chain. The O17 callback unwind patch is a separate
experimental semantic component and is not accepted by this proposal.

The isolated candidate is `verifast-fnmut-hrtb-26.10.patch`, SHA-256
`cff0d5ab1798227c39029a5c18d06619ce7eece928be85f4b1c9f440307f5ece`.
It changes only `vf_mir_translator.ml` after the exact O17 H2b chain. The
implementation matches the actual decoded `FnDef` substitutions as well as
the explicit ghost substitutions, performs a one-call registration directly
before the translated call, and holds no pending equality across calls. It is
**off by default**: both `SORT4_HRTB_OUTPUT=1` and an explicit comma-separated
`SORT4_HRTB_OUTPUT_TARGETS` list are required. Only named bodies activate the
component; a missing, malformed or duplicate target list fails translation.
A diagnostic
`CHALLENGE8_HRTB_CALL registered={0,1}` line records each actual FnMut call
considered under opt-in, and `CHALLENGE8_HRTB_EQ` records each registration.
The matcher requires its F/T identifiers to be declared generic parameters.
When a matching compiler clause exists, any local ghost declaration other
than a named lifetime token fails closed before proof, including a local
ghost type named `F` or `T`. This conservative rule prevents an annotation's
`IdentTypeExpr` from silently resolving to a shadowing ghost alias. It does
not certify arbitrary Rust local type scopes; that remains part of source/MIR
admission before wider application. Static forward `git apply --check`,
application, byte comparison and `git diff --check` passed in a disposable
pinned checkout. Syntax, typing, proof and regressions remain untested until
the next authorized hosted run.

## Hosted gates and decisions

First run the exact positive and false-normal callback with all O17 posts and
the prior nine-case unwind matrix. The positive must pass full normal and
unwind posts, return/leak/dead-code checks and refinement; the false-normal
case must reach and fail only its added `false` in the normal post. All four
marker admissions must still reject before proof, and false-unwind and both
duplicate-owner negatives must fail at their O17 obligations. Inspect trace
for exactly one registration before the real call and no registration on any
other call. A green callback remains component evidence, not actual sort4.

`hrtb-controls.rs` and hosted-only `hrtb_controls.py` prepare isolated
translator matcher controls with fresh NORMAL/readonly MIR, source identity,
refinement, considered-call and equality traces. They cover opt-in off,
Boolean positive, non-Boolean RHS, missing projection, wrong F, wrong T,
unequal tuple lifetimes, wrong method lifetime, non-lifetime *ghost* method
argument, local `abstract_type F/T` shadows, a duplicated source bound, a
FnOnce-only callee without matching FnMut trait, an unannotated second call and a later
body with a different output. Their `req true` contracts deliberately omit
ownership, so a trace match is **only** translator matcher evidence and does
not count as a verified function or an ownership negative. The shadow cases
must fail at the exact frontend type-scope certificate; malformed setup and
other frontend failures stay inconclusive. Rust may canonicalize away the
duplicate source bound; the runner classifies that case inconclusive unless
two projection clauses actually appear in decoded MIR. Well-typed Rust cannot
produce a non-lifetime decoded `FnMut` method substitution, so the ghost
non-lifetime control is only an adjacent AST guard; a decoded-MIR mutation
test is still needed for that exact malformed-input boundary. Full callback
and resource/post negatives remain separate gates. Existing ordinary panic
and shared-cleanup/Drop controls must keep their behavior on the combined
profile. Missing-fraction, close-token, borrow-end, half-lifetime and swapped
slot controls still gate the unwind component separately.

The existing `probe.py` nine-case callback source matrix remains unchanged.
An optional `--enable-hrtb` flag sets the two HRTB environment variables only
for each case's full verifier (and optional AST diagnostic), targeting that
case's exact function name. Export, decode and refinement stages run without
the opt-in. With the flag absent, O17 behavior is preserved.

No local builds, verifiers, extractors or research runners may execute. Static
patch applicability, hashes and document checks are the only local checks.
The owner has extended hosted CI through 11:30 UTC on 2026-10-08; the main
agent owns the one-job-at-a-time dispatch. This worker prepares files only.

## O19 hosted evidence and targeted control repair

O19 run `37746579002`, commit `a6f9d5e00cc99c06f8c49fa2e27e6a92308a1a79`,
used the production patch SHA above. The isolated `callback_positive` reached
both the unwind and normal arms after one `CHALLENGE8_HRTB_EQ` and one
registered call trace. Its checked `recover_pair`, complete current-cell and
owner posts, and final leak checks passed: `0 errors found (94 statements
verified)`. The four resource/post negatives failed at their added obligations:
false normal, false unwind, duplicate F owner, and duplicate left T owner.
The four marker admission variants failed closed before target proof. This
qualifies the *isolated callback fixture* only. It does not establish an exact
actual-sort4 call/source/MIR certificate, cleanup fidelity, or broader resource
matrix.

Twelve of fifteen HRTB matcher controls had their expected traces and decoded
clause shapes. Three remained inconclusive for control-construction reasons.
`missing_projection` had no projection *clause*, but its MIR contained an
`FnOnce::Output` type alias for the local result, which the runner had counted
as a clause. The runner now counts only `projectionTerm` entries. The
`shadowed_f` and `shadowed_t` annotations were emitted as ordinary ghost
statements and failed to parse before the scope guard. Their source now begins
a ghost declaration block with a harmless predicate followed by the same
local `abstract_type F/T`. The pinned preprocessor classifies a first-in-block
annotation beginning `pred` as `BlockDecls`; the translator merges these into
the body ghost statements traversed by the scope guard. This is a static
syntax/path correction, **not** a hosted result. The exact scope-admission
classification requires a fresh runner trace. Production HRTB patch bytes
remain unchanged.
