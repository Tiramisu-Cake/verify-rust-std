# Compile-only preflight for the prepared guard candidate

This two-step Cloud-only preflight prepares the already reviewed candidate,
then compiles its exporter, generated decoder, translator, and real VeriFast
console in dependency order. It does not run a proof fixture or change runtime
semantics. The prepare-only mode stops before compiler/proof execution; the
preflight records `COMPILE_ONLY_NO_PROOF_CREDIT`, `accepted: false`, and
`proof_attempted: false`.

Run these commands from the reviewed Cloud Build checkout, with its normal
provider guard and pinned tool environment. The baseline source build evidence
must already exist at `/workspace/evidence/allprooflogs/build`. No unaffected
proof matrix or proof run is a prerequisite for this isolated compile check.

```bash
research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/build-profile.sh \
  /workspace/merge-work/runner-temp/challenge8-merge-overnight/source \
  /workspace/guard-compile-source \
  /workspace/evidence/guard-source-prepare \
  /workspace/evidence/allprooflogs/build \
  prepare-only

research/challenge-8/cloud-build/origin-layout/compile-preflight.sh \
  /workspace/guard-compile-source \
  /workspace/evidence/guard-compile-preflight
```

The first command applies the pinned candidate preparation and writes
`source-prepared.json`, without compiling. The second checks the candidate HEAD,
source hashes, and patch hashes against `insertion-onecell/PROFILE.json` before
building. It uses one Cargo job and explicit `dune build -j 1` stages for the
decoder, translator, and `vfconsole/vfconsole.exe`; the console executable is
copied to the candidate's `bin/verifast`, matching the Make target's artifact
path. The direct Dune console build receives the GNUmakefile's findlib-derived
`Z3_DLL_DIR`; it preserves the ambient `OCAMLPATH` and
`OCAMLOPT_CCLIB_FLAGS`, matching the pinned `WITHOUT_LABLGTK=yes` profile,
which skips those GNUmakefile exports. Each build stage has a separate log,
time-v report, exit-code file, and a 900-second timeout. An EXIT trap writes a
failure `compile-preflight.json` naming the failed stage; after successful
compilation, the script rechecks pinned source hashes and writes the detailed
compile-only report.

The existing Cloud recipe transports this script as a proof-path input, but no
early dispatcher hook is integrated. These commands are an explicit
prepare-then-preflight step; the regular proof dispatcher does not invoke the
preflight automatically. A compiler failure must be retained as compile
evidence and resolved before starting proof work. A repaired source requires a
fresh prepared home and fresh evidence directories. A successful compile says
nothing about proof validity or acceptance.
