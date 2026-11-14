# Independent S3 static review

Reviewer: GPT-6 Luna HIGH, isolated context, no nested delegation, no edits,
no compiler/build/test/verifier/CI execution. This is a static review only.

Final candidate `86428e9313a8a697482bfd092de61a735a716961`, tree
`146049f153dd5410d8be7a812b071147c64c2cd0`, baseline
`bf8170b28afb682f8dd55a94199caa247736d8fa`.

Final packet: review-packet-final; canonical spec SHA256
`5cb2d32da653131c7cccb72bc508b37601a80a740d9ecabc697cc59b725404a4`;
packet SHA256 `ee7224caa3b049cb4e92ffa5037214e47e2020e1f96678180dba57bed360cc7b`.
Reviewer ran smallsort-session review check against the supplied candidate/spec
identities: PASS. Committed diff whitespace check: PASS.

## Finding and correction

Initial candidate 15ede35f3f6809e79a869d33482f7fc6034464f5 consumers read
Nested.marker. A nested callee has no shadow entry LoadArgument; full caller
source reset therefore risked an unrelated marker-read failure. The reviewer
required isolating the intended payload read. This was a potential extra-failure
and oracle ambiguity concern, not observed verifier behavior.

Correction 86428e9 makes moved-source consumers custom MIR bodies containing
only Return; fieldwise-return helpers write constant marker 0. Call(Move(source))
and the saved-pointer post-call payload read remain explicit. The same reviewer
checked this delta and confirmed the finding addressed. Production source and
its semantic dependencies were unchanged from the initial reviewed candidate.

## Static conclusions

No remaining source correctness finding from this review. The specific
UnionAsField classifier, exclusion of supported carriers, snapshot/reset order,
exact-place full-storage extent, normal-continuation destination reset, and
accepted Item/Shim/foreign/black_box route dispositions are coherent by source
inspection. Existing supported transfer protocol and early Unsupported paths
were preserved.

The classifier checks layout().is_ok(), not is_sized(); exact from_ty error is
still required. If an unsized nested slice classifies, for_deinit's new explicit
is_sized check reaches the existing unsupported-size boundary. Unknown extent
is not synthesized with size zero. Rust borrow/type review found no evident
source error, but no compiler typecheck occurred.

The corrected custom MIR is structurally plausible, including fieldwise nested
construction/return, simple Call operands, empty consuming helpers and actual
Move spelling. Compiler acceptance, consumed MIR, object/extent binding and
optimizer/model retention remain unverified. Marker fields have local
dead_code allowance for their storage-layout role, not disabled safety checks.

## Explicit limits

Source/static approval only. Baseline test-only patch apply/tree/blob checks
were established mechanically by the main worker; the reviewer did not
independently execute baseline tests. Both false-success/intended-failure pairs,
exact emitted failure/duplicate counts, all legal controls, fmt/build/clippy and
Quick remain NOT_RUN/UNKNOWN. No reproduction, empirical repair acceptance,
docs narrowing, B1/B2 or independent proof credit follows from this review.
