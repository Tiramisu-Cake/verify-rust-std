# Typed AST transport certificate B

This card records the narrow transport contract before implementation in the pinned VeriFast translator. The transported value remains the existing Marshal pair `(headers, flattened)`; no serialization format, producer admission, semantic AST, kernel behavior, or selector obligation changes.

## Domain and authorization

The producer must first satisfy the existing exact-nine-body admission and the fixed SmallSort source digest `7ec86f52b362f7f8b2ed26e3fa108212eb3d6288820bab9c6db3fa37bf8cabe0`. The consumer retains the existing exact one-body C4 admission and checks the existing pinned export SHA gate. The selector source itself is checked against its separately pinned source SHA. This code does not invent or authorize a digest: the owner pins the first fresh, unchanged producer artifact after Cloud verification in the external manifest/receipt.

The only permitted transport mutation is changing the exact typed source-location file path `verified/lib.rs` to `selector/lib.rs` while preserving line/column coordinates and the rest of the location value, including macro structure. The old/new paths have equal byte length. Every other source path, AST constructor, scalar, string, declaration, header, and ordering must remain identical.

## Certificate construction

Before export serialization, create typed structural views of headers and flattened declarations with `Ocaml_expr_of_ast`. Reject `WSuperMethodCall`, because that projector omits `methInfo`; reject `InferredType`, whose mutable inference state is not covered by the transport proof. Walk each `Ref`'s contents exactly once and reject a repeated physical `Ref.id`, so ignoring object identities when comparing separately decoded projections cannot erase sharing. No alias-preserving general serializer is introduced.

At import, decode the original Marshal pair, form its typed view and apply the same fail-closed domain guards. Form the relocated Marshal pair by exact fixed-width replacement, decode it, apply the guards again, and form a second typed view. Recursively compare both views: all constructors and non-location payloads must match exactly; every old-path `Loc` must correspond to the new path with identical remaining location structure; every other `Loc` must be exactly equal. Count old-path typed locations and require that count to equal raw Marshal replacement count. Require ordinary `S`-string occurrences of either endpoint to be zero in both projections. Require at least one certified path location and exact reverse replacement back to the original bytes.

Header/package collisions remain structural: only exactly equal shared declarations/headers may be deduplicated; any same-key unequal value rejects. Preserve imported package and declaration sequence and retain extra ghost definitions. The runtime-body gate counts only the exact nine `Ast.Func (Ast.Regular, ..., Some body, ...)` entries, not arbitrary body-bearing ghost/proof declarations.

## Invariants and limitations

1. Original producer bytes are SHA-256 pinned by the import gate; the source SHA and producer artifact identity are independent external receipt facts.
2. The translated selector-local source has the same bytes as the producer source, checked by the selector source digest.
3. The typed projection is a partial, fail-closed audit of the exact admitted AST domain. Unsupported nodes or mutable inferred-type nodes make the artifact inconclusive rather than being silently normalized.
4. Location transport preserves all location fields except the single exact file path. The typed-location count equals raw byte replacement count; ordinary AST strings cannot be changed by this mechanism.
5. Neither projection nor comparison changes parser, spec, verifier, proof posts, or kernel behavior; all nine imported runtime bodies are still verified in the consumer before the C4 body.

No local compilation, extraction, verifier run, or proof test is part of this implementation. Compilation and proof validation remain Cloud-only.
