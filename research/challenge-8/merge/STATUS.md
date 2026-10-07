# Merge checkpoint — supported stock Rust components accepted; wrapping STOP

Updated 2026-10-08 (Moscow; runs dated 2026-10-07 UTC).
Branch challenge-8/merge, isolated worktree /root/verify-rust-std-merge.
Owner entry documentation HEAD: 7d27ce106d27208bcd1156fe5675f70f8f9bf1aa.
No active run. No uncommitted proof/tool draft. Two excluded wrapping-fixture
annotation/prototype corrections are committed but NOT RUN / NOT ACCEPTED.
Supported stage closed at this documentation checkpoint; no wrapping rerun
or semantic tool change permitted by this stage.

**Budget 512/1800 hosted job seconds used, 1288 remain**, same merge budget:
entry330 + P1 111 + P2 36 + P3 35. Includes setup/evidence; no reset, retirement
or transfer to/from networks or the first agent. One own hosted run at a time.

Caller audit COMPLETE: stable/unstable public entry ZST guards cover their
routes to general scratch, sort8 and (nonzero) network merge. Cached-key sorts
nonzero (K,index) tuples. Direct general SmallSort ZST remains outside those
returns. Direct network ZST returns below18; at18..32 its same-address region
loop does not reach merge on normal paths. Standalone Challenge ZST remains
OPEN; no size>0 premise was added to its general contracts. [Audit](POINTER-DESIGN.md).

Rust component proof SHA **1c318453efa4e3a774b2edd791a5298d76132eb0**,
[run37686627140](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37686627140):
9 isolated positives,12 own bodies,102 execution records,25 return/leak paths;
full verifier/export/decode/refinement/integrity pass. Checked local Rust G2
step/terminal lemmas; exact const/mut add, Boolean advances and destination sub;
positive-stride order/guard equivalence conditional on pointer/index associations.
Two intended negatives accepted at exact TARGET assertions,128 classifier
rejection controls pass. No whole-merge refinement or Rust resource summary.

First blocker to further pointer/index composition: stock26.09 has no function
for exact const-pointer wrapping_sub/add. [P2/run37686101335](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37686101335),
source1f2eaaa832a7183180675389979ec15c62a78b5d, establishes both missing methods
with export/decode/refinement0. Wrapping -1/provenance/re-entry-to-end associations
remain OPEN. The read-from--1 negative is INCONCLUSIVE at an earlier setup
obligation; its corrected draft is NOT RUN. No ordinary-sub replacement or axiom.

G2/A/B proofs and premises unchanged and accepted:

- G2 b1ed0c22dafec350a64e83675d55350806d77208 / run37672184476:
  arbitrary-length scalar cursor geometry with arbitrary normal choices.
- A fc4d03d31f92c6d3f3566b0baa506d0a6dec6805 / run37677079473:
  final scalar guard alone gives exact occurrence permutation/write trace.
- B 4e546ec150cf655681516be727aa1a79f525fc56 / run37681190236:
  fixed finite SWO on immutable keys, sorted halves, faithful normal answers
  and scalar odd choice imply stable sorted occurrence permutation/guard pass.

Full Rust G2 loop/composition, actual pointer-to-ID/copy realization, caller
premise proofs, memory permissions/initialization/ownership, legal FnMut effects
and unwind remain OPEN. Nonzero geometry is not general provenance/permission
soundness. ZST address noninjectivity is semantic audit evidence, not a stock
ZST layout proof. Full merge safety and Challenge completion NOT CLAIMED.
Stock unchanged26.09 only; std/runtime/signatures/A/B/comparator model unchanged.
No network/exactN13 resumption, branch merge or first-agent-tree/common-doc edits.

[Results](RESULTS.md), [plan](PLAN.md), [journal](EXPERIMENT-LOG.md),
[source map](SOURCE-MAP.md), [coverage](coverage.md), [integration](INTEGRATION.md).
Proof SHA is executable evidence; later documentation HEAD is reported separately.
