# R20 exact state-diagnostic adoption

Tool revision 578120769161e217e53bd569bafdccbd4b2e020e carries the reviewed
source-preserving MIR metadata, diagnostic-only context for the existing
unequal LocalAddressTaken refusal, and the previously reviewed closed-usize
constant case. The refusal context carries function identity, paired
original/verified block and command positions, complete command listings, and
the same standalone fatal diagnostic.

This revision makes CastData.sourceTy optional in the schema. The actual
exporter writes Some(exact operand type); built-in synthetic Cast fixtures
explicitly write None. Synthetic region metadata also uses identity None and an
empty region_scope_id, so it does not fabricate a body-bound inference
identity. These are serialization and fixture compatibility changes only;
they add no translator acceptance behavior. The strict RawPtr projected-place
classifier remains unchanged. Reaching the intended gate remains unproven, and
other index cases remain unsupported/inconclusive.

The exact R20 registration names the refinement-checker source, MIR schema,
and exporter. The profile pins all three source hashes. Reverting the R20
registration and tool, core, exporter, schema, and cumulative-patch pins must
reproduce the immutable R19 profile bytes and then pass the unchanged R19/R17
validators. The final ordered patch slot stays in place and contains the exact
git diff -U1 f2e92cec..57812076 artifact. The provider changes only its exact
onecell prove.py hash. The client keeps the prior R19 tuple and accepts this
exact registered tuple only.

P3's dispatched source/profile/ledger records remain historical and unchanged.
The integration does not edit caller bodies, posts, runtime, CFG, ownership
rules, lifetimes, or trusted premises. The recipe removes two uninvoked service-test inputs: r9-wiring-service-test.py
(8,325 bytes) and r11-native-receipt-service-test.py (4,698 bytes). Exact-path
searches found no invocation in run-proof.sh, run-merge.sh, merge.sh,
first-callback.py, onecell prove.py, or control.py. The active R8 wiring, R8
freshness, and tool-evidence tests remain. The R11 source-preflight and its
historical R11-INPUTS inventory remain unchanged; both removed test files
remain in the repository. The checked slice-content helper remains a separate proof
input behind its exact hash, and the parent raw-body binding remains unchanged.

Validation is synthetic profile-reversion, exact provider/pin, callback, and
phase-admission testing plus static source/hash checks. Rust/OCaml compilation,
generated decoder behavior, actual Cloud verification, and any proof acceptance
remain Cloud-UNVERIFIED. No proof credit follows from this source integration.
