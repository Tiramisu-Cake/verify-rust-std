# R20 exact state-diagnostic adoption

Tool revision 37b834280a3910d58c46ea4b1c6e73265287ff3e supersedes the
metadata-only candidate for the next exact R20 source tuple. It carries the
reviewed source-preserving MIR fields and adds diagnostic context to the
existing unequal LocalAddressTaken state refusal: function identity, paired
original/verified block and command positions, complete command listings, and
the existing standalone fatal diagnostic. It does not change the comparison,
restart, acceptance, or failure-classification rules. The diagnostic does not
supply state equality or proof evidence.

The exact R20 registration names the refinement-checker source together with
the MIR schema and exporter. The profile also pins the refinement-checker
source hash. Reverting the R20 registration and tool, core, exporter, schema,
and cumulative-patch pins must reproduce the immutable R19 profile bytes and
then pass the unchanged R19/R17 validators. The final ordered patch slot stays
in place and contains the exact git diff -U1 f2e92cec..37b83428 artifact.
The provider changes only its exact onecell prove.py hash. The client keeps the
prior R19 tuple and accepts this exact registered tuple only.

P3's dispatched source/profile/ledger records remain historical and unchanged.
This integration does not edit proof inputs, caller bodies, posts, runtime,
CFG, ownership rules, lifetimes, translator acceptance, memory model, or
trusted premises. The recipe also removes the dormant r9-wiring-service-test.py input (8,325 bytes). An exact-path search found no invocation in run-proof.sh, run-merge.sh, merge.sh, first-callback.py, onecell prove.py, or control.py; active merge.sh explicitly invokes and retains the R8 wiring/freshness and tool-evidence service tests. The removed file remains in the repository.

The checked slice-content helper remains a distinct proof
input behind its exact hash; the existing parent raw body binding remains
unchanged.

Validation is synthetic profile-reversion, exact provider/pin, callback, and
phase-admission testing plus static source/hash checks. Rust/OCaml compilation,
generated decoder behavior, actual Cloud verification, and any proof acceptance
remain Cloud-UNVERIFIED. No proof credit follows from this source integration.
