# Compile-only preflight for the prepared guard candidate

This preflight isolates compiler/build failures before any proof fixture or
proof stage is started. It accepts an already prepared candidate source home;
it does not copy a checkout, apply patches, change coordinator/cache state, or
dispatch a Cloud Build. All compiler and Dune execution remains Cloud-only.

From the reviewed Cloud Build shell, after the existing preparation step has
produced the candidate source home, run:

```bash
research/challenge-8/cloud-build/origin-layout/compile-preflight.sh \
  /workspace/<prepared-candidate-source-home> \
  /workspace/<new-empty-compile-evidence-directory>
```

The caller must provide the same Cloud provider guard and pinned dependency
environment as the existing `insertion-onecell/build-profile.sh`: supported
`SMALLSORT_PROVIDER_FILE`, `SMALLSORT_EXECUTION_PROVIDER=cloud-build`,
`RUSTUP_TOOLCHAIN=nightly-2026-09-25`, and `/tmp/vfdeps-adf88dc` containing the
already provisioned Cap'n Proto/Dune toolchain. The script checks the existing
`insertion-onecell/PROFILE.json` hashes for the prepared source and four patch
inputs before invoking any build. A mismatch exits before compilation.

The build order is deliberately narrow and serial:

1. `cargo build --locked` for the prepared `vf_mir_exporter`, then copy that
   just-built executable into the candidate's `bin/` as the frontend consumes
   it.
2. Dune-build `vf_mir_decoder.cma`, which runs the schema-generated decoder
   rule and builds its `vf_mir` schema dependency.
3. Dune-build `vf_mir_translator.cma`.
4. Build the real `../bin/verifast` Make target with `-j1`, compiling/linking
   the remaining OCaml dependencies, AST emitter and console executable used
   by the later proof stage.

Each stage gets a separate log and exit-code file. On completion,
`compile-preflight.json` records `COMPILE_ONLY_NO_PROOF_CREDIT`,
`accepted: false`, and `proof_attempted: false`, along with pinned source and
binary hashes. This result can establish only that the selected source builds;
it does not run or upgrade any proof, fixture, classifier, or acceptance gate.
If a stage fails, stop before proof execution and retain its log as compile
evidence. A repaired source requires a fresh preflight run and fresh evidence
directory.
