# Merge / insert_tail — limited third session CLOSED

Both actual first shared references now pass `ref_precreated_token` and `ref_initialized` obligations from the original three-cell array and owners. The verifier reaches the first FnMut at `verified/lib.rs(185,13-77)`. Callback resource restoration remains unproved.

First causal blocker: full first Continue-unwind post at `verified/lib.rs(130,16-19)` lacks `array<u64>(begin, 3, _)`. AST routes the callback unwind to `ReturnStmt(unwinding)` before loan/lifetime recovery. Neither normal recovery block executes. Concrete-u64 HRTB registration remains0; late callback, updated gap and cleanup are not reached. No normal/unwind F/frame/full-post credit. Full body/posts preserved; no new entry premises or trusted semantics.

B1 regression **PASS within the previous bounded normal domain**: positive, six proof negatives, ten admission, four receiver/end/retirement, helpers and mandatory normal/unwind regressions matched. **B2 NOT ACHIEVED** under PROGRESS-REVIEW; index15% unchanged.

Build `30bce9a0-29e8-4535-9060-ee6d9df2dccc`, rawFAILURE; proof=infra `9e15014b5c62f94eb797e044d1f4ca9bd8cb74f1`. Frozen tool `a158398e336edce9817f62a55733a3470a986d7b`; profile `0e67b038f940a9892dcb840747fbcc340532a31649979601af545acc41a0c68b`, EXPERIMENTAL/NOT_ACCEPTED/NOT_FOR_INTEGRATION. Full archive/inventory/receipts/text chunks verified.

T0 00:19:22Z, main01:19:22Z, absolute01:49:22Z; Buildfinished00:48:04Z in originalwindow. Completion resumed08:38:07Z under owner20min allowance; no newproof/Build. Account CLOSED **543/960s;417 retired**, previous1564retired/no carryover. Own active/request/reservation/unresolved none; v3/max3 unchanged. Policy6e1a8e59c56669abe5e6ec2013478e45ed2cc267/ACK1e65f562994220a909ccf97903c36cb054576b76 confirmed.

Next needs a separate owner decision on exact-u64 HRTB and first Continue-unwind recovery; new semantics need separate scope/profile/regression gate. Additional session is not opened. [Checkpoint](cloud-build/origin-layout/FINAL-CHECKPOINT.md) · [Exact result](cloud-build/origin-layout/SHARED-REF-SESSION3-RESULT.json) · [Experiment card](cloud-build/origin-layout/ACTUAL-INSERT-TAIL-B2-CARD.md).
