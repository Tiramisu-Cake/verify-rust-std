# P2 mutable fingerprint preparation (static only)

## Defect and applicability

The existing actual-helper source writer specializes the unchanged std
`select_unpredictable<T>` body at `T = *mut Element`, but the R22 mutable-gate
inventory remains open: there is no fresh mutable typed MIR/unit/body/snapshot
binding and the translator's relevant certificates admit only
`*const Element`. A source signature alone does not establish those bindings.
This gap applies only to the separate P2 raw-pointer specialization with
unrestricted generic `Element`; it does not alter the const route or establish
a generic-`T` summary.

## Invariant

Preserve the exact std runtime body and cleanup graph, the fixture's generic
signature and contract text, ghost-strip identity, and source identity. A
future fingerprint must bind each source and decoded typed MIR object to the
same `*mut Element` specialization and exact pointer depth. Const certifiers
remain const-only. All runtime, ownership, normal/unwind, leak, refinement and
same-site controls remain required. No proof credit, translator admission, or
Network publication is produced by this preparation.

## Distinguishing controls

The new `prepare-mut-fingerprint-request.py` accepts only the exact mutable
fixture record and bytes. Its synthetic checks exercise rejection of changed
hashes, const/mut substitution, wrong pointer depth, changed cleanup/runtime
sentinels, non-pending capture state, and attempted status inflation. The
emitted request lists later Cloud outputs and source/MIR binding obligations;
those outputs remain `PENDING_CLOUD_CAPTURE` until an authorized fingerprint
Build supplies them. The adapter does not parse MIR or make translator claims.

## Next exact work

After P2 source-only preparation is independently reviewed, register/use the
authorized Cloud fingerprint route to capture original and verified source,
NORMAL and readonly typed MIR, complete unit/body records, and required
snapshot hashes. Review the actual decoded type substitutions and cleanup
graph before implementing a closed opt-in translator gate. Then run the full
positive and refusal matrix in its authorized lane. Keep
`P2-INTERFACE.json.status` at `NOT_PUBLISHED` until all publication criteria
in `../select-callee-r22/NETWORK-P2-RESPONSE.md` have been met.

## Local artifact boundary

`overnight-helper/prepare-mut-fingerprint-request.py` and its synthetic test
are static source-contract tooling only. No rustc, Cargo, exporter, MIR
decoder, verifier, Cloud service, or proof runner is invoked by them.
