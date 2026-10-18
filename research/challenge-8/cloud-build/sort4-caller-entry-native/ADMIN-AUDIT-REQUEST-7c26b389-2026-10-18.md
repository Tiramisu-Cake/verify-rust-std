# ADMIN-AUDIT-REQUEST — 7c26b389-1ad9-45c8-9adf-089125476fdb

Prepared request only. Raw audit needs separate owner authorization; this file
neither grants it nor permits another Build/compiler/verifier or account reopening.

Build: `7c26b389-1ad9-45c8-9adf-089125476fdb`, project smallsort-ci, region global.
Owner select-sort4, authorization SORT4-A1-UNUSED-MUT-FIX-CLOUD-2026-10-18;
canonical C experiment protocol retained separately. Exact proof/infra:
`e58a75bbdcf6704175ceebcd72a227607a92d2ae`.
Submitted config SHA256:
`b54b646c52589c95e2e42a869e5c05b4f15b6ed626756ffb77e11cd735b99c41`.

Archive URI:
`gs://smallsort-ci-evidence-504462351565/cloud-build/7c26b389-1ad9-45c8-9adf-089125476fdb/evidence.tar.gz`.
Archive SHA256 from verified ordinary index:
`4da91b4e0f81a8527bfbd45466c21e38daa1cb8cc57860648ec352c389a849ce`.
Brief SHA256 `2a9657a67f3f214e960e09639a2a4afb3be78ce3506d5d06db59f760ff85544f`;
index SHA256 `bbf7d9e8b6dbba8b6e127db93fc31e7d0b4368f1ea1d15576b5aa9888f396cf2`.
Both match the reader processing receipt, processor0.4.0, derived/v2.

Known: ordinary Brief corroborates a1-R-only-native-reference-build TERMINAL
exit2, budget491s; tool-reconstruction adapter_error,26 source-reported NOT_RUN.
But failure_diagnostics.messages=[]: no concrete compiler/make error is returned.
The old Build had two unused_mut errors. Both approved modifiers are removed in
this candidate, and exact source reconstruction gives exporter SHA256
`c29d0d4692eab84257fe61036d6e41dbc11ee3ad999005df4ffb157bb8b463ad`.
Do not assume the old diagnostics persisted, or that exporter compilation passed
and only console failed, without observed command/status evidence.

## Bounded extraction requested

Return **one UTF-8 report <=16384 bytes total**, including references/hashes,
with **at most30 raw context lines total**. No raw archive/full log/full verifier
log/MIR/AST attachments. No rerun and no token/credential output.

1. Extract the first causally linked compiler/make error underlying this combined
   build exit2, with only the bounded context above. Separate observed diagnostic,
   source-reported blocker and your causal inference. If unestablished, say UNKNOWN.
2. Give the recorded failing command/argv/cwd/component and its actual status;
   distinguish cargo/rustc, OCaml/console, another make prerequisite, and parent
   make exit2. Do not infer child exit codes from parent's status or reconstruct
   execution as if observed. State whether the two old unused_mut diagnostics
   are actually present in this log or whether different diagnostics caused it.
3. State last directly confirmed build substage and next not-reached/unknown
   stage. Report whether exporter compile success, console completion and R-only
   reference receipt are actually evidenced. Confirm C/matrix stage-marker
   presence/absence from originals, not from missing index messages.
4. Report original cases/aggregates/stage-marker presence/count/schema/provenance
   sufficient to reconcile26NOT_RUN, without dumping26 full payloads or inventing
   proof credit. Missing derived messages do not establish missing originals.
5. For each factual finding give bucket/object URI and generation if available,
   archive member, JSON pointer or <=30-line excerpt range, full SHA256 verified
   against the archive inventory. Keep the exact Build/proof/infra/config/archive
   chain above. Return an out-of-band report SHA256 when feasible.

Priority sources, under separate administrative authorization only:

- `allprooflogs/cases/sort4-c1-current-recovery/a1-tool/a1-R-only-native-reference-build.log`,
  verified member SHA256 `f3ba5380316c6aee2aad00bc004aaaade6af5f9d2ba75f6b0569134314c81a9b`.
- Same prefix `a1-R-only-native-reference-build-stage.json`, SHA256
  `66620752e728d7b7f66dfe0a20704d714845afd825a1f3fe1f18123e3b0e1e90`.
- `proof-audit.json`, SHA256
  `216c3a8ce72b1e6a0bdff71e0a67f25e9eac0e9fba6930212e3a82789de593f4`;
  only relevant first_blocker/run_error/execution_events/phase metadata.
- Relevant nested build stage receipts/exit files and R-only reference receipt
  presence, if any; files-sha256.json/manifest.json for member/provenance checks.

Pinned parent invocation (source-derived, not a returned runtime argv):
`make -C <isolated-A1-tool>/src build-vf-rust-mir-exporter ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes`.
It must exit0 before the reference binary/receipt and before C. Do not bypass this
gate, suppress warnings or alter verdicts/pins/ledger/proof credit. Goal: determine
the next minimum justified fix before a future separately authorized Build.
