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
| N13 Boolean sorting and occurrence permutation | Same unchanged stock profile, [N13 run37641704629](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37641704629), proof SHA `fccae976b8979105a19910f8e2181809d5d39103`: Boolean263 statements/7633 return-leak paths; identity380 statements/3 paths; both negatives and14 rejection controls accepted |
| N13 general-order transfer | Mathematical finite-class/threshold induction in [INTEGRATION](INTEGRATION.md), using accepted Boolean theorem and checked local min/max threshold lemma. Full machine-checked N13 rank composition NOT accepted: timeout180s after3/12 universal projection bodies |
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

Total **1245/1800 job seconds**, including cold preparation/evidence; **555 remain**.
Only this branch's executed job durations counted; skipped jobs have zero cost.
The other direction's budget is untouched. Generated proofs/full logs/results
and exact std/tool certificates remain in Actions artifacts; no logs/build output
committed. Failed runs are evidence, not intended negative controls.

## Ready continuation

N13b proof source `a2be90886dc1e61c43b29d7ddc1cb95e028bd569` combines the identical
projection computation into one universal lemma exporting all12 threshold posts,
then applies it at each right output. It keeps all45 CE correspondence checks,
all final assertions/posts, binary/identity/negative/classifier gates. N9 output
generation is unchanged. Jobcap8min/inner420s/per-file180s fits remaining555s.
Acceptance still requires a NEW exact-SHA hosted run and full artifact inspection;
this prepared proof is not accepted evidence. Current dispatch state is in STATUS.

Integration proposals are in [INTEGRATION](INTEGRATION.md); do not import a
conditional abstract result as an assumed verified Rust helper summary.
