# Independent review: imported selector dead-code diagnostics

**Finding: the C2 consumer failure is a dead-code accounting mismatch in the
serialized AST transport, not an observed semantic failure in the selector
bodies.** The evidence supports one narrow transport repair candidate before
any implementation. This review ran no compiler, verifier, extractor, or
Cloud job and grants no proof credit.

## Evidence and differential

The C2 run is Build `200ed04f-904b-4971-a27c-7e10edeb7f46`, proof/infra
`3a65d691e8c1ccdd9c0533516895a47c61a3335d`, using tool
`2e95eec0c0a08c071f896fd9d00a606f572d5352`. The consumer log reports the fixed
producer AST `a567807354602a49f2445f083b4c62a849cb385b915f9a6e6fd99932473e878e`,
typed location-only transport over 3442 locations, and the complete nine-body
verification sequence before `sort4_stable`. The consumer has no symbolic
execution errors, but exits 1 without `0 errors found` due to these five final
diagnostics:

- `selector/lib.rs(117,13-35)`
- `selector/lib.rs(155,170-196)`
- `selector/lib.rs(156,25-52)`
- `selector/lib.rs(173,20-41)`
- `selector/lib.rs(174,21-43)`

The raw consumer trace records execution of each of these exact spans before
the final dead-code report. The source copied to
`composition-fixture/selector/lib.rs` has SHA256
`7ec86f52b362f7f8b2ed26e3fa108212eb3d6288820bab9c6db3fa37bf8cabe0`, equal to
the standalone selector's `verified/lib.rs`. The fresh standalone selector
trace uses that same source SHA and has no dead-code diagnostics. Thus source
annotations and body bytes do not explain the five residual entries.

There is an environment difference: standalone selector uses
`SORT4_STRICT_LFT_CUT=0`, while the C4 consumer uses `=1`. The selector source
contains no `end_lft_binding` marker; the strict-cut path requires such markers
before it applies the cut machinery. The cleanup projection was already active
and required at producer export, and the imported artifact is the exact final
nine-body AST. The consumer's C4 environment therefore does not explain why
these already executed selector spans remain registered.

## Concrete cause

The exporter at tool
`2e95eec0c0a08c071f896fd9d00a606f572d5352`,
`src/rust_frontend/vf_mir_translator/vf_mir_translator.ml:17735-17744`, first
audits the typed AST and then serializes `(headers, flattened)` with
`Marshal.No_sharing`. The importer unmarshals that value and changes only the
source-location endpoint from `verified/lib.rs` to `selector/lib.rs`; the
typed certificate confirms source coordinates and ordinary strings are
unchanged.

VeriFast's console dead-code tracker in `src/vfconsole/vfconsole.ml:111-116,
267-280` uses `HashedLoc.equal l1 l2 = l1 == l2`: it registers a statement's
location and removes it when execution reports that same location object.
`Marshal.No_sharing` discards physical sharing in the serialized object graph,
including shared source-location tuples. This gives a concrete explanation
for the observed pattern: the location values print identically and their
statements execute, yet the tracker retains five location entries. The exact
per-entry alias pairs are not recoverable from the no-sharing artifact, so this
is a strongly supported static diagnosis rather than a dynamic identity trace.

## Narrow repair candidate and gates

For a new exact profile, preserve object sharing in the producer AST
serialization used by this transport. Keep the pre-serialization
`inspect_transport_view` call, especially its refusal on repeated mutable
`Ast.Ref` identities; do not remove or weaken it. Keep the import hash,
typed-location certificate, reverse relocation check, exact nine-body/order
admission, and all ordinary verifier dead-code checks. Re-pin the changed
export and relocated hashes, then rerun the full fresh selector producer and
consumer sequence. This is limited to preserving AST object identity through
transport; it adds no proof summary, does not change a contract, and does not
silence a diagnostic.

The existing typed projection comparison is insufficient to qualify this
change: it checks value/coordinate equivalence but intentionally erases
physical aliasing. Add a transport certificate over the raw unmarshalled AST
pair that checks the physical-equality partition of the `loc0` tuples returned
by `Ast.root_caller_token` at every visited location, including aliases
between statement and expression locations. Require the partition to be
identical in the original and relocated graphs, alongside the existing typed
value comparison and location counts. This directly guards the identity used
by `vfconsole`'s dead-code hashtable and detects any accidental alias change
from relocation. Retain the no-repeated-`Ast.Ref` audit before the sharing-
preserving marshal; do not replace it with an alias check that permits mutable
reference reuse. Because raw endpoint relocation operates on a same-length
path and only after the typed location-only audit, it should preserve this
partition, but that invariant needs explicit certification.

With sharing-preserving Marshal, a repeated path string may be emitted only
once even when many typed locations reference it. Therefore do not require
the raw byte replacement count to equal the typed endpoint count. Keep both
counts as separate evidence: require a positive raw replacement count, and
have the typed certificate independently check every location coordinate and
constructor under the exact old-to-new endpoint relation; require original
typed old-endpoint count > 0, original new-endpoint count = 0, relocated
old-endpoint count = 0, and relocated new-endpoint count equal to the
original typed old-endpoint count. Continue checking ordinary string leaves
are unchanged and contain neither endpoint. Retain the reverse-relocation
hash check.

Also compare the producer's live admitted AST alias partition with the
unmarshalled exported AST before treating the export as sealed. For the
traversal, record physical alias partitions for both `Ast.root_caller_token`
and `Ast.lexed_loc` location tuples, so statement keys and nested location
identities are covered; compare those partitions again between original and
relocated imported graphs. This producer-side check verifies that Marshal
itself preserved the relevant sharing, rather than only proving that later
relocation preserved whatever sharing happened to survive. Keep the existing
fail-closed exclusions for repeated mutable `Ast.Ref`, `InferredType`, and
`WSuperMethodCall` unchanged.

The evidence so far identifies the failure mechanism statically; it does not
prove which exact aliases account for each of the five reported entries. The
alias-partition certificate and a fresh Cloud consumer result are therefore
required to close that uncertainty.

The global structural-equality alternative in `vfconsole` is outside this
repair: it could merge distinct synthetic statements that share coordinates
and needs a separate review of dead-code checker behavior. Do not add
`allow_dead_code`, skip the imported bodies, weaken cleanup/unwind checking, or
accept the current five diagnostics.

Acceptance requires a fresh Cloud result on new exact proof/tool/profile pins:
first run producer-seal discovery to record the new sharing-preserving export
hash and review it, then run a second fresh sealed producer/consumer build
using that exact pin. The standalone nine-body producer must pass; the same
final AST must be re-imported and all nine bodies reverified before the
consumer; the consumer must have no residual dead-code entries and must
complete its original posts, return, leak, and lifetime checks. Preserve the
selector cleanup-off negative and the existing six same-post composition
controls plus exact admission mutants. The previous Build's certificate and
body proofs remain bound to its old transport and cannot validate the repair
candidate.

## Post-implementation static review: tool `87b79a844d7ec9b05d9768bdb3e6e249efde8120`

**Review result: GO for the producer-seal discovery run, with no proof credit.**
The reviewed tool diff changes the export from `Marshal.No_sharing` to default
sharing-preserving Marshal and compares live-producer versus decoded-export
alias partitions before writing the artifact. On import it independently
requires positive raw replacements, keeps typed old/new endpoint counts
separate, checks the exact typed AST/location relation and unchanged ordinary
strings, checks the original-versus-relocated alias partition, and retains the
reverse-relocation hash. The partition traversal records both
`Ast.root_caller_token` and `Ast.lexed_loc` tuple identities. The existing
fail-closed `Ast.Ref`, `InferredType`, and `WSuperMethodCall` checks remain in
place. This matches the reviewed transport repair boundary.

The runner diff gates discovery receipt creation on the full nine-body
selector success and the producer alias marker, then returns a
`PRODUCER_SEAL_DISCOVERY_ONLY` result with `diagnostic_complete=false`,
`composition_positive=false`, and consumer admission `NOT_RUN_UNSEALED_DISCOVERY`.
It captures the outer normal/readonly MIR through the existing capture path
before returning. The ordinary composition gate additionally requires the
reviewed typed endpoint count and both alias-preservation markers. Discovery
must therefore only establish/review the new export hash and required capture;
it cannot serve as the fixed-pin consumer run.

This is static review only. The discovery build must still show the fresh
producer succeeds and emits the expected certificate/receipt. After reviewing
that exact seal, a second fresh profile must pin it and reprove all nine bodies
before the consumer; only that run can test whether the dead-code diagnostics
are resolved.
