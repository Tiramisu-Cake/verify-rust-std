# R20 exact state-diagnostic adoption

Tool revision 1fec4ffa55703fc571c6eb82d96072596325d647 supersedes the
6eb7e5bb candidate for the next exact R20 source tuple. It retains the
source-preserving MIR metadata and diagnostic-only context for the existing
unequal LocalAddressTaken refusal. That context carries the function identity,
paired original/verified block and command positions, complete command
listings, and the same standalone fatal diagnostic.

The additional interpreter behavior is narrowly limited to closed usize
typesystem constants: Value with a Leaf, matching outer/value UIntPtrWidth
types, scalar sizes from one through eight bytes, and bits fitting that size.
Other typesystem constant forms remain unsupported. The strict RawPtr projected
place classifier is unchanged, so reaching the intended gate remains
unproven and other index cases remain unsupported/inconclusive. This does not
add pointer, resource, lifetime, provenance, or memory-model rules.

The exact R20 registration names the refinement-checker source together with
the MIR schema and exporter. The final tool revision also removes an unused
mutable binding in the exporter; this is a compile-warning correction with no
serialized or semantic change. The profile pins the refinement-checker source
hash. Reverting the R20 registration and tool, core, exporter, schema, and
cumulative-patch pins must reproduce the immutable R19 profile bytes and then
pass the unchanged R19/R17 validators. The final ordered patch slot stays in
place and contains the exact git diff -U1 f2e92cec..1fec4ffa artifact. The
provider changes only its exact onecell prove.py hash. The client keeps the
prior R19 tuple and accepts this exact registered tuple only.

P3's dispatched source/profile/ledger records remain historical and unchanged.
The integration does not edit proof inputs, caller bodies, posts, runtime, CFG,
ownership rules, lifetimes, or trusted premises. The recipe removes the dormant
r9-wiring-service-test.py input (8,325 bytes). An exact-path search found no
invocation in run-proof.sh, run-merge.sh, merge.sh, first-callback.py, onecell
prove.py, or control.py; active merge.sh explicitly invokes and retains the R8
wiring/freshness and tool-evidence service tests. The removed file remains in
the repository. The checked slice-content helper remains a separate proof
input behind its exact hash, and the parent raw-body binding remains unchanged.

Validation is synthetic profile-reversion, exact provider/pin, callback, and
phase-admission testing plus static source/hash checks. Rust/OCaml compilation,
generated decoder behavior, actual Cloud verification, and any proof acceptance
remain Cloud-UNVERIFIED. No proof credit follows from this source integration.
