# S3-2 r1 — bounded conditional next-leaf plan

PLANONLY / NOT_APPLIED. Preserve checkpoint56edd and all S3-1 packages. Frozen
source513341f41ce53833a279571401c924bdddddb6c8, stock0aac16ef62da9e9d5645782d458593e5d78143ba;
reviewed controlfc29b93b1e333b73e55e2872701c80d9927f3b02 is read from the Kani
repository. Review27040 approves that control delta; GO99291133 concerns a
separate coordinator campaign. **S3 native results/cost/fit are UNKNOWN** here.
No job/status/native evidence was queried. Review approval is not leaf proof.

Citations: S = source513341, `library/core/src/slice/sort/shared/smallsort.rs`;
M = S4matrix9e013a, `ch8-s4/offline-matrix/MATRIX.json`. INPUTS.json binds full
commits/blobs/SHA256; SELECTORS.json contains actual signatures, source lines,
all100 exact M row pointers,14 classes, six dispatch bodies,34 merge contexts,
and39 network caller rows. S differs from M's bd62 source only by guarded sort4
semantic ensures; runtime routing/signatures/bodies match. No source is edited.

## Concrete reuse boundary

Even IF S3-1 leaves pass, backing48 merge8 numerically contains all34 pairs:
for n16..32, h=floor(n/2), source/dst=(n,0) or(n+8,h). But S3-1 initializes all
outside-dst bytes. In actual stack sort8, first merge knows only[n,n+8)
initialized, leaving32 other outside-dst slotsMU. Second knows[0,8) plus
[n,n+16), leaving16 outside-dst slotsMU. Thus **zero complete sort8 caller
contexts are automatically discharged**. The exact init masks are recorded for
each of34 rows. Sort4 arrays6/6 also do not qualify V34→S48, and same-allocation
sort4 does not replace that separate-allocation call. [S:262–311,764–835]

Network fixtures use fully initialized V34, active base1. All actual swap bases
1..17 and indices<13 fit S3-1's numeric V34/base0..20/a,b0..12 domain. This is
potential concrete fit, not proof of network ordering or source/cfg lifting.
The19 sort9 caller rows deduplicate to11 callee(base,L) tuples;20 sort13 rows to13.
Equal tuples can reuse an admitted exact provider only after proving current
source/tool/effective-cfg/T/F/provenance/init/preconditions. The parent caller's
sorting/induction/ownership proof remains necessary. [S:332–392,460–610; M:N2–N6]

S3-1 insertion p1..16 covers numerical lengths but not every context. General
inserts operate in mostlyMU S48 at bases0/h, not initialized backing34. Network32
right insertion begins at absolute17, beyond S3-1 begin1..16. Network17 still
needs p16/span17. Even final merge n8 has different actual allocations than the
S3-1 separate arrays10/10; the other30 lengths need fresh proof. [S:286–311,667–737,937–1017]

## One possible NEXT campaign, conditional on actual results

| Order / proposed selector suffix | Actual domain / encoding | Source-loop unwind proposal |
|---|---|---:|
|next_sort8_u8_n32_left_real_pfc|V34 src1; whollyMU S48 dst0/temp32; real two sort4+merge|50|
|next_sort9_u8_v34_base1_len9_real|Original positive9,25 real swaps; full V34 outside frame|36|
|next_sort8_u8_v34_s48_context34_real_pfc|all34 triples; side0 whollyMU, side1 only prior[0,8),[n,n+8) initialized|50|
|next_sort9_u8_v34_context11_real|all19 caller rows /11 exact callee tuples; prefix9, suffix/exterior frame|36|
|next_sort13_u8_v34_base1_len13_real|Original positive13,45 real swaps; changed inline encoding, no swap summary|36|
|next_sort13_u8_v34_context13_real|all20 caller rows /13 tuples, including mixed25; prefix13 and full frame|36|

Names are NOT_REGISTERED/NOT_RUN. The proposed module does not exist. Each row's
signature/cfg, requires, precise modifies, full-value sortedness/count, init/frame,
loops, registration status, roles/covers and prerequisites are in SELECTORS.json.
All inputs are independent full bytes0..255 with actual pure KeyLess<u8>.
Snapshots cover active8/9/13 spans only: the current model CAP32 does not permit
silently snapshotting the entire V34/S48 backing. Useful return, unsorted/tie/
duplicate/nonconstant witnesses and complete dynamic producer-ID binding remain
mandatory. Prefix/suffix state cannot be discarded. [model:active_snapshot/post]

The PFC sort8 body runs actual helpers. Scratch output/temp initialization and
unread-MU footprint must be checked before typed/spec reads; do not initialize
extra scratch simply to fit an older provider. Side1's arbitrary initialized
prior values overapprox caller correlations without assuming sortedness or a
summary. Actual sort8 contract has dst order/count plus dst/temp modifies; a
modular consumer still needs an explicit checked init/temp guarantee.

Positive9/13 Original roots prove finite actual-call semantics only. Neither
helper currently has a semantic contract/PFC registration. Before stub_verified
reuse, require a separately reviewed guarded prefix contract, precise prefix
write set, init/frame post and actual checked PFC in every claimed context.
Current sort8_registration_only and any unproved summary remain unqualified /
DIAGNOSTIC_ASSUMED. NEXT itself uses **no verified or ordinary substitutions**.
This makes actual13 different from the old timed-out sort13_assumed encoding;
it is not an unchanged600s retry. [S:500–610,815–835; frozen batch registration]

Bounds are source proposals, not sealed runtime settings or fit predictions:
max48 fixture/frame loop→50; max34 network fixture/frame→36; model loops8/9/13,
merge4, and25/45 straight-line swap sites. Nested multiplicity uses per-loop
bounds, not products. Preserve unwind/default checks; any extra generated loop
requires review/upward adjustment. Never lower bounds/domain/alphabet to fit.

Root/coordinator must first inspect actual S3-1 evidence, then separately authorize
new implementation, exact source/control/request/workflow/cfg, static gates,
review and GO. Stop broad roots if fixed discriminators or stock compiler/MIR,
init/frame, identity/snapshot/containment/role/U checks fail. Later roots become
NOT_RUN; no automatic retry or dynamically substituted root list. Do not run
unchanged merge32_real/sort13_assumed/general32, reduced alphabets, experimental
ordinary-stub fixes or new-main969f. Keep stock0aac and reject-ALL-U; the disabled
U proposal is not an admission rule. fc29 metadata still reports compiler-instance,
contract-resolution/property-origin edges UNKNOWN; names/hashes do not fill them.

One job/shared stock setup, at most six serial fresh singleton slots is an
**envelope estimate**, not authorization:6×720+180+240=4740 under reference6900;
child600 includes compile180, RSS6GiB. Retain fresh-prefix controls and reviewed
fc29 fail-closed snapshot/protected-error/precise-ESRCH/lifecycle checks in the
future exact request. Native costs and fit are UNKNOWN. No native duration
is inferred from Python validation or historical solver/external cutoffs.

## Remaining DAG through full16/32

sort4 + exact partial-init merge8 → actual sort8 → general half initialization;
actual swap → actual positive9/13 → checked shift/insert prefix induction;
changed final merge invariant K0–K8 + odd center + allocation direction → final
consumers; copy seeds/extensions/back-copy and CopyOnDrop/forget remain actual
caller obligations. SELECTORS.json has eight later families, **not extra NEXT
slots**, with signatures/contracts/init/frame/loops/prerequisites and source refs.

General16(size<=16): two sort8, no insertion, final merge16. General32: two sort8
plus p8..15 per half and merge32; size>16 instead uses sort4+p4..15. Network16:
13-prefix plus p13..15, no merge. Network32: two13-prefixes plus p13..15, private
MU32 merge32 and copy-back. Mixed25 is left9/right13 plus odd merge25; empty
insertion boundaries9/13/18/26 are retained. All F0/F1,G0/G1/G2/G3S/G3L,N0..N6
and all100 exact rows remain explicit, not just these endpoints.

Physical exactC=n+16, physical48/view(n+16), physical48/view48, larger/interior
allocations and same-parent disjoint v/scratch are separate scopes. Identical
raw callee tuples within physical48 may reuse a qualified exact leaf after
provenance/init proof; that does not prove the parent's different slice metadata,
length guard or frame. Arbitrary capacity needs a checked locality theorem.

Preserve size0/ZST,1..8,9..16,17..85,>=86 under the original nonoverflowing guards.
Stable Freeze always uses general; size>16 still takes sort4 at32. Unstable Copy
uses network<=8, then general iff size*48<=4096, otherwise fallback16; Freeze
non-Copy uses the general gate. Six entry/forwarding bodies stay distinct.
Global model supports only u8/Cell<u8>/NonCopyByte exact KeyLess pairs; helper
span/pair semantics are u8-only. Typed Cell fallback16 and NonCopy general32
need fresh typed providers or actual inline proofs; large payloads need a real
full-value model/checked representation result. Inactive guarded posts, Copy/
Freeze assumptions, equal sizes or first-byte projections cannot close them.
No generic T/F, arbitrary callback, stability, termination or unwind credit.

Current reference31/31+11/17=42/48 leaves six item2 attempts before any unknown
coordinator accounting. Working2S3(includingS3-1+NEXT)+2S4+S5+reserve is only an
estimate, not a reservation/grant/guarantee. No run/slot/ledger/publication action.
Root+coordinator decide subsequent work; publications remain owner-only.
