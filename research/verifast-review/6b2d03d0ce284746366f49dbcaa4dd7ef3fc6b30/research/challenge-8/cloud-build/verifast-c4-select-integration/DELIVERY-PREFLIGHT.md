# Cloud source preparation preflight

The `source-prepare` stage runs immediately after the existing input preflight,
before package installation, downloads, Rust toolchain setup, or VeriFast build.
It imports and executes the pinned Python source preparers against the restored
30-module pack, checks the resulting selector/C4 source hashes, and materializes
the source-only gate fixtures in a dedicated
`allprooflogs/source-preparation/` directory. This exposes Python import and
fixture-construction failures before compiler/tool setup starts.

The fixture inventory includes strict-lifetime cases, outer-bound escape,
pointer-value cases, pinned ManuallyDrop fixtures, source/contract admission
mutants, and the source half of the composition case. It does not run Cargo,
rustc, the MIR exporter, the refinement checker, or VeriFast. The composition
AST and tool-dependent diagnostic cases remain for the later verifier stages.
The later run keeps using `cases/integration/`, so its mutable fixture paths do
not collide with the preflight evidence. This stage is preparation evidence
only and grants no proof credit.
