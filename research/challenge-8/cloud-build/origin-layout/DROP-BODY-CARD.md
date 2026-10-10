# Concrete source-linked one-cell Drop body diagnostic

Status: c451ed14 saved diagnostic replay corrected; two new probes not run; no actual-callee credit.
Profile: `experimental-merge-origin-layout-concrete-u64-v1`, tool `8cb0121b03a5164495bf0d7c6c236ea9504d5ce4`.

## Obligation and scope

The pinned `smallsort.rs` block at lines 295–309 declares the private three-field
`CopyOnDrop<T>` and its `Drop::drop`, whose body copies `self.len` current source
elements to `self.dst`. The bounded consumer is the one-cell guard at line 551
in `insert_tail`, with `T = u64`. This diagnostic mechanically substitutes `T`
with `u64` in the exact extracted block and in both original and verified case
files. It is a **source-linked specialization**, not a compiler-generated
monomorphic MIR instance. It cannot establish an actual callee, compiler glue,
generic safety, a comparator frame, or full `insert_tail`.

The direct control retains the historical full count-n `req`, normal `ens` and
`on_unwind_ens false` byte-for-byte except for mechanical type substitution.
Its inherited `safety_proof` still opens generated FBC/default own and now
executes the required checked `call()`; any
prototype-compatibility failure is retained. Even if its runtime body reaches
the copy and return, a separate compatibility error keeps the whole case
INCONCLUSIVE. A conditional-body label requires complete verifier success and
return/leak gates.
The canonical cases retain the generated safe-Drop FBC precondition and the
generated normal/unwind postcondition, including their compatibility and leak
checks. AST admission checks both generated outcome arms separately: each must
return the exact `src`, `dst`, `len` fields, padding and thread token, with no
completed payload inserted. Ghost `safety_proof` opens FBC and `own`, checks the existing root and
src/dst geometry, then executes `call()`. A `first_body_false` case may count
only if the real method body is reached; a `prototype_false` case tests the
canonical prototype immediately after opening FBC/own. Runtime copy operands
and dynamic `self.len` stay unchanged.

The one-cell `own` carries an existing quarter source share, an uninitialized
destination and the CURRENT u64 value. Both the historical direct contract's
`dst[..len] |-> _` and the `canonical_dst_pre` assertion lower through
`DummyPat` to `array_`, which permits
uninitialized elements. Its c451ed14 first failure in frozen prelude line 256
asks for the empty-tail `array_(dst + 1, 0, _)`, a singleton-to-array shape
entailment, **not** proof that destination initialization is missing. The
already observed concrete literal-one copy from an uninitialized destination
remains separate evidence. Do not assume an initialized gap, replace the
destination contract, or claim that a conditional strong-pre direct-body PASS applies to
the one-cell caller. The diagnostic does not add authority, an ownership pool,
an entry-value snapshot, or a layout premise.

## Falsifiable result and stages

The positive first checks exact source, specialization/ghost strip, qualified
MIR body and three fields, AST canonical FBC/own/prototype and dynamic copy,
export/decode/refinement, then root bounds/alignment/separation, direct strong
pre entailment, method body, canonical post, return and leak. The classifier
reports the **first** failure stage; setup/frontend/refinement/unrelated helper
failures are inconclusive. A completed direct control establishes only the
conditional specialized body on this exact profile. A canonical refusal at
destination array shape, root alignment, guard interval, or residual payload is
preserved as such, never counted as a positive or intended negative.

The six retained cases are `direct_positive`, `direct_first_body_false`,
`canonical_dst_pre`, `canonical_positive`, `prototype_false`, and
`first_body_false`. The `canonical_dst_pre` case checks the maybe-uninitialized
destination array shape immediately after opening FBC/own, so it remains informative if root layout blocks the
full canonical case. The two canonical false cases must fail at the
exact asserted location after their preceding gates. Original/verified files
must match after removing recorded ghost text; the original must match the
independently specialized pinned block. Each Cloud stage must retain its source
hash receipt. Full normal and unwind posts, dead-code, return and leak checks
remain active. `on_unwind_ens false` belongs only to the conditional Drop-body
contract and does not turn off caller unwind checking.

## Trust and layout boundary

No compiler, verifier, parser, translator, schema, prelude, kernel or std source
change is part of this diagnostic. In particular, `gen_drop_contract` and
generic `drop_in_place` remain unchanged. The current model gives the guard no
source-qualified positive byte extent or alignment. The prior generic V3b
canonical diagnostic stopped at self alignment after checked root limits. If
this concrete run stops there, a repeat without new evidence is unwarranted.
A future layout import must bind the pinned compiler/target's qualified
`CopyOnDrop<u64>` instance to the verifier's *same* `sizeof/alignof` terms;
a measured numeral or source name alone is not a proof premise. A semantic card,
independent review and affected positive/negative gates are required before
such a tool change. Proof status stays OPEN until a fresh Cloud run passes its
own exact obligations.

## Isolated c451ed14 follow-up probes (review before Cloud)

The saved c451ed14 run reports the direct body copy, return and leak with zero
verifier errors, but the initial Python AST admission incorrectly expected
three adjacent assignments; the pinned exporter interleaves exact storage-live
nodes. Saved replay must validate the three storage-live/assignment pairs and
the unique source-located MIR copy while allowing only the annotation's
source-located `VeriFast_ghost_command` in false-body cases. Mutating operand
origins, extra calls or locations must still fail admission. The six original
ghost cases and their outcomes remain fixed.

`canonical_alignment_probe` adds a seventh isolated case at the first genuine
canonical-positive frontier, `self` alignment. Immediately after the already
successful `points_to_limits::<CopyOnDrop>(self as *mut CopyOnDrop)` call, it
opens the same typed aggregate `points_to`, calls frozen `to_u8s_` and
`from_u8s_` on the same `self` pointer, and closes the same aggregate value and
fraction before the existing field binding, geometry and `call()`. The expected
positive is that the self-alignment assertion passes without a new precondition
or loss of FBC/own resources; failure at opening, lemma preconditions, value
reassembly, or canonical post is recorded at its exact first frontier. This
probe uses no layout numeral or representation declaration and makes no
compiler-qualified layout claim. It is a proof-annotation hypothesis, not a
verifier semantic change.

`canonical_dst_shape_probe` is a separate eighth case at the earlier
destination slice frontier. It invokes frozen `points_to__limits::<u64>` on
the existing `guard_dst` singleton `points_to_`, then attempts to close only
the zero-length `array_(guard_dst + 1, 0, nil)` tail after establishing its
pointer-within-limits fact from that same storage. It then closes one-cell
`array_(guard_dst, 1, cons(old_gap, nil))`, returns that array to the unchanged
target `guard_dst[..guard_len] |-> _`, and retains the inherited checked
`call()`. If endpoint limits cannot be derived, the case must stop there as
INCONCLUSIVE; no endpoint, initialized value or array segment is supplied as a
premise. Both new cases retain full generated normal/unwind posts, original
runtime copy, ghost-strip equality, source-qualified MIR/AST admission and
the parent exact validated receipt. No result is promoted by the card alone.

Freshac238e6a/eccfd6d5 admits all8source/MIR/AST/stagegates. Alignmentroundtrip derivesalignment, thenroot-source intervaldisjointness refuses lib102; no separation/layout upgrade. Destinationlimits/endpoint/emptytailpass, thenfrontendold_gap is unbound outside own predicate. Narrowfollowup: insert `assert *guard_dst |-?-> ?shape_old_gap;` before singletonclose, then useexactexistingoption `cons(shape_old_gap,nil)`. Assertion derivesfromexistingchunk withoutconsuming/newpremise; endpoint andtailunchanged. Independent reviewer approves this localized variable-binding fix before implementation. DirectstrongbodyPASS has nonvacuoushandwrittenreq; defaultguardown=false makes safeprototypecompatibility vacuous, so no canonicalcallee/glue credit.

Final fresh result1f2f9442/739b261f: option-binding fix passes destination singleton-array target. Reached call100 refuses strongreq28 positiveGuardextent, while separate alignment probe refuses root_source_disjoint102 afteralignmentpasses. DirectbodyconditionalPASS; defaultown=false safeprototypevacuous, actualcallee/gluecreditfalse. All8admissiongates and outerbindings valid, mandatorysmokespass; combinedprofile notaccepted. Sessionclosed; no new proof/semanticdelta or automaticcontinuation.
