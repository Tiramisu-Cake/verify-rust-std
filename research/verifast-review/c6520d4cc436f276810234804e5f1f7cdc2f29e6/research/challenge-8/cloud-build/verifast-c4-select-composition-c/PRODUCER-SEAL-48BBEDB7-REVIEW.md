# Independent raw review: sharing-preserving selector producer seal

**Verdict: GO to freeze this exact AST hash as the candidate producer pin for
the next fresh sealed run. This is not composition acceptance or final proof
credit.** Review was limited to saved discovery artifacts and logs; no local
tool, extraction, verifier, or Cloud command was run.

## Seal and provenance

Cloud Build `2a5e48b0-3be1-4f01-8026-2d358329667d` used proof/infra commit
`d718d56dae82dd2a12393f970bcae085ec8a1aa4`, profile
`verifast-c4-select-composition-20261011-c3-discovery`, and manifest SHA256
`f8df48257788f227954df17571076e7f57fb3dc8eff34c37e9e411253e81bbf0`.
The manifest pins tool candidate `87b79a844d7ec9b05d9768bdb3e6e249efde8120`;
the saved effective-hashes record says `exact: true`, with translator SHA256
`bc00d59110bf1c235f866ec141726965bca8f12378f1dc42c39458a3f624e8de` and the
remaining listed effective tool/spec hashes matching that manifest.

The saved artifact `selector-final-ast.marshal` has SHA256
`48bbedb711fade25fde0622af0b56c6c17aab318ce0a94f1e517f9c153a81af9` and size
531,290 bytes. The proof log binds this hash to the final nine-body export and
prints `producer_location_alias_partition=preserved`. The companion readable
declaration dump has SHA256
`c112ff565a67f8cd3a525b7477aa5ef83070ef4221a593fac661ce043f2901c9`; it is
inspection output, not the transported proof object.

## Producer proof and source correspondence

The raw `selector-positive-proof.json` reports exit 0, no errors, no dead-code
diagnostics, `0 errors found`, return observed, and leak check observed. Its
verified source SHA256 is
`7ec86f52b362f7f8b2ed26e3fa108212eb3d6288820bab9c6db3fa37bf8cabe0`. The
final required function sequence is the seven selector helpers, the nested
`DropOnPanic<T>::drop`, and `select_unpredictable`; the saved headers and log
show all nine verified, with nested Drop before the outer function.

The fresh pre-AST fingerprint refusal record says `exact: true` and its unit
and nine body fingerprints match the pinned values. The saved selector MIR
record says `selector_exact: true`; its complete normal and readonly decoded
MIR hashes are respectively
`bb50b114bcda7905c84f890500f4a8991009c4a554ddcbe8d5eb5f6a87229e83` and
`c0d287337dd3f1b2c6cd84a96274a7f4861550d664d16fb493ffef8a57a546a9`. Its nine
body hashes match the pinned `O26-R3-FRAME-SHADOW-TEST.json` source profile.
The source pair is original
`466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5` and
verified `7ec86f52b362f7f8b2ed26e3fa108212eb3d6288820bab9c6db3fa37bf8cabe0`.
The C4 capture likewise says `c4_exact: true`, with complete `sort4_stable`
normal/readonly record hashes
`af8dcfda4212ec1e1bd8fcafcb763fe0107fbeb63b6c1a65bc830e2c81bf9f80` and
`aebd7d6219106ba8f6b2fd730bb0a9b0876bea141eb2f06ab7c6e3804abc23ea`; its
verified source hash is
`ba9e6ad3633004c3d934c590462443951ddd6dec80a5df9ffb687ec940958c6f`.

## Discovery-run classification and remaining gates

The build itself is classified `SETUP_OR_EXECUTION_FAILURE`, with
`diagnostic_complete: false`; `producer-receipt.json` was not created. The
saved traceback identifies the later outer-capture setup error:
`outer-discovery nine-body decoded MIR order differs`. The requested name list
included `recover_pair`, which is a ghost lemma, while the captured runtime
MIR contains `negative_outer_bound_escape`; the capture helper's source shows
it requires every requested name as a runtime body. Normal outer MIR export
and decode completed, but readonly outer MIR and that capture's refinement
stage did not run. This capture-name/setup defect is separate from the already
completed selector producer proof and does not turn the run into a proof
negative.

The candidate seal is suitable for freezing because the exact producer proof,
effective translator pin, source fingerprints, full selector/C4 source MIR
correspondence, artifact digest, and producer alias marker are present and
consistent. The composition consumer did not run. Before final acceptance,
complete the corrected outer normal/readonly capture through the authorized
Cloud capture-only path, then run a second fresh sealed producer and consumer
profile pinned to this exact artifact hash. That run must reverify all nine
bodies, observe the import-side typed endpoint and alias certificates, clear
all dead-code entries, and pass the original consumer postconditions, return,
leak, and lifetime checks plus the already required controls. This discovery
build itself grants no consumer, negative, or final-profile credit.
