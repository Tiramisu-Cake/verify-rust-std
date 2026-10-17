# A1 Cloud tool reconstruction helper (UNRUN)

`a1-tool.py` is an import-inert Cloud Build helper. Its sole entry point,
`reconstruct(a, c4, audit, driver, manifest, profile)`, requires the exact A1
phase, provider, opt-in, Cloud Build IDs, shared deadline and `/workspace`
paths. It creates one isolated copy of the pinned production tool source. It
does not submit or monitor a Build and never reads prior raw evidence.

The committed source chain is reproducible without a `/tmp` translator:

1. Three strict lifetime patches from `CALLER-ENTRY-MANIFEST.json`.
2. Ten C4 historical patches from the pinned `selected-runtime.py` table,
   checked against their committed per-step profiles and frozen C4 snapshot.
3. Native C1 capture, C1 bound, C4 combined, ZST size, and dead-code identity
   patches, checked against their committed profiles and the selected base
   source snapshot.
4. The committed slice `as_mut_ptr`, stable threshold, and selected branch
   binding patches. `SELECTED-BRANCH-BINDING-PINS.json` fixes the result to
   translator SHA-256
   `e484d9f95202c876957a5d5ab349c6a40bc04dbcf813db4b373819402d807e64`.
5. The A1 R and C patches, each guarded by exact patch SHA and complete
   affected-file input/result hashes supplied by the new A1 profile.

The old `driver.reconstruct()` builds an intermediate console, so this helper
mirrors its patch and source-snapshot checks but skips that build. It invokes
one final Make stage with `build-vf-rust-mir-exporter ../bin/verifast`, which
builds the Rust exporter and Dune console after both A1 patches. Each consumes
the changed Cap'n Proto schema through its existing build path. The stage uses the same `a.deadline_epoch` as
the rest of the Build and caps itself at 900 seconds. Frozen kernel, parser,
specifications, proof std source, other binaries and source modifications are
checked before and after compilation. The existing production tree must remain
unchanged. The receipt records source and binary hashes without claiming proof.

Required A1 profile fields: `phase_id`, `tool_head`, `kernel_sha256`,
`selected_base_translator_sha256`, `profile_accepted=false`,
`caller_manifest_sha256`, `caller_driver_sha256`,
`stable_threshold_pins_sha256`, `r_patch_sha256`, `c_patch_sha256`, and
`r_before`, `r_after`, `c_before`, `c_after` hash maps. R maps must contain the
translator, schema and exporter paths. C maps repeat those paths, enforce the
R result as their input, and require unchanged schema/exporter hashes.
The runner must pin this helper and the new A1 profile before invoking it.

Only Python AST syntax parsing was done locally. No imports, tool build,
source extraction, verifier, proof runner, or Cloud job were executed. The
exact build result and compiler API compatibility remain UNRUN Cloud gates.
