# Immutable local → compiler Drop storage: first remaining gate

AFTERNOON source-specific design, NOT IMPLEMENTED / NOT A RUNNABLE CANDIDATE.
Source279 constructor initializer is proved only in no-Drop fragment, supplied
full CURRENT payload domain. V4 fails its full FBC-close for immutable local
physical half-permissions. No current-owner/payload weakening follows.

The original actual Drop strong pre requires full self field/padding storage,
exact root geometry, source array fraction f, writable destination and current
owner list. Canonical safe Drop pre must still be generated FBC with real payload.
Compiler Drop logically owns the local and invokes destructor with exclusive
mutable self even though its Rust binding was immutable. That source-language
fact needs an explicit verified storage/provenance/permission transition; the
existing C-like ConstType half model supplies only a read-only projection.

## Why a shortcut is not a sound candidate

- Giving the addressed immutable local full writable field chunks immediately
  would bypass the existing immutable-byte enforcement; no separate readonly
  discipline has been proved equivalent.
- Returning full chunks from its existing half chunk would invent permission.
- Changing source let to let mut or stripping ConstTypeExpr changes source/model
  admission; it does not establish the original source statement's transition.
- Fractional FBC can at most prove a fractional storage fragment, not canonical
  full safe-Drop pre; full CURRENT generic foreach pool cannot simply be scaled.
- A stored pure equality for the guard's address/bytes creates no permission.
- An empty/disarmed branch in guard-own would permit canonical Drop without its
  payload. That does not solve normal forget; keep non-False fully armed own.

## Required rule/interface before implementation

Identify exact MIR Drop terminator and initialized local at source279, original
ADT/Drop/source/profile, move/storage-dead state, exclusive borrow/provenance and
all live raw/shared aliases. Establish the complete ownership authority for that
stack allocation, distinguishing the existing readonly projection from any
remaining authority. If a new representation uses escrow for unexposed permission,
its origin, one-time recovery and invalidation must be tracked from allocation;
it may not be conjured at Drop. Generic struct/local behavior stays unchanged.

Only the authorized disposal/move transition can consume the initialized local
state and produce the exact full mutable-self FBC. Retain existing byte-validity,
immutable writes, alias/provenance, field/padding and scope deallocation checks.
No postulated numeric self-versus-array separation: derive it from actual
allocation/reference state or leave it a caller premise. Actual same-source Drop
callee must prove full effect before glue summary is installed. Constructor V4's
borrow of an immutable live local is a different transition from implicit Drop.

Trust review must explain why Rust immutable binding permissions can become an
exclusive destructor borrow under the chosen alias/storage protocol. At present
we have neither a conservation derivation nor a verified escrow representation;
therefore **no full-permission semantic upgrade is justified in this checkpoint**.

## Falsifiable gates for a future separate profile

Positive exact initialization→move/Drop storage transition→canonical FBC→proved
actual Drop→completed CURRENT payload/canonical post→glue caller post; matched
assert false after each reached transition. Full return/leak/unwind/source/MIR
refinement mandatory. Negative duplicate move/Drop, reuse after storage-dead,
wrong ADT/source/callee, wrong lifetime/provenance, live conflicting readonly/raw
alias, missing field/padding, missing escrow/permission and second full physical
cell reject at their intended mechanism. Arbitrary additional generic T.own is
not the duplicate-permission oracle. Setup/header/precision failures remain INC.
Normal mem::forget must preserve the existing payload exactly once by a checked
callee/protocol; its generic consumes-own summary has no such post. No normal
credit until that is verified. Unwind restoration uses CURRENT scratch values.

Recommended next discussion: choose the narrow source-specific initialized-local
ownership representation and implicit Drop transition before coding. An isolated
constructor physical-half diagnostic would only corroborate the already traced
kernel behavior and is not a reason to spend another build. Geometry alignment
and both intervals, canonical completed payload post, actual scratch acquisition,
C1/F-frame and arbitrary-n actual merge remain independent concrete gates.

## Provisional allocation-authority representation (review target, not code)

An explicit candidate representation is a phase-indexed physical-storage escrow
separate from `<CopyOnDrop<T>>.own`: allocation-origin authority A(id,p), readonly
projection R(id,p,src,dst,len), and inaccessible remaining physical permission
E(id,p,src,dst,len). It contains NO payload owner pool; existing own remains full
CURRENT arrays/foreach. Fresh stack allocation must establish total authority
before splitting physical fractions. Since current verifier creates only half,
E cannot be introduced by a later proof annotation: allocation bookkeeping itself
would need a narrowly scoped experimental rule and a conservation proof.

The required state sequence is allocated/uninitialized → three exact field
initializations → initialized immutable local → source-linked moved/disposal
state → exclusive destructor self → terminal storage cleanup. Initialization
must update both projection/escrow value knowledge consistently; it cannot update
one half while leaving the other half with stale values. An exclusive Drop event
consumes R and E once, derives full same-value fields/padding/FBC, and forbids old
local reads/second move/second Drop. End-of-scope handling consumes the exact
remaining storage authority, with no residual escrow leak or coefficient reset.

R/E alone do not establish lifetime exclusivity: any live shared/raw alias with
conflicting bytes permission blocks reclamation. Rust immutable-binding source
checks must remain active before disposal; full writable rights may only be
exposed after the verified move/Drop transition. The actual Drop's field/array
post and effect must restore the appropriate terminal storage protocol rather
than granting full mutable local access again. Ghost code cannot forge A/E or
advance state; immutable writes, duplicate token, duplicate physical-cell, stale
value and use-after-move controls must reject. Generic T.own need not be unique.

This is an implementation contract to assess, not a soundness conclusion. Exact
allocation/deallocation primitive linkage, field initialization interference,
raw provenance/lifetime exclusivity and scope cleanup remain to be proved. If
those cannot be expressed without a broad model rewrite, reject this candidate
and retain the conditional results. It supplies no self/array numeric interval
axiom, no callback frame and no full profile acceptance. Compiler MIR evidence
must determine the actual move/Drop transition before any summary is installed.
