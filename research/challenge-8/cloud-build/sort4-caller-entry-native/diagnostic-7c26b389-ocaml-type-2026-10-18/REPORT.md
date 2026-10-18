# Build 7c26b389: ordinary Brief now identifies the OCaml blocker

Build: `7c26b389-1ad9-45c8-9adf-089125476fdb`. Diagnostic checkpoint parent:
`6aebaf19d028e38aa38edf828aa5ca647f28228a`. Owner: select-sort4.

The reloaded ordinary Evidence Brief (processor 0.5.1) is sufficient to select a
minimal source proposal. Earlier Brief limitations and administrative requests
remain historical records; administrative raw access is not needed to select
this proposal. No raw evidence or full logs were read or downloaded.

## Confirmed observations and limits

The Brief reports CORROBORATED / CORROBORATED_SOURCE_REPORT diagnostics:
`a1-R-only-native-reference-build` exited 2; OCaml reported
`The constructor D.Type expects 0 argument(s)` at
`rust_frontend/vf_mir_translator/vf_mir_translator.ml:6681`.
The make summary reports Error 1, with child status UNKNOWN. These are distinct
exit observations; the packaging/run exit 0 is not proof acceptance.

The diagnostic refers to log line 1283, SHA-256
`f3ba5380316c6aee2aad00bc004aaaade6af5f9d2ba75f6b0569134314c81a9b`;
the R-only stage receipt SHA-256 is
`66620752e728d7b7f66dfe0a20704d714845afd825a1f3fe1f18123e3b0e1e90`.
These references are supplied by [the Brief](brief.md) and
[evidence index](evidence-index.json), not by reading their raw sources.
[The processing receipt](processing-receipt.json) hashes match the saved Brief
and index. VERIFIED_ARCHIVE_AND_INVENTORY establishes integrity, not proof credit.

Coverage is incomplete: 102 candidate stage records, 96 parsed, 6 not captured,
32 omitted from the compact presentation. There are 95 zero exits and one nonzero;
order is NOT_ESTABLISHED and last completed stage UNKNOWN. No independent result
for the Rust exporter alone is established. This diagnostic does not prove the
absence of other tool errors or prove old unused_mut diagnostics cleared.

All 26 matrix rows remain source-reported NOT_RUN, including P1, both threshold
body/conformance pairs, caller/bound/overflow obligations, negatives, seven
regressions and the complete own-pair N-false31 lifecycle. No P1 equality result,
body proof, receipt acceptance or caller outcome is established. Successful R-only
reference receipt and final C tool are downstream of this failure in pinned source
flow; neither success is established by evidence. No formal credit is assigned.
Full A1/A2 and actual small_sort-to-helper transfer remain open.

## Source diagnosis and separate proposal

Pure source reconstruction from tool base
`f76012fb518703b1d98e243ac4f487f16877cfcb`, the 43 pinned pre-R patches and the
published R patch reproduces the reported location exactly. R-only translator
SHA-256 is `564a865b4a4b0ac6a05c55f9f1ece48f7517e614bf25f49816c34eebe269e6ed`.
At line 6680, normalize_required_arg binds an unannotated local match result;
line 6681 contains `D.Type ty -> D.Type (normalize_required_ty regions ty)`.

The pinned schema defines GenericArgKind.type with Ty payload and
GenericParamDefKind.type with Void payload. The pinned OCaml decoder generator
`2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2` emits same-named constructors, payload
versus nullary respectively. Its src/main.rs SHA-256 is
`45c54aa26bb62e0e2d401ce510d45c3c46f9beff5996379c46fd6c3affbb52a9`.
The source-based explanation is constructor disambiguation without an expected
result type. Brief supplies no column/span, so which occurrence was highlighted
is UNKNOWN; this explanation and fix have not been compiler-validated.

[The proposed patch](PROPOSED-generic-arg-kind-annotation.patch) changes only:
`let kind = match arg.kind with` to
`let kind : D.generic_arg_kind = match arg.kind with`.
It supplies type context without changing the match arms, schema or semantics.
This is a proposal only, not an authorized activation of a new R candidate.

Source-only patch application/check passes, and unchanged C applies afterward.
[Static identities and limitations](source-check.json):

- Overlay SHA-256: e89272bdfa653f49c1ec2db3cd72a07bd92845e30ec36eaec9577b6a2ec3688d.
- Proposed R translator: 7b9ae6bfcc056cf5b1ade002c867157a36cc992535d2baf40b9dd10203c433c3.
- Proposed final C translator: 72f4f0b83d3c565edde5c9bbb688ac12a6d21ce94d149fff37c22a5555ac639d.

No compiler, decoder generator, extraction or verifier was executed. Temporary
source files from this diagnosis were removed; foreign decoder-source checkout
and coordinator state were preserved. Active patches, profile, historical pins,
verdicts and ledgers are unchanged.

## Next authorized preparation and validation

Review the one-line proposal, then obtain authorization to fold it into a new full
R candidate. Recompute the full R-patch hash from actual bytes (the overlay hash
above is not that hash); bind proposed R-after/C-before/C-after translator hashes,
retain R-before, exporter c29d0d46...b463ad and all other semantic pins. Keep C
patch bytes unchanged. Run source-only reconstruction, closure/config checks and
pin review before a separately authorized Cloud-only build. That build must first
complete R-only exporter/console and its own reference receipt, then final C and
the unchanged 26-row matrix with own-pair N-false31 receipt ordering.

The sole existing Build allowance was consumed: 433/960 Cloud seconds charged,
527 retired; account CLOSED, no retry or carry. No new Build or account opening
occurred. Another Build needs a new explicit allowance/window. Compilation of
this proposal and any subsequent blocker remain UNKNOWN.
