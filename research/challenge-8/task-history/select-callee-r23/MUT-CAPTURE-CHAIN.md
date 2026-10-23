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
4. `overnight-assume-actual/prepare-actual-nine-body-mut.py` adapts the
   pinned A1 pair from its exact const-pointer source signatures to mutable
   signatures using finite inventories (four sites in transmute, three in
   assume-init) and verifies reverse substitution reproduces the complete
   original pair. It then applies the pinned R21 transform, which composes the
   pinned R20 branch-selected repair.

The older
`overnight-assume-actual/prepare-mut-owner-fractional-capture.py` remains a
separate downstream adapter for a pre-owner-projection full-unit pair. Its
writer is Cloud-gated, and it verifies the required P2 contract hash against
the exact helper contract bytes at the signature boundary. Its pure
`transform_pair` function remains useful for synthetic source tests.

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

Synthetic tests exercise the source stages on byte fixtures, including the
final R21/R20 transformation and A1 pointer specialization. They synthesize
the pinned A1 const-pointer signature/body shapes and verify all seven
specialization sites and byte-exact reverse substitution. The fingerprint
request test also uses synthetic source bytes and does not run the std source
writer locally.

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


## R23 independent-review repair

The first source candidate was NO_GO. The new nine-body source adapter now
SHA-pins the A1 source builder and specializes the exact 4 transmute and 3
assume-init pointer type sites, with typed signature/body and inverse rewrite
checks. The alternate full-unit writer requires the same pinned Cloud gate
before filesystem input/output, and requires both the explicit contract hash
and exact contract bytes at the mutable helper signature. Its recorded
contract hash is computed from those checked bytes. The formerly source-backed
request tests now construct synthetic bytes; see VALIDATION-NOTES.md. All 30
current source/provider/target-helper tests pass using synthetic inputs only.
Actual source/MIR fingerprints and proof remain absent; the repair is pending
independent delta review and stays inactive.
