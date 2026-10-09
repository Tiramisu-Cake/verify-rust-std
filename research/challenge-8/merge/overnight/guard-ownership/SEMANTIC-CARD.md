# CopyOnDrop payload-own transition, DAY merge

Status: prepared diagnostic; no Cloud result or caller theorem. This card precedes
the candidate implementation. It uses the existing pinned stock-26.10 and
experimental six-component tool homes from the a643 direct-Drop run. It adds
only source annotations to an exact extraction of the repository's unchanged
`CopyOnDrop` struct and `Drop::drop` body. It changes no parser, translator,
kernel, prelude, runtime Rust, copy summary, or refinement rule.

## Actual obligation and falsifiable hypothesis

`smallsort.rs:295-307` defines the private guard and its full-length copy. The
source site at `:279` constructs that guard after filling scratch, `:286` calls
the merge, and `:291` forgets it on normal return. The nearest testable claim is
that an explicit, **nonempty** `CopyOnDrop.own(t, v)` can carry one existing
source owner pool and a writable destination range into the generated
`CopyOnDrop_full_borrow_content`, and that the actual Drop prototype's
`safety_proof` can open that FBC to discharge the already checked strong direct
body precondition. `own` is a predicate over the **by-value** three-field
initializer; it cannot mention the address of the guard object. Its payload is
`[?f]v.src[..v.len] |-> ?values`, `v.dst[..v.len] |-> _`, and
`foreach(values, own::<T>(t))`, plus all original pure source/destination
geometry and positive stride. It does not create T ownership from copied bytes,
sharing, or addresses.

The strong direct Drop pre and full normal post from the a643 case stay byte
for byte, including guard-object geometry and separation, count-n current
source values/owners, destination bytes, and unwind `false`. The generated FBC
continues to supply the three fields and padding. The one genuine uncertainty
is whether the original **guard-self** nonnull/alignment/object-limit and
guard/source/destination disjoint inequalities follow in this frozen model from
the FBC field/padding chunks separated from nonempty array resources. None of
these facts can be hidden inside by-value `own`. Failure to derive them is an
architectural OPEN result, not permission to delete an original precondition.

Domain: exactly the existing direct generic Drop diagnostic's positive-size T,
count-n, valid aligned disjoint initialized source, writable destination and
thread-owned current values. This is conditional on a supplied owner pool; it
does not claim public caller, ZST, arbitrary comparator frame, construction,
normal forget, or compiler drop-glue applicability. All original direct-body
normal/unwind posts remain required. The prototype must have a real non-False
own body and reach the direct pre without an `assume`.

## Controls, stage, and decision

The positive must pass source hash admission, MIR export/decode, AST admission,
VeriFast prototype and actual body, refinement, return/leak/dead-code checks.
Inspect the AST for the custom `TypePredDef`, generated FBC, and actual prototype
`safety_proof`; inspect the full log for both prototype and actual body. An
`assert false` immediately after opening the own payload in `safety_proof`
must reject there **after** FBC/own admission and before actual runtime body.
A matched first-runtime-body `assert false` must reject at that exact body
location after a successful prototype. A third case omits the array/owner
payload from `own` while preserving pure geometry. Its first Cloud run is
calibration only: the exact missing-chunk error predicate and coordinates must
be recorded before a later run can count it as an intended negative. Frontend,
setup, unexpected geometry, timeout, or unrelated failures give no
intended-negative credit. Negatives do not prove a positive theorem.

A separate construction witness copies the exact runtime statement at
`smallsort.rs:279` into an isolated function, with the original three-field
guard and actual Drop body in the same source. It fixes `2 <= len`, matching
the branch that reaches that physical construction in the caller. Its explicit pre **supplies**
the initialized source array, each existing T owner once, writable destination,
and all value-only geometry. Its post requires the non-False guard `own` with
identical `src`, `dst`, and `len`; source stripping preserves wrapper runtime
bytes and the exact statement is matched to the repository source line.
Constructor verification is conditional evidence for that physical statement,
not evidence that the enclosing caller has established the supplied pre.

If positive, matched controls, and constructor witness pass, the next separately
checked task is to derive the witness pre from the actual enclosing caller. That
site must prove a single transfer into `own`; it cannot mint owners. The
ordinary `mem::forget` path and compiler drop glue remain OPEN even after this
positive.
If guard geometry is not derivable from generated FBC, checkpoint its exact
predicate/location and preserve full logs. Reassess within the authorized phase
before a justified independent next step. Repeated payload edits without new
evidence do not advance this diagnostic.

## Self-review before hosted execution

This profile is annotation-only and separately named; original and verified
Rust strip to identical bytes. The existing a643 direct-body contract is pinned
as an immutable input. The candidate's payload is resource-bearing, so normal
`forget` would consume it and needs a later ownership handoff proof. No source
owner appears twice. The source/destination arrays remain separate chunks and
their values are the current values at the copy. The uncertain self geometry is
stated explicitly above. A passing microfixture would prove only its stated
conditional prototype/direct-callee bridge under the frozen experimental
profile; it would not establish tool admissibility, caller restoration, or
generic drop glue.
