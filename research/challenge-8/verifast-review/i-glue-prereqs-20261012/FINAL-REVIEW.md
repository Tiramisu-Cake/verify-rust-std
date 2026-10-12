# Final independent review — I glue prerequisites, 2026-10-12

**Decision: NOT_QUALIFIED.** This is a setup/build result, not a C2 proof
result or a validated profile. The reviewed tool head is
`c23278c3ea716b64d2fdeee134b834095956ac56`; the paired project source
is `fc11cdfc`. No new experiment after the authorized main window is
included in this verdict.

## Evidence and gate status

* First Cloud run `d02ccd21` at project `1c1be000` stopped in
  `exporter-build` (exit 101). Its log identified pinned rustc API usage
  errors. Tool follow-up `c23278c3` changed only those three localized API
  sites; independent static review found no new trust rule.
* Second Cloud run `70085ccc-e0b7-4099-98bb-7d206f2fc635` used project
  `fc11cdfc` and tool `c23278c3`. The downloaded archive at
  `/tmp/c8-i-glue-prereqs-20261012/second-evidence/evidence.tar.gz` hashes
  `ef289db69248b93b813918585ad009aeb4c66e9d3f1ad6ab886d07a84eae3266`.
  `exporter-build-exit-code.txt` is `0`; `console-build-exit-code.txt` is
  `2`. The console log shows `vf_mir.capnp` decoder generation, a Cap'n Proto
  source-prefix warning, then pinned `ocaml-decoder` plugin panic
  `src/main.rs:155:14: not yet implemented` / exit 101. Console, official
  refiner and proof-case execution did not complete.
* The archive's `proof-audit.json` says
  `COMPONENT_BUILD_OR_SETUP_FAILURE`, `proof_credit=false`,
  `verification_accepted=false`, `accepted=false` and
  `diagnostic_complete=false`. Its checkpoint records stage `console-build`,
  exit `2`, `raw_result_present=false`. This is faithful to the raw stage logs.
  No C0, C2 positive or intended negative, lifetime/leak, or refinement
  result is established. C1 has a successful exporter substep but fails as a
  whole; C0/C2 remain **NOT_RUN** and C3 remains deferred.

## Concrete remaining blocker

The additive Cap'n Proto schema introduces `concreteGuardFieldOffsets` and
`concreteGuardFieldSizes` as `List(UInt64)` in `AdtDef` (and a `List(Text)`
field). The pinned decoder generator `2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2`
routes a list element through `print_type_decoder`, whose visible cases cover
struct, enum, parameterized pointer and text but end in `todo!()` for numeric
scalar elements. This strongly implicates the new `List(UInt64)` fields in
the plugin panic; the source-prefix warning is separately present in the
console log, so the exact ordering/causal chain still needs Cloud confirmation.
See the [pinned decoder source](https://github.com/btj/capnpc-ocaml-decoder/blob/2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2/src/main.rs#L117-L150).

The next authorized phase decision should first select a narrow encoding
compatible with the frozen decoder, or explicitly review a decoder extension
as a new trusted tool-profile change. Repin the full schema/patch/source
hashes, add a decoder-generation regression gate that distinguishes the
source-prefix warning from the unsupported list element, and only then run a
fresh authorized Cloud build. Passing exporter hashes and an earlier static
admissibility review cannot qualify C0/C2. No local compiler/verifier/proof
execution or new experiment was performed for this review.
