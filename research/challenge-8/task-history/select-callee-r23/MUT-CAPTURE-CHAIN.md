# Mutable P2 source chain adapter (inactive, source only)

## Defect and applicability

The standalone P2 writer produces an exact `*mut Element` fixture pair, but it
does not produce the linked full unit consumed by the nine-body owner proof.
The existing const chain reaches that unit through:

1. `prepare-actual-helper-capture.py::write_fixture`;
2. `prepare-actual-owner-linked.py::write_case`, which obtains its actual
   helper by calling the const writer;
3. `overnight-guard-actual/prepare-actual-nested-drop.py::write_case`, which
   consumes the linked owner source and adds the checked Drop adapter;
4. `overnight-assume-actual/prepare.py::write_case`, which consumes the
   seven-body source, adds A1 adapters, then inserts the saved-guard transfer;
5. the R21 fractional transform, which applies its pinned R20
   branch-selected final-select repair.

The gap applies only to the pending `T = *mut Element; Element unrestricted`
source candidate. No existing step above accepts a mutable fixture directory:
the owner-linked writer calls the const capture writer, and the seven/nine
body writers call that owner-linked route. This identified the gap addressed
by the separate mutable route below.

## Parallel source preparation

The inactive source-generation route is now parallel at each source stage:

1. `overnight-helper/prepare-actual-helper-capture-mut-parallel.py` extracts
   the exact pinned generic std body directly and makes the mutable fixture.
   It never imports/calls the const fixture writer and is gated by the pinned
   Cloud provider identity.
2. `overnight-helper/prepare-actual-owner-linked-mut.py` uses that mutable
   fixture, builds the S6 constructor/as-mut-pointer/drop source linkage, and
   rewrites each generated component under fixed inventories: two type sites
   in the constructor module, three in `as_mut_ptr`, and one in pointer-drop.
   It rejects unsupported pointer shapes, preserves the exact actual body,
   then runs the owner projection. It imports the specific source builders;
   it does not import the linkage wrapper that loads the const fixture writer.
3. `overnight-guard-actual/prepare-actual-nested-drop-mut.py` adds the
   generic checked Drop method and owner-preserving forget source, with the
   saved-guard transfer.
4. `overnight-assume-actual/prepare-actual-nine-body-mut.py` adds the generic
   A1 adapter pair, then applies the pinned R21 transform, which composes the
   pinned R20 branch-selected repair.

The older
`overnight-assume-actual/prepare-mut-owner-fractional-capture.py` remains a
downstream adapter for a separately prepared pre-owner-projection full-unit
pair. The new full route does not depend on it.

Every mutable source record says typed MIR is unbound, admission is absent,
proof was not run, publication is not allowed, and credit is zero. Shared S6
source certificates and generated const-specific adapter literals are stored
only as source-generation inputs; the post-rewrite source has no const
`Element` spelling, and none of those source records is accepted as a mutable
typed certificate. The owner-linked writer pins the mutable parallel fixture
writer and does not load `prepare-actual-helper-capture.py`.

The final route preserves the exact std body and checks ghost-strip identity,
call counts, pointer type spellings, and each insertion boundary. It retains
the existing normal/unwind, ownership, leak, refinement, and same-site source
controls. It adds no translator rule and does not establish any typed MIR
fact.

The paired synthetic test exercises the source stages on small byte fixtures,
including the final R21/R20 transformation. It confirms the source-generation
transforms produce identical const/mut annotations modulo the fixture
signature in a separate comparison, and rejects const substitution, wrong
pointer depth, source/hash drift, and missing anchors.

## Remaining gate

No actual std source preparation was run locally. The four writer stages use
`provider.py::require_supported_provider`, require the coordinator's real
`SMALLSORT_EXECUTION_PROVIDER=cloud-build` identity, and reject GitHub identity.
The transitive source functions are pure source builders; no GitHub-only CLI
entrypoint is invoked. Synthetic provider controls cover missing/wrong
provider, GitHub identity, missing Cloud build ID, and a valid mocked Cloud
record. The source identities are ready for an authorized Cloud source-only
invocation; its output must then be fingerprinted on the authorized Cloud route. Fresh
NORMAL/readonly typed MIR, full unit and nine body hashes, snapshots, ordered
ghost pins, cleanup graph, and mutable-specific translator gates remain
mandatory. The source route itself supplies none of these. Until the complete
mutable positive and refusal matrix is accepted and independently reviewed,
keep `P2-INTERFACE.json` at `NOT_PUBLISHED`.

The adapter at
`overnight-assume-actual/prepare-mut-owner-fractional-capture.py` accepts a
pre-owner-projection unit only and is retained for the alternate route; it is
not the new route's entry point.

## Prior localized blocker

Before these parallel source adapters, the identified gap was that the
existing `prepare-actual-owner-linked.py` called the const fixture writer,
and nested-drop/nine-body writers consumed that result. The current parallel
chain removes that dependency for source generation; its generated adapter
text still requires fresh mutable MIR binding and proof.

