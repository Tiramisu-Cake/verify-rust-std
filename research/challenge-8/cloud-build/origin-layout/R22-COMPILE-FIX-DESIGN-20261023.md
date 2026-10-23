# R22 compile-fix admission extension

R22 P1 on source `dd4a2dd2` using tool578 / profile9496 stopped in exporter compilation before
proof (`proof_attempted=false`). The Evidence Brief reported two Rust compile
errors in `vf_mir_exporter/src/lib.rs`:

- E0382: the `ReErased` arm consumed the region Cap’n Proto builder with
  `init_identity()` before the following `set_id()` call. The fix reborrows
  the builder before initializing the erased identity.
- E0433: `pointer_coercion_data_cpn` was used without importing the generated
  `pointer_coercion_data` module. The fix adds that exact module alias.

The reviewed, published candidate is tool commit
`e1ee4415b711d1b368cbfaad27bda88ed0a216e1`, two commits after tool578. The
exporter SHA-256 is
`0b456d055d498429c3da5bd4b7a1eb455b1b691bb0133a5f61bb449aad4e4345`. The
existing cumulative patch and first 18 ordered patches remain intact. The
exact `git diff` from tool578 to e1ee is appended to the cumulative patch;
patch SHA-256:
`0ffeb7464c7f0ef96bb0f29f0d144a5cd1a1ad1cad5c967e3d726b0cc49855e7`. Replaying
all 19 ordered patches from profile baseline
`f76012fb518703b1d98e243ac4f487f16877cfcb` reproduced all changed tool files
byte-for-byte at e1ee.

This creates an R22 extension to profile
`experimental-merge-label-storage-r11-v1`; the profile name stays unchanged so
existing runner/profile routing remains applicable. Its only tool source path
is the exporter. The extension records both compile-only edits and
asserts no schema, emitted MIR, refinement, proof, runtime, CFG, postcondition,
or control change. R22 admission accepts either the unchanged initial tuple
(tool578/profile9496/original provider and patch) or this exact extension
(e1ee/profile registration/cumulative patch/registered provider). No other tuple or
historical profile is reclassified.

Reversing the R22 profile's registration, effective tool,
exporter pin, patch pin, and final ordered-patch entry reproduces the original
profile9496 bytes exactly. R19 and R20 validators/constants remain unchanged;
their original profile/provider paths continue to use their existing exact
checks. The R22 provider entry preserves the existing R11 control files and
pins the R22-specific `prove.py` profile admission at
`582a5f985353d648a08f391a34f50ccd2e387c0693ffa4c0d2ab0fcde2dc650a`. Its
actual profile admission now recognizes the exact R22 registration, reverses
it to byte-exact profile9496, then passes that profile through unchanged R20
admission. The R22 provider uses an internal selector only to choose exact
source pins; the transformed runner receives the public R11 profile name.
The exact R22 provider module SHA-256 is
`5b60c22b36d564c0b7d5089e4be7168848c1c5cb5b873c071bc208134f604b48`.

Candidate profile SHA-256:
`5fd081ec48a07354d9158bd7f4c09c9be88fa72519d8849943a612705c1e452e`.

Validation is static and synthetic in this worktree. It does not run the Rust
compiler, exporter, MIR preparation, verifier, or Cloud Build. R22 P1's
compile-only failure remains historical and receives no proof credit.


## P2 translator compile-fix tuple

The first R22 compile-fix candidate (tool `e1ee4415`) remained compile-only but its P2 Build `fb2529be` still failed during translator compilation: three synthetic `Lifetime` records omitted the generated `identity` field. The Brief reported exporter/decoder errors 0, translator errors 1, and `proof_attempted=false`. That Build added no proof credit. Its Build, review, and ledger records remain historical; this selected candidate supersedes only the effective R22 admission tuple.

The new exact candidate is tool commit `65f0bb35e4f188cf8ce405a67253127173c5c3a1`, parented on the reviewed `e1ee4415` candidate. Its only delta is three synthetic translator fixtures assigning `identity=Nothing` (translator SHA-256 `e5fe47a16b1a94dcfd07d7d7c0355d4e5acb999650f00498d11606909960dde2`). The exporter remains `0b456d055d498429c3da5bd4b7a1eb455b1b691bb0133a5f61bb449aad4e4345`. The cumulative patch appends the exact e1ee-to-65f translator diff to the established patch; source replay must match the exact 65f tool blobs. This extends the same R22 registration and public R11 profile name with both affected source paths; it does not introduce a third accepted tuple or change runtime/phase/control gates.

R22 admission pins the exact registration, tool commit, exporter and translator source hashes, cumulative patch and profile bytes. Reversal restores both exporter and translator hashes, tool578, and the original profile9496 patch before calling unchanged R20/R19 admission. The historical tool578/profile9496 tuple remains admitted independently. The earlier e1ee tuple is not a current alternative.


## Exact transport-only recipe removal

The selected R22 source pack exceeded the fixed 571567-byte transport cap after the translator tuple and admission gates were added. To recover transport headroom, R22 removes only `research/challenge-8/cloud-build/origin-layout/R11-INPUTS-20261021.json` from `proof_paths`; the file remains unchanged in Git. The selected `.py`/`.sh` closure was checked for literal consumers and has none. References found outside that closure are the obsolete `r11-source-preflight.py` and offline historical R11/R20 tests. The live `prove.py` reads `R11-START-20261021.json`, which remains in the selected recipe. The R22 service test asserts this exact path delta and retained START input. No runtime, control, test, profile, ledger, or other recipe input was removed.
