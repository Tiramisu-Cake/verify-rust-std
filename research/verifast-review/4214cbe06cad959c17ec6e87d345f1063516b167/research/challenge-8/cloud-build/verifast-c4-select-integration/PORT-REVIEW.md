# Independent review: translator-only selector port

Reviewed 2026-10-10 before baseline dispatch. Scope: the exact
`selector-integration.patch` (`2c384f14b596c9f2713c39592ce0f414e4bdb9d994dbab7895eaa7a92eedfff0`)
applied after `tool-c4.patch` (`b33e19deec896aefad1232f982e4499dfcdef6026e09c12b9c914852d9f6beaa`).
The resulting manifest pins translator `c24b54e62cef198dda894587dc37c01a17ffeac3fd6fe234c0ef38e31d67d905`
and `src/verifast.ml`/kernel `37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`.

## Verdict

**GO for the planned baseline Cloud diagnostic on this exact port.** Static review
found no blocker to dispatching the selector-unit and C4 gates on the pinned
effective tool. This verdict does not establish that the patch compiles, that
source refinement passes, or that any proof obligation passes: compilation,
refinement, and proof results are all **unknown** until the Cloud run.

## Findings

- `selector-integration.patch` changes only
  `src/rust_frontend/vf_mir_translator/vf_mir_translator.ml`. The manifest's
  translator hash matches the reviewed effective file. The C4 `src/verifast.ml`
  hash and other profile inputs remain at their manifest pins.
- The prior C4 strict-lifetime code remains present: strict marker admission,
  full-unwind refusal, scope/CFG checks, relocation cardinality, and the C4
  bound-prefix route remain in the effective translator. The selector runner
  sets strict-cut mode off for its separate source unit, while its C4 mode sets
  strict-cut mode on. This is profile-specific routing; it provides no proof
  that strict lifetimes work in the selector unit.
- The R3 ghost-scope path is opt-in and retains the existing C4 marker handling
  after ghost-statement processing. The one rejected ghost-column hunk is
  represented by the exact `routes = 2` check after strict-relocation
  cardinality and before pending callback-marker validation. It is guarded by
  the selector's ghost-column opt-in and does not add a C4-mode route.
- The ManuallyDrop identity flag remains in the call translator once. The
  selector cleanup predicate is separate; it converts the result only for the
  exact checked pointer-drop/assume-init sites. The final successor inventory
  contains one combined guard that retains the MDnew, G1, owner, and cleanup
  predicates. No wider unwind suppression was found in that path.
- C4 and selector source/CFG identities remain separate. The selector adapter
  still checks the historical nine-body inventory and old typed call/edge
  coordinates only under its exact selector admissions. The C4 runner removes
  those parent opt-ins before the strict C4 invocation. The historical selector
  identities therefore cannot certify a C4 body or a C4-to-selector call.

## Dispatch boundary

The baseline run may now determine build, refinement, and proof behavior for
these two isolated modes on the pinned tool. Inspect the complete raw logs and
the intended first failing VC for controls; setup or refinement failures do not
count as semantic negatives. A later AST-level first-select composition is a
new delta and needs its own addressed review before its proof result can be
credited. The current port claims neither actual caller composition nor profile
acceptance.
