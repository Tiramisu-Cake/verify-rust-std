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
`504b1e067bf269a77053ee4f701ba6a914d1854868a0d33cfc35736db736c6bd`. The exact
R22 provider module SHA-256 is
`913a5ea847038bd6acb3ee21fa82688bc22f3348a8265080dfb75d1a35eebba1`.

Candidate profile SHA-256:
`5fd081ec48a07354d9158bd7f4c09c9be88fa72519d8849943a612705c1e452e`.

Validation is static and synthetic in this worktree. It does not run the Rust
compiler, exporter, MIR preparation, verifier, or Cloud Build. R22 P1's
compile-only failure remains historical and receives no proof credit.
