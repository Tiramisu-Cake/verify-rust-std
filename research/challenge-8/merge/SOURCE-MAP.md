# Exact Rust source and arithmetic model

## Caller audit source ledger — before P1

SmallSort is byte-identical to upstream Rust
`b6f0945e4681bc4d2faa7c22c5f61dc36abf7dd2`; other core/alloc files below
are not vendored in this reduced subtree. Exact reference URL prefix:
`https://raw.githubusercontent.com/rust-lang/rust/b6f0945e4681bc4d2faa7c22c5f61dc36abf7dd2/`.
Read-only downloaded files were hashed, not compiled. Full paths/hash ledger:

| Path under library | SHA256 | Relevant lines |
| --- | --- | --- |
| core/src/slice/sort/stable/mod.rs | 3f2b2d8543a1cb91c9352e041bed49949a31cbd4b1030ec1a82cca1304cb22d3 | 25–29 ZST;63–76 drift;120–124 drift call |
| core/src/slice/sort/stable/drift.rs | 5992b53abed257aa1c2dc2bb811d6a525294471e7a98d434f161d376100bf9c9 | 233–240 create_run/quicksort |
| core/src/slice/sort/stable/quicksort.rs | e7b5df9c7022ade2b932d83c4d0757ba1a211286e03c350695dd383b951e0264 | 26–28 SmallSort dispatch |
| core/src/slice/sort/unstable/mod.rs | 367fc5b0a8dd2ca26643cdcef821ac9ec0fc4c67e7246293b8675609450e2ac7 | 18–22 ZST;40–45 ipnsort |
| core/src/slice/sort/unstable/quicksort.rs | 8fc55e114a3715dafb6b6d336b9450534ce7d45314d71faa9bd79a0c7d3e8a13 | 18–29 SmallSort dispatch |
| alloc/src/slice.rs | dce55c82186526b4c252e99da7a503e6d9765221434fcb3b8495ddfe57113086 | 125–130,185–190,239–245,809–814 stable wrappers;310–354 cached-key |
| core/src/slice/mod.rs | 2180b3b20c402a77394e0378b3bbffcbc74be11560e99c5b5b5f31e80b6dd3d6 | 2988–2992,3042–3046,3093–3098 unstable wrappers |
| core/src/ptr/const_ptr.rs | 6a402581b4b309d53b94cf6ae32aaf15a49a6209399680fddf7fe922eb4de062 | add829,sub935,wrapping docs1000–1024/1080–1103,methods1053/1132 |

Vendored SmallSort: stable specialization49–62; unstable Freeze90–169;
general scratch220–294 (sort8 calls241–249, full merge286); network311–376
(len<18 no_merge, merge367); sort8 663–679. Public sort routes inherit early
ZST returns; direct trait/helper calls do not. Direct ZST network's pointer-equality
loop354–362 prevents its long path reaching merge (short path returns). General
scratch still has direct ZST merge routes. Cached-key sorts a distinct
nonzero `(K,index)` type. Detailed boundary in [POINTER-DESIGN](POINTER-DESIGN.md).

Stock tool source809de4596839b739dd999f9e462242c835e3af46:
vf_mir_translator.ml2395–2439 maps add/sub,2860–2890 maps comparisons;
prelude_core.rsspec105–110 retains provenance in ptr_add;159–164 defines limits;
189–190 scales typed offsets. No pointer wrapping spec/mapping found in audit.
Rust fixture operator projections/refinement are independent of source-text
admission for the full SmallSort body. The original certificate below is retained.

## Accepted Rust projection map

P3 proof1c318453efa4e3a774b2edd791a5298d76132eb0/run37686627140.
Source certificate remainsf2ccc11b235e8f2224131ddef4a12c17409c58863c5712726cb13a02a4960bc7.

| Actual operation | Rust fixture | What is checked / omitted |
| --- | --- | --- |
| src.add(m),src.add(m-1),src.add(n-1),dst.add(n-1) at810–815 | init_const / init_mut | Symbolic in-range add(i), address/provenance/limits; actual initialization linkage OPEN |
| left.add(is_l),right.add(!is_l) at707–708,830–831 | forward_left / forward_right | Exact Boolean casts/operators, no comparator/copy |
| dst.add(1)709 / dst.sub(1)742 | destination_up / destination_down | Exact ordinary steps, reverse i>=1 premise |
| left<left_end827 | pointer_order + stride_order | Exact operator equivalent to index order given source-derived associations |
| left!=left_end OR right!=right_end837 | pointer_guard + stride_equal | Exact Boolean guard expression; panic body/resources omitted |
| Scalar paired/terminal formulas | g2_steps | Both Rust lemma bodies checked; no C import/whole-loop proof |
| wrapping_sub740–741 / wrapping_add822–823 | wrapping_down / wrapping_end | P2 exact method support blockers, projected15:17–54 /14:20–44 |

Every source projection remains separate from actual Rust merge refinement.
The first seven positive P3 sources are byte-identical to P2 projections (seven
raw VF0 cases); order/guard change only research unsafe prototype qualifiers.
Stock compiler emits source MIR independently and refiner compares each isolated
annotated fixture to its ghost-free original. No actual merge source replacement.
wrapping_down/end exact minimal source/log hashes are in the journal. Their
P2source1f2eaaa8 remains the authoritative diagnostic SHA; corrected excluded
reentry/read draft fixtures at1c318453 are NOT RUN.

Pinned base c22f0a30ed457165e07599e226cee289a270b715; full source
library/core/src/slice/sort/shared/smallsort.rs SHA256
32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959.
Admission must check FULL bytes plus the three active function bodies; comments
are not executable calls. Rust runtime/signatures remain unchanged.

merge_up lines683-713: comparator reads right then left in the argument order
is_less(&*right_src,&*left_src); its normal Boolean is negated into is_l.
Select left when is_l, else right; copy selected source to current dst BEFORE
changes; advance right by !is_l, left by is_l, destination by1, in that order.
Both candidate source positions must be readable before comparator selection.

merge_down lines716-746: same comparison/negation; select RIGHT when is_l,
else LEFT. Copy BEFORE changes; right wrapping_sub(is_l), left
wrapping_sub(!is_l), destination sub(1), in that order. A cursor may be -1
only as a wrapping intermediate AFTER its last read, not as a readable position.
Destination sub(1) must remain an ordinary admissible position.

bidirectional_merge lines760-841: n=len, m=n/2, caller n>=2 entails m>=1.
Initialize L=0,R=m,D=0,LR=m-1,RR=n-1,DR=n-1. Repeat exactly m times,
merge_up THEN merge_down. Afterwards left_end=LR.wrapping_add(1),
right_end=RR.wrapping_add(1). If odd, compare left<left_end, select left if
true else right, copy to current D, advance left by that Boolean and right by
its negation. Destination D is NOT advanced by the residual. Final guard tests
left!=left_end OR right!=right_end; on mismatch it panics AFTER the last copy.
The precise line/body certificate will be supplied by hosted admission.

## Invariant with arbitrary comparator results

Write n=2m+e, m>=1, e in{0,1}. After k paired iterations let a count forward
left selections, d count backward RIGHT selections:0<=a,d<=k<=m.
L=a,R=m+k-a,LR=m-1-k+d,RR=n-1-d,D=k,DR=n-1-k.
For k<m BOTH up sources and BOTH down sources are in[0,n), as are D,DR.
The up update cannot affect the down cursors/read validity. D+1<=n,DR-1>=0.
After a down step LR can reach -1 only at the last iteration; RR stays>=0.
Terminal ends are d in[0,m] and n-d in[n-m,n], allowing one-past boundary n.

Paired writes are [0,m) and[n-m,n), disjoint. For e=1, D=m is the sole gap;
BOTH terminal forward sources a<=m and2m-a<=2m=n-1 are readable, regardless
of how the actual pointer comparison chooses the residual source. After that
copy the selected forward cursor may be n; it is not dereferenced again.
All2m+e=n writes are accounted for. Arithmetic scalar final equalities mean
(a==d) when even, (a+h==d) when odd residual Boolean h; if scalar h=(a<d),
the odd pass cases are d=a or d=a+1. No SWO is used for these range claims.

Readability is always strict upper bound n; a terminal position n or wrapping
intermediate -1 is not permission to read. n=2 and n=3 are included universally.
ZST pointer comparisons are NOT assumed to equal logical index comparisons;
range geometry tolerates either residual branch without that assumption.

## Hosted admission certificate

G2 run37672184476/proofSHA b1ed0c22dafec350a64e83675d55350806d77208 admits
all three exact signatures and ALL active statements9/9/30, with operation
linesup704,706–709;down737,739–742;loop817–819;ends822–823;odd826–831;
guard837–838. Sourceadmission JSON SHA256
f2ccc11b235e8f2224131ddef4a12c17409c58863c5712726cb13a02a4960bc7.
Bodyhashes up0ca042e27b297c765dcd972bed404d30535e716600c762d84542371fe74bf7ba,
down0022e177284c62796ea1b944d257a1ebab2573b8c2ee0c6412ae3835e50294c7,
bidir7e312114db3dc90c4e7164d4ff10e1e9df931a6977ae02b89a596aa4f56083d8.
This source-text/order certificate is not a Rust refinement/permission bridge.
Each take_left(up) andtake_right(down) is the negationof its own comparator
answer; the bijection covers arbitrary independent answers. Residualh may be
arbitrary forgeometry, so no ZST pointer-order embedding is assumed.

## Functional occurrence correspondence — accepted A2 / B7

Occurrence IDs are original slice indices0..n-1; keys and pointer addresses are
separate. At pre-pair state(k,a,d), current candidates are exactly:
up(left=a,right=m+k-a), down(left=m-1-k+d,right=n-1-d).
Decision pair fst=take_left(up),snd=take_right(down) each negates its own
rel(rightID,leftID) answer. fa_trace records the selected source BEFORE its
movement at destination k, then selected reverse source BEFORE its movement
at n-1-k, then recursively the next pair. For odd n it appends the last source
h?a:2m-a at destination m. All G2 cursor equations and ordering remain unchanged.

fa_output instead lists increasing destination order: up::(recursive_middle++
[down]), terminal singleton only when odd. Checked fa_trace_output_at and
fa_destinations relate those two representations at arbitrary destination p,
including exact single-write count and out-of-range zero. fa_entry adds arbitrary
source-ID counts under scalar guard alone. This is not a physical pointer/copy
refinement or Rust ownership summary.

Functional ms_faithful uses the same exact two comparator read pairs at every
step, including after previous forward updates (the reverse state is independent).
Finite fixed SWO and original-half sortedness occur only in B. Separate tie
lemmas give forwardleft/backwardright for equivalent keys; odd h=(endA<endD)
models the scalarized line827 only. B7 admits the same fullsource/signatures/
active operation certificate as G2, and rechecks all G2/A/SWO/application bodies.
This three-part evidence remains separate: checked mathematical composition;
exact source-text schedule admission; still OPEN actual Rust pointer/resources/
callback/unwind transfer. ZST comparisons need their own bridge.
