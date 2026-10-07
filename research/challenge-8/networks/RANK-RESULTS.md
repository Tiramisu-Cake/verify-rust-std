# Finite SWO rank phase: accepted claims and exact open obligation

2026-10-07: generic finite SWO -> integer ranks and full exact N9 composition
ACCEPTED. Full universal symbolic-domain N13 component R13f ACCEPTED;
exact-domain N13 adapter remains OPEN after R13e. This is the same phase/budget, not a new authorization.
No actual Rust safety or public Challenge completion is established.

## Constructed ranks and general immutable keys

For arbitrary fixed pure rel on a finite list d, assume finite irreflexivity,
strict transitivity and transitive incomparability. Each occurrence has its own
ID; equal keys remain allowed. Define rank(x) as the count of ORIGINAL
occurrences z satisfying rel(z,x). Checked induction proves, for x,y in d:

- rel(x,y) iff rank(x)<rank(y), in both directions.
- Incomparability in both directions iff rank(x)==rank(y).
- 0<=rank(x),rank(y)<length(d).
- CE decision rel(right,left) selects the exact pair of IDs, realizes min/max
  ranks, preserves domain membership and arbitrary-q occurrence count.
- swo_ordered_pair projects rank(left)<=rank(right) to !rel(right,left).

The bridge derives correspondence rather than assuming an embedding. Weighted
class sizes may leave rank gaps; ranks do not identify distinct occurrences.
All16 generic bodies accepted in R9f, VF0,83statements/40return and leak checks.
Generated-source SHA256
`acc2d0bd1d43eba573c57c206438398ab1dc7a887945ea1bdf96a1885312f2ca`.
Stock VeriFast26.09 and list/count/forall semantics are unchanged. No own
bodyless axiom, imported solution, Copy/Freeze or stability assumption is used.

For immutable keys pull back their chosen fixed strict weak order to occurrence
IDs. Applying these pure results requires that every key and this order stay
fixed, every comparator call return normally and answer exactly
rel(current_right,current_left), and actual swap_if_less realize that ID CE.
Non-key effects need not vanish. This is a functional applicability premise,
not a restriction introduced into unrestricted Rust safety.

## Accepted N9 and N13 boundary

[Full N9 R9f](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37661652169)
checked `04ea22075f87634221cc43ccba59486fb10ad817`: all25 source CEs,
ID/rank wire equality at every step, all8 adjacent key-order posts, every output
ID in original d and complete arbitrary-q multiplicity. Both the universal
composition and its exact0..8 specialization have full accepted posts, VF0,
4214statements/546return and leak checks. Generated-source SHA256
`984b6479c71dd2788583319df7d21b248778e99c53888920f6f1bc484079afa9`.

N13 R13f checks the full universal `network13_finite_swo_composition(rel,d,q)`
component with finite_swo(rel,d) and mem(0,d),...,mem(12,d), all45 exact source
CEs, all12 adjacent order posts, all13 output memberships and full arbitrary-q
multiplicity,19named bodies/2143statements/7675return and leak checks,VF0. This unit isolates the extra
exact-domain helper/wrapper as OPEN, retaining the component's entire contract.
[Component run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37668142119),
published/checked source `7dfc3edae6b8cb5cbba1a98d3a53495a5b53bc2c`.
Generated-source SHA256 `f65fe3366282ce905cc895c2a5326a13cb8e6a0b78fddb7ef46c988e1a1454bf`;
byte-identical to R13e through the entire universal component, then closing the
ghost block. All19bodies match expected/visited,full normal/return/leak/source
gates accepted. Exact adapter excluded only from this explicit component unit.

The last complete EXACT N13 unit [R13e](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37666145711)
checked `46f50efabb44b6790efd446cc612b4ea4d95af0a` and timed out300s.
Generated-source SHA256
`0ccb713de8487e439901fba98d4001c8358d6e51bbbc44f09e871d1cca498598`
identical to R13d. The full symbolic body completed203.928s, checked equality
of finite-domain laws208.170s, but exact wrapper call3464 started218.656s and
never finished by300s. No false assertion was reported; this is inconclusive.

Precise remaining machine obligation: under d==literal(0..12) and
finite_swo(rel,d), instantiate the checked universal composition, discharge
initial memberships, and export ALL literal-domain memberships, all12 literal
adjacent !rel(next,prev) posts and complete arbitrary-q original multiplicity.
The original concrete wrapper R13/R13c has the same intended specialization;
its failed artifacts are retained. Equal-domain premises are mathematically
substitutable and their finite-law equality body was reached, but the entire
exact adapter has no accepted certificate. No axiom substitutes for that gate.

Both sizes include/recheck the previously accepted integer-rank theorem bodies
in the same unit before summary use. The frozen prove.py remains SHA256
`994afa65a24c1deb73fd120ac88c96fa5d86eb971f58adba678c850a1153d0c4`.
The full SmallSort source stays SHA256
`32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`.
Source admission certifies exact25/45 ordered calls, indices0..8/0..12 and
required len>=9/len>=13 prefixes. All-pairs order is the mathematical corollary
of exported adjacent order, rank correspondence and integer transitivity;
it is not separately enumerated as a machine post. Universal q and distinct
initial IDs establish occurrence permutation even for tied keys. Stability
and entry-value snapshot preservation are separate and unclaimed.

## Meaningful negative and trust boundary

The negative relation has only0<2: irreflexivity and strict transitivity hold,
but0~1 and1~2 while0 !~2 violate transitive incomparability. Concrete ranks
rank(1)=0,rank(2)=1 contradict less(1,2) iff rank(1)<rank(2). The classifier
requires the intended false assertion at65,26-28, after rank evaluations.
All7 wrong-line/predicate/body/target/column/timeout/source controls reject.
Negative-source SHA256
`7c9cf87ce96c670b6bb5bc60e52921b62840b4ffafd5b255ff449a7c453d57be`.
Preparation, unsupported-operation or a failed callee precondition never count.

Frozen official VeriFast26.09 source809de4596839b739dd999f9e462242c835e3af46,
archive SHA256da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa,
console SHA256dc672335da76fe1bb06cf7ebca916185c34edb65466df0a937645a437c7f0ecc.
Strict full-body/return/leak/source-integrity/zero-error gates remain unchanged.
No verifier/parser/kernel/prelude patch, Rust integration or branch merge.
Actual Rust FnMut effects/borrow recovery, select_unpredictable at *mut T,
ManuallyDrop/read/copy permissions, ownership/provenance/memory and normal/unwind
safety remain OPEN. Mathematical ID/rank proofs supply none of these resources.

## Hosted evidence and budget

| Experiment | Run | Checked source SHA | Job seconds | Outcome |
| --- | --- | --- | ---: | --- |
| R9 | [37653028959](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37653028959) | ccf813e797a1cea88c9629aaf33d501a57db0e15 | 14 | Include preparation failure |
| R9b | [37653292102](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37653292102) | b8359b838e96312693f0340cc6daf5db7c78fd1d | 12 | Boolean-post elaboration; negative accepted |
| R9c | [37653560718](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37653560718) | 09d41dd233d4b15366a38532b6b2cc5e5820b701 | 37 | Bare relation assertion elaboration |
| R9d | [37653851684](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37653851684) | 955fd2a3334e8fe14c55bdb00f98c4f9813da775 | 192 | Generic accepted; N9 timeout after6CEs |
| R9e | [37654875244](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37654875244) | a38cc109329613645de8d995a5faba2feed7627f | 192 | All25CEs/first7 final pairs; last bridge timeout |
| R9f | [37661652169](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37661652169) | 04ea22075f87634221cc43ccba59486fb10ad817 | 72 | Full N9 and exact wrapper accepted |
| R13 | [37662026439](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37662026439) | f00f446e72758ec8c6da1f34d74c7c92719aecf2 | 193 | Exact concrete wrapper timeout180s |
| R13b | [37663270558](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37663270558) | 5783475c864ab3d4416c027b9ab75c671ea5f9e7 | 12 | Nested generic closing-token parse failure |
| R13c | [37663550717](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37663550717) | b70ac9a25a2894ab12564c9ac24b8866aca63db8 | 193 | Exact concrete wrapper timeout180s |
| R13d | [37665036667](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37665036667) | e5bc807534b155cd0cb63bbc7d89a48497bbfecd | 192 | Equivalent formal-domain adapter timeout180s |
| R13e | [37666145711](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37666145711) | 46f50efabb44b6790efd446cc612b4ea4d95af0a | 314 | Same exact adapter timeout300s after analysis |
| R13f | [37668142119](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37668142119) | 7dfc3edae6b8cb5cbba1a98d3a53495a5b53bc2c | 226 | Full universal component accepted; exact adapter OPEN |

**1649/1800 summed hosted job seconds spent,151remaining.** R13f actual job
18:36:41Z-18:40:27Z cost226s, including preparation/evidence. Owner last
continuation spent1202 of1353; no new budget. No active run. Further full-unit
retry would not fit151remaining at measured226s; exact obligation saved.
Actual job start/end includes cold preparation and evidence; skipped jobs cost0.
Previous phase stays1499/1800spent,301unused not transferred. Other direction's
budget untouched. Every executable check was GitHub-hosted; no local generator,
verifier, compilation or test. All historical sources/logs/hashes/failures are in
RANK-EXPERIMENT-LOG.md and Actions artifacts; none of the generated files/logs
are committed. Independent review corrected R9e's earlier second-pair reading:
all25CEs and first7 final pairs were reached; bridge5059 on the last pair stalled.

## Publication

Saved65f2ddb06a8de05b718209f8df746fe1fb03163e and
04ea22075f87634221cc43ccba59486fb10ad817 were published first, unchanged,
and remote04ea220... verified. HTTP500 history remains preserved; resumed
ordinary fast-forward push worked, no permission bypass or Git Data fallback.
Each subsequent proof SHA was pushed/remote-verified before its single dispatch.
A final documentation-only checkpoint follows the last proof SHA; it is not a
new verification run. See STATUS and final report for local/published/checked
SHA distinction. No automatic merge.
