# KANI3300 C1-T coordinator request (NOT_RUN)

- Baseline 6134e42dd1c65dc980336e7d9455aba02d423edf + exact test-only commit 28e684cbae348130d559b87e030536d8f8a3c1ff; tree 9e6645a470702d774ccf874074cbac325fa46371.
- Then M1 + the SAME twelve files, paths and SHA256 from TEST-MANIFEST.json. Worker 14 imports this exact commit unchanged (or coordinator composes it); verify all path/hash identities after import. No parallel fixture edits.
- Use existing Uninit Quick coordinator process; no new workflow/framework/runner/adapter. C1-L compile-only runner is cancelled; a8f6b7196a remains historical. No CI was dispatched or awaited here; Cloud $0.

## Six selectors (each has one harness)
- `tests/expected/uninit/promoted-allocations/direct-legal.rs` → `promoted_direct_legal`.
- `tests/expected/uninit/promoted-allocations/direct-left-hole.rs` → `promoted_direct_left_hole`.
- `tests/expected/uninit/promoted-allocations/direct-right-hole.rs` → `promoted_direct_right_hole`.
- `tests/expected/uninit/promoted-allocations/helper-legal.rs` → `promoted_helper_legal`.
- `tests/expected/uninit/promoted-allocations/helper-left-hole.rs` → `promoted_helper_left_hole`.
- `tests/expected/uninit/promoted-allocations/helper-right-hole.rs` → `promoted_helper_right_hole`.

## Required observations and acceptance

1. Freeze baseline/M1 production, test commit/tree and per-file SHA256, tool/configuration identities and exact selected harness. Distinguish setup, compiler, solver, harness verdict and golden matching (including NOT_RUN at unreached stages). A setup/compile error is not a semantic result.
2. If needed, coordinator adds --emit=mir in existing Quick and performs targeted property inspection. Establish retained raw_eq and full three-byte reads; actual promoted GlobalAlloc referents, caller carrier provenance/addends, offsets/extent, actual Some/None masks before unwrap_or(0), emitted symbols/layout and aliases/coalescing for BOTH operands. Do not infer Some(0)/None or coalescing from GOTO zero data. Bind helper caller arguments through compare into raw_eq. Source spelling alone proves none of these.
3. Record exact property IDs, descriptions, locations and reached outcomes for BOTH operand byte checks, plus equality assertion on legal selectors. Name ALL extra safety/Unsupported failures. Early validity/layout/Unsupported or an unrelated failure cannot satisfy a hole control. No fabricated IDs, inferred type spelling or lowering details in goldens; refine only from observed details through the fixture owner.
4. Corrected-model semantics and goldens are identical on both revisions: legal requires both checks reached SUCCESS, equality true and harness SUCCESSFUL; left hole requires offset-0 left read FAILURE and right check reached SUCCESS; right hole requires offset-2 right read FAILURE and left check reached SUCCESS. No earlier UB or extra new safety/Unsupported failures on M1. If a check is unreachable/not emitted/unbound, report that limitation, not acceptance.
5. On baseline legal may falsely fail and hole selectors may already report FAILURE. Preserve exact per-check outcomes and extra failures as repro evidence. A fully initialized promoted operand may also falsely fail. Thus negative golden match, overall FAIL or whole-Quick aggregate cannot establish intended operand. Do not promise all baseline negative selectors match; do not weaken corrected-model goldens to accept false/extra failures. Baseline known failures are repro, not whole-Quick PASS.
6. Initial negative goldens use only the existing uninit-read diagnostic prefix (type suffix and IDs NOT_RUN). They do not exclude unrelated/extra errors. Golden matching is necessary output checking, not sufficient contract acceptance. Pair it with the property/binding observations above; retain observed results separately from semantic expectations. No new input has compile/runtime/proof credit from this package.

Report via the existing authorized evidence interface. Return fixture findings to C1-T owner through coordinator; worker 14 must preserve these fixtures byte-for-byte. D0 and existing raw-eq/other controls stay outside this twelve-file commit; their later CI matrix remains coordinator/M1 scope.
