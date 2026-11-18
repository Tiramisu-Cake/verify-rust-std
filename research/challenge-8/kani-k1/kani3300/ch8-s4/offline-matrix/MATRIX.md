# Independent S4 offline coverage matrix — READY

Task `task1964a85b811894bac2f9874aceb7f6857efc2069`. Frozen source
`bd62e54df1b4749154790aa3db3cc7978f547f75`, tree
`dc2e7a7f258719a05c65bbb9b1e2c7f1e8271ac8`; plan
`da89127150a550ccb3861a7bfc5b6205c6409e61`, intake
`ebd77a955b2b8d1b4e8079cfbf569386bcf0b130`, stock tool
`0aac16ef62da9e9d5645782d458593e5d78143ba`.
All source reads used `git show bd62:...`; no current S3 candidate was read.

This is a coverage inventory, with **zero admitted leaves, zero closed proof
obligations and zero independent B1/B2 credit**. Every future selector is proposed,
NOT_REGISTERED/NOT_RUN. Full arbitrary-byte fallback N0..16 and general/network
N0..32 remain the goal. MATRIX.json contains14 actual classes and100 exact
length/size rows (17 fallback,50 general,33 network), leaf DAG, geometry premises,
source citations, S3-1 counterfactual, gaps and proposed finite selectors.

All citations below refer to frozen `library/core/src/slice/sort/shared/smallsort.rs`
at the SHA above. Intervals are element offsets; h=floor(n/2), r=n-h;
p is relative tail offset and insert_tail argument span is p+1.

| Actual class | Seed / leaf calls and exact lengths | Source lines |
|---|---|---|
|F0:0..1|Return, no scratch or leaf|32–51,220–224|
|F1:2..16|shift(offset1), insert p1..n-1, spans2..n (max16)|220–224,704–737|
|G0:0..1|Return before scratch-size check|241–253|
|G1:2..7|copy1 to scratch offsets0,h; each half L=h,r uses insert p1..L-1; merge n|262–311|
|G2:8..15|sort4 at offsets0,h; insert p4..L-1; merge n|273–311|
|G3S:16..32,size<=16|sort8 twice, insert p8..L-1; internal merge8 twice, final merge n|262–311,811–834|
|G3L:16..32,size>16|sort4 twice, insert p4..L-1; final merge n; u8 never takes this path|262–278,286–311|
|N0:0..1|Return before stack allocation|332–348|
|N1:2..8|One region n, shift(offset1), insert p1..n-1|350–373|
|N2:9..12|sort9(prefix9), shift(offset9), insert p9..n-1|359–373|
|N3:13..17|sort13(prefix13), shift(offset13), insert p13..n-1; n17 needs p16/span17|359–373|
|N4:18..24|Two regions h,r in9..12: each sort9 then insert p9..L-1; merge n, copy n back|350–390|
|N5:25|Left12: sort9+p9..11; right13: sort13+empty insert; odd merge25/copy25|350–390|
|N6:26..32|Two regions h,r in13..16: each sort13 then insert p13..L-1; merge n/copy n|350–390|

**Actual T/F and dispatch.** Stable default and unstable default take fallback
(threshold16); Cell<u8>/KeyLess<Cell<u8>> is the finite default-path target.
Stable Freeze takes general with caller scratch (threshold32) regardless of type
size. Unstable Freeze forwards: its default selects general iff size*48<=4096,
else fallback; its Copy specialization selects network iff size<=8 and
size*32<=4096, else general iff size*48<=4096, else fallback (lines32–192,
194–218,1039–1043). The six implementation bodies/forwarding remain distinct.
u8/KeyLess<u8> takes stable general and unstable network; NonCopyByte/its own
KeyLess takes Freeze-default general. S1 only declares N0..3 smoke domains
(verify/sorting_entry_smoke.rs:1–172); no full-threshold result follows here.
The active model recognizes just these three exact pairs; other guarded posts
are inactive, not generic sorting theorems (verify/sorting_model.rs:9–158).
FreezeMarker is backed by Freeze (shared/mod.rs:3–13). Generic callbacks,
large payloads and ZST/all geometries have no admission from these finite pairs.

**Allocation/init/frame/count.** F uses initialized v and restores each insertion
gap, with no scratch use. G uses initialized v and writable MaybeUninit scratch
of length>=n+16 for n>=2; the stack wrapper allocates48. Its seeds and per-element
copies must initialize sorted halves before merge scratch[0,n)->v[0,n).
CopyOnDrop/mem::forget and the distinct failure paths remain obligations
(lines226–330). For G3S the two sort8 triples (src,dst,temp) are
(v+0,S+0,S+n) and (v+h,S+h,S+n+8), each length8. sort4 fills temp halves;
merge8 consumes S[n,n+8)->S[0,8) or S[n+8,n+16)->S[h,h+8).
These are **34 distinct n/src/dst contexts** over n16..32, with destinations and
temporaries disjoint inside one scratch allocation. General final merge reverses
the source/destination allocation roles. Stable external scratch can require
additional disjoint same-allocation v/scratch reasoning; a separate stack fixture
does not establish it.

N modifies regions in v, then for n>=18 merges sorted v halves to separate
private MaybeUninit stack32 and copies n initialized elements back. Its sort9
receives slices9..12, sort13 slices13..17: only the first9/13 are sorted by those
networks, so the suffix and exterior frame must survive until insertion. The
second region begins at h, which changes backing/base context. Literal source
extraction finds25/45 swap sites, stored in JSON; extraction proves no sorting.

Every leaf needs exact source/tool/cfg/T/F/provider binding, valid provenance,
alignment/nonwrap, initialized spec reads, destination initialization, precise
outside/source frame, full-value counts and a lawful comparator with the admitted
callback footprint. Final merge additionally needs all n2..32 and odd-center
coverage (lines902–1017). Integer interval checks and canaries establish no
pointer or general locality theorem. Fixed48, a short view into48, an exact
n+16 allocation and arbitrarily larger scratch are separate scopes. Normal
partial correctness supplies no generic ownership, stability, unwind or
termination theorem; verify.rs:36–60 records additional check/domain limits.

**Even if all proposed S3-1 roots pass.** The committed implementation TASK at
entry1964 proposes two checker negatives, fresh swap PFC, separate/same-allocation
sort4, insert p1..16, separate/same-allocation merge8, and sort13_weak. Exact
READY13 candidate pins are not supplied; geometry constants/results are UNKNOWN.
The conditional residuals remain:

1. Actual sort8 semantic composition and its34 internal merge8 contexts.
2. Positive actual sort9/sort13 ordering, prefix/suffix/frame and base contexts.
3. Final merge n2..32 beyond n8 (30 other lengths), including odd center, then
   consumer copy-back/seeding/guards and insertion-loop/caller induction.
4. Cell fallback through16, typed NonCopyByte general through32, the size>16
   general branch, six dispatch bodies, and all unproved backing/locality domains.

No u8 length match grants another T/F or allocation context. A weak-network
negative, safety-only contract, registration or assumed consumer is not the
missing positive proof. No S3 source, runner or contract was designed/modified.

**Prioritized future selectors.** JSON specifies exact proposed finite domains:
sort8 geometry bridge; actual network prefixes; all-length final merges; Cell
fallback0..16; u8 general0..32; u8 network0..32; NonCopyByte general0..32. All use
full logical bytes. Candidate source/control/contracts/unwinds and independent
review/GO are future work; there is no dispatch or attempt reservation here.
The short implementation-question list is in JSON and leaves all obligations
open rather than choosing new trusted premises.

**Historical S2 unchanged.** ebd77 intake reports swap native SUCCESS but strict
NOT_GRANTED: four unreachable checks plus three absent named success roles.
Three generic negative FAILUREs are unadmitted; checker_count has assertion.2
versus expected.1. Heavy roots UNKNOWN, later NOT_RUN and deferred general32
remain distinct. No retrospective label/policy waiver, artifact intake,
compiler-instance origin claim or independent proof credit is made.

Static document consistency checks passed: cited frozen tree and report digests,
complete classes/exact lengths, insert bounds,34 interval pairs, mixed25,
network17/tail16, large-type32/sort4, literal25/45 sites and provider/citation
references. These checks prove no leaf semantics, pointer/init safety or native
fit. No compiler/rustfmt/solver/CI/push/PR/issue/ledger/subagent/model action.
