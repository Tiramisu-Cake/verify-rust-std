# Coordinator diagnostic request — STOP, no dispatch performed

Input: exact S5 source 8d67298c48eb7b2381f806a6353433d1440e3d94 / tree
5fb7dbaa6f79a75ca552be9d4d5c7b535cf38058. These are research-only diagnostic overlays,
not an S6 frozen candidate or normal-suite acceptance request. File SHA256 identities
are in MANIFEST.json. Preserve pinned dependencies and all checks.

First observe `repro/ordinary-hook-return.rs` on that exact source using existing
bounded Linux targeted infrastructure. Use source kani-flags before --cbmc-args,
regular output and --object-bits 12. Capture actual instantiated callee kind/body,
FnAbi, generated MIR call/destination/normal target, marker-selected UntrackedDeref
interception, protocol begin/store/load behavior, all native failed descriptions,
exact check summary N, reached useful checks, exits and source/tool/tree identities.
Do not bless any failure or create a guessed expected file. If a prior analysis or
layout failure dominates, record NONDISCRIMINATING and preserve the exact output.
Add initialized ordinary bodyful MU argument/return companion for comparison
(existing `maybe-uninit-argument-return` / `transfer-qualification/legal-ordinary`).

Observe `generated-modifies-no-shadow.rs` and invalid-target separately only if
needed to confirm the source type-shape analysis; setup failures are not semantic
qualification. Confirm whether a selected PFC actually executes a hook call.

For Fn-item candidates capture optimized FnDef callee kind and ABI. Plain has no
predetermined native outcome; shadow-return can qualify Shim refusal only if that
actual Shim is reached, with no prior tuple/layout failure. Reuse existing forced
fn-pointer selectors as the distinct indirect control. Actual --force-rerun is
required for repeated selectors; ignored/cached results are not qualification.

Do not run partial-source-tests as accepted fixtures: they are incomplete drafts
with known static/golden issues listed in REVIEW.md. No full regression, Gate A,
SmallSort/SEL1 replay or gate workflow belongs to this diagnostic request.

After a corrected control design and a new reviewed source candidate, the original
S6 targeted fmt/build/clippy, units6/2/9, all Uninit/expected/ui/script and remaining
json-handler, four unchanged S5 sensitivity patches (actual --force-rerun), and the
same bounded Linux Quick remain required. S5 receipts do not qualify that new SHA.
Gate A three-platform remains a separate later task, NOT_RUN.
