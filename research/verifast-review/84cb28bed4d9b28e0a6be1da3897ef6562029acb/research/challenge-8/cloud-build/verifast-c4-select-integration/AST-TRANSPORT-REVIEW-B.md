# Independent AST transport review B

Static review, 2026-10-10. Target: the proposed transport certificate for the
final selector AST, with the VeriFast kernel unchanged. No compilation,
translator execution, extraction, proof, or Cloud operation was performed.

## Verdict

**Conditional GO for a fresh Cloud diagnostic**, once the transport certificate
is implemented as described below, the fixed artifact/profile manifest is
reviewed, and the artifact is regenerated from a fresh successful nine-body
selector run. The current raw Marshal substring replacement by itself remains
insufficient. This review does not establish build, refinement, or proof
success.

## Typed projection

`Ocaml_expr_of_ast.of_list ... of_package` provides a useful structural view of
the `(headers, packages)` AST: locations become `Ocaml_expr.Loc`; ordinary
strings become `S`; constructors, lists, tuples, options, scalar values, and
the AST fields represented by those constructors remain structurally visible.
The formatter dereferences `Ref` nodes through their `contents`, so a recursive
comparison must visit the reference contents. Inferred types are projected as
an `Oo.id` plus their referenced inferred-type state; comparisons across two
separate decodes should preserve the identity equivalence relation (a
consistent ID renaming), rather than demand equal process-local object IDs.
The transport currently serializes with `Marshal.No_sharing`. Since inferred
type identity is physical-object based, the certificate must also check that
serialization and relocation preserve every alias relation relevant to
`InferredType` and mutable `Ref` fields. The narrow safe gate is to refuse an
artifact containing `InferredType` or aliased mutable references unless the
round-trip demonstrates the same identity partition; alternatively use a
sharing-preserving serialization and pin it. Equality of contents alone is
not enough when AST behavior depends on identity.

The projection is not complete for every AST constructor. In particular,
`WSuperMethodCall` drops its `methInfo` field (`src/frontend/ocaml_expr_of_ast.ml`,
around line 562). Several statement constructors deliberately raise `TODO`
instead of projecting (`PerformActionStmt`, fraction and box/handle operations,
around lines 842–848). Therefore, admission must scan the original typed AST
and refuse if it contains `WSuperMethodCall` or any constructor that the
projection omits or rejects. Do not treat successful projection alone as proof
that the projection is lossless. For the exact nine-body artifact, the
certificate should record that this fail-closed scan passed.

With that guard, compare original and relocated projections recursively over
both headers and packages. Permit differences only in `Loc` source paths that
equal the exact old path; require the new path and preserve line/column values,
`Lexed`/dummy shape, and nested macro-location structure. Require all `S`
leaves to compare unchanged, and in particular zero old-path occurrences in
ordinary strings. Count old-path occurrences in typed locations and require
that count to equal both the raw Marshal byte occurrence count and the number
of substitutions. Keep the existing raw artifact hash, relocated hash, and
reverse-certificate checks as integrity checks; they do not replace the
structural comparison.

## Producer binding

An environment-supplied hash is not producer provenance. Before final replay,
freeze an immutable reviewed manifest containing the fresh producer AST SHA,
selector source SHA, effective tool/profile hashes, the exact source/MIR/body
and pre-AST pins, and the nine-body proof evidence identity. The final replay
must require the exported AST SHA to equal that fixed manifest value. Generate
a per-run receipt only after the driver validates `selector_ok`; bind it to the
manifest, export artifact hash, source/MIR/body identities, effective profile,
and proof-audit/log hashes. The composition stage must consume that receipt and
the matching artifact from the same run.

This is a Cloud-driver evidence chain and stale-artifact admission check, not a
cryptographic attestation that the producer binary or runner is trustworthy.
The consumer still needs to reverify all nine imported definitions before
`sort4_stable` in the same kernel invocation, and its actual typed first-call
gate remains independently necessary.

## Scope

No kernel change, generalized AST framework, assumed summary, or expanded
proof claim is approved here. Any omitted projection field discovered in the
exact artifact changes this verdict to **INCONCLUSIVE** until the projection is
made lossless for that field or admission refuses the artifact.
