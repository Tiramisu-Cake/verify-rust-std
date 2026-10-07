# Independent networks results and integration boundary

Branch `challenge-8/networks`; separate worktree `/root/verify-rust-std-networks`.
Frozen research entry `bea62488b44f8c557e45e04cb4eb259b0173422f`.
Actual SmallSort full-file SHA256
`32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`.
No runtime Rust, generic signatures or common STATUS/PLAN changed; no merge.

## Claims and evidence

| Claim | Evidence and precise boundary |
| --- | --- |
| N9 binary/rank sorting and occurrence permutation | Stock VeriFast26.09, [N9e run37641057339](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37641057339), proof SHA `58f1680ec7951a265535f0462701511478f6efa3`: all5 cases accepted, full general-rank sorted-output post and all8 universal projections, both exact negatives and14 rejection controls |
| N13 binary/rank sorting and occurrence permutation | Same unchanged stock profile, [N13b run37642585521](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37642585521), proof SHA `6851001f78b02144e25037c55d55644fa34b30de`: Boolean263 statements/7633 return-leak paths; full rank1126 statements/7638 paths; identity380 statements/3 paths; both negatives and14 rejection controls accepted |
| N13 general-order transfer | Full N13b machine-checked threshold/rank composition accepted, including all12 universal threshold posts and full sorted-output rank post. General-key finite-class transfer in [INTEGRATION](INTEGRATION.md) |
| Exact source sequence | Hosted fail-closed admission of the whole pinned file and literal function bodies:25/45 calls, source lines, index bounds, argument order; [SOURCE-MAP](SOURCE-MAP.md). This is sequence correspondence, not Rust refinement |
| Actual swap_if_less contract | [SWAP-CONTRACT](SWAP-CONTRACT.md): effect-aware normal/unwind safety specification separate from fixed-order functionality. Rust implementation proof OPEN |

Abstract CE on occurrences `(A,B)` produces `(c?B:A,c?A:B)`. Identity permutation
holds for arbitrary decisions. Sorting additionally requires a fixed total
preorder (or strict weak order on equivalence classes), c exactly when
key(B)<key(A), preservation of every occurrence's key throughout all callbacks,
and normal callback returns. Each finite ordered key-class input has integer
ranks; threshold projection commutes with min/max at each CE. An inverted final
pair would project to1,0 at the right rank, contradicting accepted Boolean order.
This proves conditional general key order without limiting physical T to integer
or Copy/Freeze types. The handwritten transfer argument and machine verification
of the complete rank application are identified separately above.

Networks sort only the first9/13 elements, assuming len>=9/13; suffix effects
are framed relative to callback effects. Complete entry-value snapshot
permutation needs snapshot preservation, stronger than preserved keys. No
stability promise. Neither abstract proof establishes physical ownership, UB
coverage, comparator-panic safety, tool soundness, or a public Challenge8 goal.

Rust integration dependencies: exact `select_unpredictable<*mut Element>`
chosen-pointer/no-unwind summary at this source/profile (a *const specialization
is insufficient); ManuallyDrop/read/two-copy ownership and padding validity;
FnMut effects and normal/unwind borrow recovery; provenance, alignment, bounds,
equal-index and ZST logical ownership. Actual callees must be verified before
using their summaries. No parallel VeriFast patch, RAPx or historical tool profile.

## Hosted budget and preserved failures

| Run | Source SHA prefix | Summed job seconds | Result |
| --- | --- | ---: | --- |
| [37636248489](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37636248489) | d433216 | 381 | N9 initial rank/identity timeout; classifier inconclusive preserved |
| [37637872959](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37637872959) | 70eaa2d | 193 | N9 binary/identity/controls accepted; rank timeout |
| [37638843477](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37638843477) | 910c183 | 195 | N9 first projection timeout |
| [37640086725](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37640086725) | 240d2ef | 194 | N9 all8 projections accepted; final rank application timeout |
| [37641057339](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37641057339) | 58f1680 | 41 | N9 complete abstract proof acceptance |
| [37641704629](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37641704629) | fccae97 | 241 | N13 binary/identity/controls accepted; full rank timeout |
| [37642585521](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37642585521) | 6851001 | 254 | N13 complete abstract proof acceptance |

Total **1499/1800 job seconds**, including cold preparation/evidence; **301 unused**.
Only this branch's executed job durations counted; skipped jobs have zero cost.
The other direction's budget is untouched. Generated proofs/full logs/results
and exact std/tool certificates remain in Actions artifacts; no logs/build output
committed. Failed runs are evidence, not intended negative controls.

## Completed phase checkpoint

N13b source `6851001f78b02144e25037c55d55644fa34b30de` shares the45-step
projection computation in one universal lemma exporting all12 threshold posts,
then applies it at each right output. It retains all per-step correspondence,
all final assertions/posts, binary/identity/negative/classifier gates. N9 output
generation is unchanged. All full logs read and hashes matched; no active run.
The transient GitHub push/dispatch failure and API fast-forward publication are
preserved in EXPERIMENT-LOG; final checkpoint uses ordinary commit/push.

This completes the separately authorized specification/mathematical-network
work, with actual Rust helper verification still OPEN. Integration proposals
are in [INTEGRATION](INTEGRATION.md); do not import a conditional abstract result
as an assumed verified Rust helper summary or claim a public Challenge8 target.
