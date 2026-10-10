# Compile-only preflight for the prepared guard candidate

This Cloud-only preflight runs inside the merge lane after its pinned baseline
tool build and before the retained proof suite. The dispatcher mode is bound by
`origin-layout/BUILD-MODE.json`: `compile-only` prepares the candidate and
builds its exporter, generated decoder, translator, and VeriFast console, then
exits without running a proof fixture or suite. `proof` retains the current
full-lane behavior; an absent mode file also defaults to `proof`. Compile-only
evidence keeps compiler status separate from proof status and cannot be
accepted proof evidence.

The merge dispatcher uses these candidate paths under its existing pinned
Cloud setup:

```bash
research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/build-profile.sh \
  /workspace/merge-work/runner-temp/challenge8-merge-overnight/source \
  /workspace/merge-work/runner-temp/challenge8-merge-overnight/verifast-tracked-md-source \
  /workspace/evidence/allprooflogs/tracked-md-build-preparation \
  /workspace/evidence/allprooflogs/build \
  prepare-only

research/challenge-8/cloud-build/origin-layout/compile-preflight.sh \
  /workspace/merge-work/runner-temp/challenge8-merge-overnight/verifast-tracked-md-source \
  /workspace/evidence/allprooflogs/tracked-md-build
```

In compile-only mode, `run.sh` first runs the existing
`build-profile.sh … prepare-only` using its already pinned source home and
`allprooflogs/build`; that produces the candidate and preparation receipt
without compiling. It then invokes the preflight above. The preflight checks
the candidate HEAD, source hashes, and patch hashes against
`insertion-onecell/PROFILE.json` before building. It uses one Cargo job and
explicit `dune build -j 1` stages for the decoder, translator, and
`vfconsole/vfconsole.exe`; the console executable is copied to the candidate's
`bin/verifast`. It receives the GNUmakefile's findlib-derived `Z3_DLL_DIR` and
preserves the pinned `WITHOUT_LABLGTK=yes` environment. Each compiler stage has
a separate log, time-v report, exit-code file, and timeout. An EXIT trap writes
a failure `compile-preflight.json` naming the failed stage; successful
compilation rechecks source hashes and writes the detailed report.

At the root, `proof-audit.json` records `accepted: false`,
`proof_attempted: false`, and a separate compiler classification. It sets
`diagnostic_complete: true` only when baseline build, candidate preparation,
all four candidate build stages, and the post-build source hash check pass.
The packager's `allprooflogs/cases/compile-only/aggregate.json` is explicitly
classified `COMPILE_ONLY_NO_PROOF_CREDIT`; it is not a proof PASS. Any failure
records an incomplete diagnostic and no proof credit. The mode file is
source-certificate-pinned, and `proof` restores the existing full matrix
behavior.
