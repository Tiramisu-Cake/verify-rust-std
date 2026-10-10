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

The next minimal proof lane (run only after a confirmed exact compile) uses
`BUILD-MODE.json` mode `bridge-minimal`. The same pinned baseline preparation
and four-stage preflight run first. A compiler-only `profile-build.json` is
written from actual binary/source hashes after the post-build check; it carries
no native/proof credit. The runner then executes the retained-six ordinary
normal/unwind smoke and calls the existing strict one-cell driver with
`--campaign bridge-minimal-v1` using the candidate schema. The driver retains
all provider/compiler/source/profile admission and the exact combined smoke,
then executes the six span controls, five concrete recovery diagnostics and
nine guard controls. Guard assertion controls require a source/MIR/AST layout
and StorageLive receipt binding. The `missing_held_owner` u64 case is explicitly
NOT_APPLICABLE because primitive own is empty; it is not counted as a resource
negative. No legacy generic/Drop/MD campaign or actual glue/unwind is run.
`accepted: false` and component diagnostics remain separate from whole-profile
acceptance. A proof failure cannot turn a successful compiler receipt into a
compiler failure in the root audit.

Source composition can be checked without any compiler/proof:

```bash
python3 research/challenge-8/cloud-build/origin-layout/source-replay.py \
  --git-source /root/verifast-merge-incoming-span --output /tmp/merge-effective-replay-FRESH
```

This checks the retained-six baseline checkpoint and all twelve effective
source hashes after the ten ordered patches. The component commit e16352c4
alone does not contain the retained-six changes; EFFECTIVE-SOURCE.json records
the composition rather than pretending that its three differing source hashes
are component hashes.

Compile-only source transport closure: the current merge recipe omits
`concrete-drop-body.py` and `onecell-drop-interface.py`. Both remain tracked
in the repository and are outside the compile-only dependency path; startup
static preflight parses the driver without importing these modules, and the
early compile-only exit never invokes it. Before bridge-minimal, either restore
these inputs within the fixed payload bound or make unused legacy imports lazy
without changing cases/contracts. The fixed source transport/coordinator is
unchanged. This exclusion supplies no proof credit.
