# Accepted merge index geometry, actual Rust transfer open

2026-10-07: stock unchanged VeriFast26.09 accepted the complete pure arithmetic
model of the pinned merge_up/merge_down/bidirectional_merge schedule. This proves
index-access and cursor-advancement geometry for arbitrary n>=2. No full Rust
memory safety, ownership, unwind or sorting functionality is established.

Accepted [G2 run37672184476](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37672184476),
checked/published proof commit `b1ed0c22dafec350a64e83675d55350806d77208`.
All8 named own ghost lemma bodies match expected/visited; VF0,88statements,
17return/17leak checks, full normal posts and source integrity. Final entry
return/leak completes0.652030s. Generated proof-source SHA256
`4594f159400bcfeeea87e3086e5765472d121dced7385bd2ef216a83bf24dea8`, log
`f5a2cb78108d732959574541c487ec292673ef15ca726f76d8498d1467d93c9f`.
No own assumed or bodyless correspondence lemma, no finite length bound.

## Universal domain and proof

`mg_entry(n,decisions,residual_left)` requires ONLY n>=2 and an arbitrary
list<pair<bool,bool>> of length n/2. A pair describes forward-left and
backward-RIGHT selection; each is the negation of that call's comparator answer.
All independent Boolean sequences are included. Residual choice is arbitrary,
which also covers ZST pointer-order uncertainty without mapping it to an index.

Its reusable post exports full `mg_trace_safe(n/2,n%2,0,0,0,decisions,h)`,
terminal geometry at recursively computed final counts, n=2*(n/2)+n%2,
n/2>=1 and write_count(decisions,n%2)=n. Full trace recursively fixes each
current read/copy/write and each next-state relation, not just terminal bounds.
Own recursive proof is structural induction on the entire arbitrary decision
list. Stock integer div_rem_nonneg plus explicit remainder case split gives
m=n/2>=1 and e=n%2 in{0,1}; no decomposition/ordering axiom is added.

Let a count forward-left selections and d count backward-RIGHT selections.
After k paired iterations,0<=a,d<=k<=m,n=2m+e:

| Cursor | Initial position | Position after k |
| --- | ---: | --- |
| Forward left | 0 | a |
| Forward right | m | m+k-a |
| Reverse left | m-1 | m-1-k+d |
| Reverse right | n-1 | n-1-d |
| Forward destination | 0 | k |
| Reverse destination | n-1 | n-1-k |

For k<m, BOTH comparator source positions, selected copy source and current
destination are strictly in[0,n). Separate checked helpers establish up and
down accesses BEFORE their cursor changes. Up advances right by !choice,
left by choice, dst by1; down decrements right by choice, left by !choice,
dst by1, matching the actual active operations. Up/down use independent cursors;
up's progress therefore does not invalidate reverse reads in that iteration.

Forward post-cursors may reach boundary n after their last access. Reverse
left may reach -1 only after the final read; the next operation is endpoint
wrapping_add(1), not another dereference. Reverse right stays nonnegative.
For down destination, the proof supplies dst>=1 before ordinary sub(1), and
its result>=0. Mere validity of the current destination write would not supply
that ordinary-decrement premise to a standalone helper; the caller discharges it.

At the end, endpoints are d and n-d, both in[0,n], possibly one-past n.
For even n all paired accesses/updates are checked and no residual read occurs.
For odd n both remaining candidates a and2m-a are strictly below n, residual
dst=m is valid, and BOTH possible choices/advances stay within[0,n]. Residual
destination is not advanced. n=2 and n=3 are included by the same theorem.

The trace fixes writes k and n-1-k for exactly m iterations. The separately
checked mg_destination_regions lemma proves separation of[0,m) and[n-m,n).
These equations yield their full coverage and the odd sole gap m as mathematical
corollaries; write_count=n alone is not used as a uniqueness proof.

Supplemental scalar-guard lemma: even final equalities hold iff a=d; odd iff
a+bit(h)=d. If h equals scalar a<d, the odd pass cases are d=a or d=a+1.
This algebra does NOT assert the actual pointer guard implements those equalities
for ZST. Bounds are independent of both the guard outcome and sorting laws;
inconsistent comparator decisions can still cause the source's final panic.

## Exact pinned source correspondence

Full SmallSort SHA256
`32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`.
Hosted admission checks all3 exact generic signatures, ALL active statements
(9/9/30), operation order and critical source lines, with no extra active call.
Comparison arguments are right then left; copies precede right/left/dst changes;
loop executes up then down exactly n/2 times; endpoint/odd/guard order matches.
The original intrinsics::assume(m!=0) is covered arithmetically by n>=2.
Actual runtime bytes and generic signatures are unchanged.

Source-admission JSON SHA256
`f2ccc11b235e8f2224131ddef4a12c17409c58863c5712726cb13a02a4960bc7`.
[Source map](SOURCE-MAP.md) records signatures/body hashes and exact lines.
This text/order certificate and the pure model do not replace Rust refinement,
provenance, pointer permissions or callback execution semantics.

## Intended negative controls

All3 negatives use definitions only plus one isolated body. All reach their
single intended proof-stage false assertion at136 after witness antecedents:

| Error | Witness / false obligation | Exact location |
| --- | --- | --- |
| Off-by-one loop read at n | n=2,m=1,k=1,a=0 yields right=2; right<n fails | 136,18-19 |
| Both forward sources advance | Initial left0,right1 both increment; sum3 differs from required sum2 | 136,37-39 |
| Wrapped intermediate treated readable | Last down step chooses left0, post left=-1; 0<=left fails | 136,14-16 |

Exact predicates match recorded logs; no failed helper precondition/setup/parser/
timeout is counted. For EACH case all7 wrong-line/predicate/body/target/column/
timeout/source classifier controls PASS (21total). Negative source files are
byte-identical to G1; only expected diagnostic metadata was calibrated in G2.
Concrete witnesses test detectors; the positive theorem remains unbounded.

## Frozen trust profile and open transfer obligations

Official stock VF26.09 source809de4596839b739dd999f9e462242c835e3af46,
archive SHA256da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa,
console SHA256dc672335da76fe1bb06cf7ebca916185c34edb65466df0a937645a437c7f0ecc.
Frozen accepted networks classifier/prove.py remains byte-identical SHA256
994afa65a24c1deb73fd120ac88c96fa5d86eb971f58adba678c850a1153d0c4.
No verifier/parser/kernel/prelude/refiner/memory-model patch or historical profile.

Geometric comparator domain uses no sortedness/SWO/purity/key-preservation
premise. Normally returning answers may be arbitrary; a comparator panic stops
future events and supplies no unwind/ownership theorem. Sorting would separately
require sorted halves, fixed/preserved key order and faithful normal answers.

[Transfer obligations](INTEGRATION.md): actual usize/layout/isize byte limits;
same allocation/provenance/alignment and ordinary add/sub range; wrapping
provenance/re-entry; separate ZST pointer order/equality; source initialized
readable T and destination writable/disjoint copy permissions; FnMut effects/
borrow recovery, stale or duplicate temporary ownership and panic/unwind.
The pinned actual FreezeMarker bound remains, with no new Copy/Freeze constraint.
None of those actual Rust resources follows from mathematical positions.

## Evidence, budgets and publication

| Experiment | Checked commit | Run | Hosted job seconds | Result |
| --- | --- | --- | ---: | --- |
| G1 | 90872439be953a960aacbb12c79886d6a87e73db | [37671730724](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37671730724) | 11 | Inconclusive entry remainder / negative metadata |
| G2 | b1ed0c22dafec350a64e83675d55350806d77208 | [37672184476](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37672184476) | 14 | Full geometry/negatives accepted |

**25/1800 summed hosted job seconds**,1775unspent; preparation/evidence included,
skipped jobs0. G2 proof-process wall0.88s,peakRSS66220KiB. No active run.
[Artifact11505083335](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37672184476/artifacts/11505083335),
17681bytes, ZIP SHA2560844784ce64fb385aaf365ebbb6020d11442f2e1423a3b360e408b1722a1d35a
matches upload; full source/log/result/environment/resource evidence inspected.
All failure/source/log hashes preserved in [journal](EXPERIMENT-LOG.md).

Branch created from exactc22f0a30ed457165e07599e226cee289a270b715 in an isolated
worktree. Each proof SHA pushed/remote-verified before its single new dispatch.
Final local/published HEAD adds documentation only after checked b1ed0c2; no
proof result assigned to that documentation commit. All executable checks hosted.
No downloaded logs/generated artifacts committed, no branch merge or first-agent
worktree/branch/common document changes. Networks iteration closed separately:
SWO/N9/symbolicN13accepted, exactN13adapterOPEN, old budgets1499/1800 and1649/1800
and proofSHAs04ea220.../7dfc3ed...unchanged; no adapter run/unused-time transfer.
