# Exact Rust source and arithmetic model

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
