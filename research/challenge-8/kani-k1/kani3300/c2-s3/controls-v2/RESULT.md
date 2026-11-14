# S3 test-only controls v2

READY `5ca3cbf2e913e9c9b1d81cad3bce598964bafeac`

Candidate tree `2b036a185f635a377992d616a132fac8ba7d096d`; parent
`86428e9313a8a697482bfd092de61a735a716961`. Only six files in
tests/expected/uninit/nested-aggregate-reset changed. Production, docs, runtime,
existing controls, composition and all base/pins are unchanged. Author and
committer Tiramisu-Cake <igkharin@gmail.com> via git -c. Clean source worktree.

The old controls are NONDISCRIMINATING: provided baseline run 43611505688 and
candidate run 43611509452 each fail all three fixtures on the existing
pointers-to-Nested/UnionAsField Unsupported check before the intended read.
The reinit fixture also fails. These results give no F6 reproduction or repair
credit. User-reported remaining candidate results are expected210 ok, kani24/0,
ui17/0, script2/0; composition remains S5. Prior records/CI excerpts are retained.

## Revised shape

The nested payload is now ordinary union Slot { byte:u8, hole:() }, within the
same nested-union F6 boundary. All test pointers are directly *const/*mut u8;
there is no pointer/reference to Nested or Slot, pointer cast, MaybeUninit API,
copy intrinsic, raw_eq or whole-Nested assignment. Fieldwise custom MIR builds
and returns the aggregate. No check/guard is disabled.

Repeated destination: seed its slot, save the u8 address before the first Call,
then use the same destination for initialized and hole returns. Both calls
take a top-level Slot argument and return Nested, isolating the nested return
boundary. Only the retained pointer reads the payload after the second return;
there is no later address-taking setter to reinitialize its shadow.

Moved source: fieldwise build a non-Copy Nested, save its u8 field address, then
explicit Call(consume_nested(Move(source))). The consumer is empty custom MIR.
Afterward the saved pointer reads the original live source storage, never a
callee copy or return temporary. No StorageDead is added.

Reinit: both paths write through the pre-call *mut u8 address after the nested
return/Move, then read back 55/77 with own assertions. The negative oracle pins
one failure at raw read_payload's `*const u8` read; the legal oracle pins zero.
These are provisional source oracles, not observed new property counts.

## New baseline package

Apply baseline-tests.patch to exact bf8170b28afb682f8dd55a94199caa247736d8fa.
SHA256 `f93a436385b739261459853b0d173ad9afe343d2dd26cd960e5be18fc2cf2f05`.
Expected tree `1356cb004836d69fa0c234801e9c0600a7146167`, also supplied as
expected-baseline-tree.txt. Only the six new tests/oracles are present; all
fixture blobs/flags match this candidate byte-for-byte.

candidate-tests-delta.patch applies only the six test changes on 86428e9313.
Both patches passed temporary-index apply/check and exact tree/blob comparisons.
Allowed rustfmt, committed git diff --check and targeted static source scans
passed. The static shape audit and its limits are in REVIEW.md.

No build/compiler/test/push/CI run occurred. New baseline false successes,
candidate intended failures, exact counts, actual consumed MIR, field offsets,
storage identity, reachability and discrimination remain NOT_RUN/UNKNOWN.
Next execution must establish both pairs; a repeated Unsupported is not credit.
Research remains uncommitted in this directory. No docs narrowing or F6
acceptance is asserted.
