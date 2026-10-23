# Independent W8 preparation CLI review

Reviewer: independent GPT-6 Luna HIGH, no nested delegation.
Decision: NO_GO for the preparation CLI pending a localized input-pin fix; no proof credit.
Baseline: `f9960fedbb72058984a922ff67580d10dc81fbe6`.
Candidate: `3810432d3279013bb7385eab1707996e2a000383` (tree `8c2aa6c65bb5a03960603f430c194eafdd4b1874`).
Spec SHA256: `bb771f4699cc30be1601b3528c3bcea11f22a79f9ce1ad3e4da609716b783fde`.
Packet SHA256: `a0d0360934d1e33964b583e98a4e828a21074336627c068f81b8446f8eb103e6`.
`smallsort-session review check` passed for these exact candidate and spec identities.

## Finding: the input manifest and its pins are caller-controlled

`main()` accepts an arbitrary `--manifest` path and reads it after provider admission. `validate_manifest()` checks the fixed source commit/blob/path/SHA, but for each input it only checks that the path is safe-relative and the SHA is well-formed. It does not require the canonical manifest path/hash or the reviewed input path/SHA pairs. `assemble_units()` then verifies bytes against those caller-supplied manifest hashes. Therefore a different manifest can repin the header, positive file, or negative fragments and still produce prepared units. The current metadata remains marked UNVERIFIED, which prevents proof credit, but this defeats the stated fixed-input provenance guard and can hand a later phase unreviewed proof material. The lexical header check also does not reject an `axiom` declaration, so it cannot substitute for pinning the reviewed header bytes.

Require the canonical manifest identity and fixed input path/SHA allowlist before reading inputs (or an equivalently exact, reviewed pin mechanism). Keep synthetic tests isolated by injecting test-only pin constants/manifest identity; do not weaken production validation to permit alternate manifests. The current tests cover changed bytes against an unchanged manifest but do not cover a self-consistently repinned manifest.

Other scoped checks found no blocker: the CLI calls the existing provider guard before manifest/source/input reads; source content has fixed commit/blob/path/SHA pins; input paths reject traversal and symlinks; output creation is exclusive and partial writes are cleaned while preserving the original exception. Target markers and assertion coordinates are checked in separate LF-only fragments, and each negative unit must have the three positive bodies followed by exactly one distinct negative body. The original `.gh`, `.c`, and `.inc` artifacts are unchanged. The import path is inert, and output metadata stays `UNVERIFIED_STATIC_PREPARATION`, `proof_credit: false`, `parser_input_binding: NOT_ESTABLISHED`, with diagnostic predicates null.

Validation: packet identity check passed; `git diff --check` passed. The packet reports ten synthetic-only tests passed; they patch the source pin for fixture bytes and do not read actual W8 proof inputs or Rust source. I did not run the CLI, assembler, compiler, or verifier. This review grants no Cloud-stage admission or proof credit.

## Resolution review: pinned-input fix delta

Reviewer: independent GPT-6 Luna HIGH, no nested delegation.
Decision: GO for the preparation-only fix delta below; the original NO_GO above is preserved as the prior-candidate verdict. No proof credit, W8 admission, or dispatch authority.
Baseline: `3defef8604fe82dec037fc6283aab1bab389e9c4`.
Candidate: `84b9ffb9301ab95ade8b06e72f8e8bc0e1101884` (tree `27cb8ae137f5036dced18ae150591240b0f211d0`).
Spec SHA256: `d7510c128e0e7cd6be3dc8c9220651e066f6456ba4e0023be0d7b611761ab127`.
Packet SHA256: `11ed18162e5649f367b8f3c71240cff1c323720d279c497c5b68f1e46f0edbaa`.
`smallsort-session review check` passed for these exact candidate and spec identities.

The input-provenance finding is resolved in code. The CLI checks the raw manifest bytes against `MANIFEST_SHA256` before JSON parsing. `validate_manifest()` requires the exact `INPUT_PINS` path/SHA pair for every required input, and the added `axiom` token refusal covers both the header closure and positive/negative ghost bodies. I independently hashed the manifest and all five `.gh`/`.c`/`.inc` input files from the candidate commit; they match the raw manifest constant and the code allowlist. The original arithmetic inputs are unchanged from the prior candidate. The provider guard remains before manifest/source/input reads, and metadata remains explicitly unverified with proof credit false and parser binding not established.

Test-coverage note: `test_production_manifest_rejects_self_repinned_alternate_input` builds its starting manifest from synthetic input hashes, which already differ from the production allowlist. Its modified manifest is rejected, but this test does not by itself demonstrate repinning a valid production manifest to matching alternate bytes. The production code’s fixed tuple comparison and raw-manifest hash check are direct and correct; a future synthetic fixture using the genuine manifest with one consistently changed input/hash would make this regression test precise. The packet reports 12 synthetic-only tests passing. No actual CLI, assembly, compiler, verifier, or proof input execution was performed for this review.

This is preparation-only. Lexical checks do not establish C parsing, verification, source/MIR binding, Rust safety, ownership, or termination. No Cloud-stage admission or proof credit follows.
