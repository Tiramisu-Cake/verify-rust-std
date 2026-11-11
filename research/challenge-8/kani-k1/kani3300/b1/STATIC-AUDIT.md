# B1 static audit (no compiler execution)
Candidate: 835cb4a09c4e94ac6b531d20e68f9deee7262ce1; base: bf9c58e662fd65c64381ef2ac97a6397ffc0693a.
- Call error path reaches the common target push; one super traversal; no target reset in the error branch.
- InstanceKind match explicitly covers Item, Intrinsic, Virtual, Shim, LlvmIntrinsic.
- Removed delayed visitor locals field/initializer/assignment and LocalDecl/TerminatorKind imports; no remaining uses there.
- Removed external unsupported_call re-export; its private definition retains its internal analysis use.
- New production bindings are used; new helper is used for FnPtr/Virtual/non-Item reasons; no broad lint suppressions.
- Each of 20 fixtures has one proof harness, paired plain/seeded variant, and compile-flags: -D warnings.
- Only custom MIR fixtures permit internal_features, needed for core_intrinsics/custom_mir.
- Compiletest run_kani forwards compile-flags through RUSTFLAGS (tools/compiletest/src/runtest.rs:359).
- Supplied rustfmt wrapper check and git diff bf9c58e662..HEAD --check passed.
- Legacy golden sha256: 7008546b9c6963fdc4e6c0507852732014aaf7abf7ef05423d7a9c0806d9e89c, unchanged.
The research packet preserves exact unified-diff bytes; its scoped .gitattributes permits blank context lines only in review-packet/diff.patch.
This is a source audit, not a successful -D warnings compilation or executed regression result.
