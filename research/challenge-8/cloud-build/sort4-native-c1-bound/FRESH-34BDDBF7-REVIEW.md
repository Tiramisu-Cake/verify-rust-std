# Corrected prepared diagnostic — fresh partial boundary, no composition

Build34bddbf7-e536-4ef0-bb7f-82e07ef439fc, proof=infra
16bbfa6c7f4340e0643426560c4ff33531aff370. Create22:07:21.990981660Z;
finish22:13:23.959958Z; charged362seconds. Canonical evidence integrity verified;
archive025e9cc17cf3f2410e83af905624651eb5ab643ad04932bed7183c494113ffc7.
Frozen effective translator1eab6eb54fe5c23d53ca72a6d9dfcbbff09c09ffaf26c48a4f450f5068a8d313,
kernel37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c,
console8d686fef29ae6fe5b6adb91a946ff9942aef682baf934b273cc61d71a625527b,
HEADf76012fb518703b1d98e243ac4f487f16877cfcb.

Both cases normal/readonly export/decode and refinement exit0. Helpers precede
native target. Prepared source owns source4/tail/F/thread/types and opaque MU
from automatic native safe-reference resources; strict lifetime entry passes.
Positive reaches Args.own assertions189 and preserved F/thread/MU190–194,
then refuses198 at reverse packaging `open own::<&'cmp T>(t)(left_ref)`:
`No matching heap chunks: [_]own0(ref_typeid(typeid_of_lft(cmp_k), T_typeid), _t)(left_ref)`.
No full normal post/cut/return/free/leak PASS: preparation is a partial boundary.
FalseArgs reaches intended190 `Assertion might not hold. (Cannot prove false.)`
after Args.own189. This is a fresh intended preparation negative, not a callback
normal/unwind negative. No actual comparator was invoked in either case.

No strict-entry observer is required by this result; its card remains DRAFT.
Reverse ref-own adapter is not assumed: actual FnMut consumes Args.own. Review
supports proceeding to real source-bound C1, whose separate complete native
normal/direct-unwind posts remain NOT_RUN/NOT_PROVED until fresh verification.
