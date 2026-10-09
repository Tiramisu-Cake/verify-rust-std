# C2 discovery runner review

`SORT4_C2_DISCOVERY=0` is the default. The fixed Cloud environment does not
carry custom variables, so the transported profile field
`cloud_discovery_enabled` is the exact Boolean opt-in; a missing field defaults
to false. An explicit environment value of `0` overrides a true profile flag.
An explicit `1` is also accepted only when the reviewed profile flag is true.
Any effective opt-in requires the profile's exact C2 diagnostic-only
classification, `profile_accepted=false`, and
`always_reject_after_original_ast_emit=true`. The resolved activation and
profile hash are recorded in `c2-activation.json`. This allows a reviewed
profile-only opt-in without changing shared coordinators or providers.

The existing C1 baseline, strict controls, full-target control, and
bounded-prefix proof keep the same inputs and environment. C2 runs only after
that invocation has a confirmed `PREFIX_ONLY_BOUNDED_C1_THEOREM`, with VF0,
normal/direct-unwind posts, return, leak, dead-code, and helper gates. The
result remains `C2_DISCOVERY_ONLY_NOT_PROOF`; it cannot set
`actual_sort4_proved`, `full_body_exit_zero`, or `full_summary`.

The driver copies the fresh C1 fixture and replaces only its unique original
second comparator statement and its line ending with the C2 annotation draft,
so the splice does not add a blank source line. It checks the
base-verified, original-runtime, draft, and resulting ECD83 source hashes,
requires ghost stripping to recover the original source bytes exactly, and
checks the pinned marker/cut/call lines. The source-pair hashes are written to
`c2-source-certificate.json`; existing evidence is not changed.

The C2 translator delta is applied to the already-built isolated C1 translator
after checking the profile and patch hashes and the exact base-translator hash.
The delta must touch only `vf_mir_translator.ml`. Cloud rebuild checks retain
the existing kernel, effective Rust specification, proof library, all other
critical files, and all other binaries. C2 discovery uses the exact capture
environment: C1 prefix off, C1 Output equality off, strict lifetime cuts on,
and one `sort4_stable` body with unwind and full checks enabled.

Before the intentional rejection, Cloud exports and decodes complete normal
and readonly MIR and runs refinement on the ghost-annotated fixture. Both
complete target records, raw and decoded artifacts, graph inventories, and
their hashes are retained. Those records are source/MIR support evidence;
they are not a projected proof. The complete-graph inventory checks a unique
target function record and five comparator calls, but it does not claim a
source-to-MIR C2 operand or unwind correspondence. Such correspondence
requires separate review of the retained full records before any projection
could be designed. Before this capture, one fresh C1 bounded-prefix positive
is rerun with C2 explicitly off on a copy of the original C1 fixture; it must
match the prior source/pre-AST/post-AST pins and pass the C1 full checks.

The translator then emits the original
declaration to the pinned `actual-c2-original-ast.ml` and fails with the exact
profiled `DISCOVERY_ONLY_NOT_PROOF` marker. The collector copies and hashes
only a fresh nonempty AST from that invocation and requires the AST inventory
to show five `FnMut::call_mut` calls, eight selectors, four copies, and the
source-223 C2 callback. No projected AST or proof result is accepted.

A separate disposable source mutant reverses the C2 operands. The exact
profiled verified-source-hash refusal must occur before AST output or target
body proof entry. Any changed diagnostic, missing output, incomplete source/MIR
inventory, unpinned translator input, or unexpected source identity stays
inconclusive. The driver does not infer caller applicability, prove C2,
establish a callable/full-function summary, or create proof credit.

The profile and patch are experimental, default-off diagnostic inputs only.
This runner does not alter the compiler, specification, kernel, or live
evidence. It runs only in the assigned Cloud lane; local checks are limited to
Python syntax and pure byte/AST classifiers.
