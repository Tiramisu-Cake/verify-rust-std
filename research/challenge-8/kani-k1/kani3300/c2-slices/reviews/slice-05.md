# Slice05 CLOSURE — worker15 read-only review

**PASS_STATIC_ONLY; exact-head native qualification and S5 sensitivity4/4 NOT_RUN.**
Reviewed source `96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f`, tree
`445fe95f622016728286e2b820c52b626809923b`, parent accepted4
`345cedfd67df679e326474385308349d609fc43d` / run43710024495.
Input packet g0 `7551f71dc20e3b2c464bbb5818df5ee29eb51d1c`. Worker14 source untouched.
No actionable source finding within the requested slice5 scope.

Production changes exactly two owner5 parts in `ty_layout.rs::data_bytes_for_ty`, +28/-1;
94 added test paths form47 complete unchanged-F input/golden pairs. No docs delta:
the canonical DOCS-MAP assigns no added segment to5. No6/7 hunk or fixture imported.
The resulting layout blob equals F; every other production file equals accepted4,
including the existing explicit pre-F7 writer/import adaptation.

The sized size0 Closure arm returns no data bytes. Nonzero Closure environments use the
same monomorphized `args.as_closure().upvar_tys()` as `codegen_ty_closure`. Public `Ty`
converts to internal inside TLS; each capture converts back to public `Ty` before the TLS
scope exits. Recursion happens outside that scope, through the unchanged three-argument
mask helper and existing error propagation. Imports, signatures, generic parameters,
fields, impl headers and reexports are unchanged; conversion imports belong to ancestor2.

Capture count must match actual closure field-offset count. The closure's own
`fields_by_offset_order()` supplies logical indices into BOTH captures and offsets;
`current_offset + offsets[idx]` preserves the enclosing offset once. No tuple-layout
substitution and no all-true environment mask. Recursive masks retain padding and
union/unsupported errors; references describe pointer bytes, not blanket pointee admission.
Aligned-ZST, padded/reordered/mixed/nested captures, nonzero enclosing offsets, reference,
raw, MU-value/reference, unit and union boundary fixtures have useful legal and negative
oracles. They require no stage6 feature or F7 isolation API statically.

Independent seam check [SEAM-VALIDATION](../ci/slice-05/SEAM-VALIDATION.json) passed over
all48 changed Rust files, with48 explicit call contracts and no errors. The contracts
inherit accepted4, increase recursive-mask count12→13 and bind the new TLS/conversion/
upvar chain; worker15 inspected their exact arguments, type context, indices and caller.
Ten synthetic checker tests passed. This bounded checker does not resolve Rust traits,
expand macros, typecheck, establish MIR binding or prove compilation; native CI remains
required. Worker14's prior seam report was not substituted for this worker15 run.

[Source validation](../ci/slice-05/SOURCE-VALIDATION.json) independently reconstructed
accepted ancestors and owner5 extraction, checked all897 manifest identities, all413
unchanged inherited selectors and all201 currently present expected/uninit inputs.
New47 pairs exactly equal both owner1 head5 obligations and accepted4's deferred list;
`marker-hook-calls/generated-modifies-no-shadow` is included with its useful payload7
SUCCESS oracle. All8 strong cases,7 mode fixtures and7 composition roots are present.
Recursive ordinary/check retain exactly the accepted cycle Unsupported; simple-check
remains legal. The two Replace files retain local PFC companions and exact caller
selection; companion presence is not an execution receipt.

Independent Luna HIGH read-only fixture review found no6/7 dependency or actionable
oracle issue; [FIXTURE-REVIEW](../ci/slice-05/FIXTURE-REVIEW.json) records scope and limits.
S5's four original test-only mutation patches match their expected source hashes and
intended missing assertion / extra failure / repaired write / inverted-count mismatches.
Clean controls must pass before independent forced reruns. A compile failure, timeout,
early Unsupported or bare compiletest nonzero exit never qualifies as detection.

The [CI request](../ci/slice-05/CI-REQUEST.md) asks for the accepted4 recipe on this exact
source, cumulative460 selectors (451 passes +9 existing ignores if green), all68 compiler
units plus explicit9/9/1/1 relevant groups, all47 target pairs and sensitivity4/4. No fixture
flags/goldens/solver/checks were weakened. Source before/after and always-upload evidence
are mandatory; mutation trials restore source after each independent test-only overlay.

**All deferred-on5 integration obligations remain PENDING until explicit per-fixture
native results on this cumulative head.** The CI request carries their source-part/hash
provenance; future acceptance must say “integration-tested on head5” for owner1/4 and
preserve historical early-head records. Aggregate exit0, static checks and fixture
presence do not close them. Existing accepted4 obligations remain as recorded.
No local native builds, push, dispatch, Gate A or independent formal proof credit.
