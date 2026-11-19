# S3-3 insertion alternatives — READY PLANONLY / review bound

Task1f8c6fb3153527fe887af40fe024371268377ee7, CURRENT13 high/FastOFF, no
subagents/model changes. Source1b4a904/tool0aac/control775574e frozen. Root supplied
verified intake5d9439a and exact independent review
028531727fc48ef9f26f16dfb95c2b2666c96dd7: APPROVE_INTAKE_WITH_PRESERVED_LIMITS,
zero blockers. The recommendation remains conditional on separate root selection/
implementation/review/GO. Exact admissionff193cc35690a5daabaa849d412c58d9f286d893
is also bound, for prior exact metadata/one allinit case only, not future roots.
Only committed authored reports and source were read;
no artifact acquisition, native-property reanalysis or location review was repeated.

INPUTS/DEPENDENCIES and SOURCE-CITATIONS bind full hashes and exact source ranges.
ALTERNATIVES, RESOURCE and DAG JSON contain the bounded comparisons. No source,
control, cap, flag, policy, runtime, CI or accounting change is applied.

## Recommendation and what the observations establish

Prefer **fixed-base p1 on the same initialized V34 at the unchanged6GiB cap** as
the next insertion discriminator. Use a distinct proposed selector
`sorting_s3_3_future::i_p01_b01_fullu8`, not the old capped root. Keep both active
bytes and all32 outside bytes arbitrary fullu8, current sorted/full-count post,
full outside frame, arbitrary outside canary, actual insert_tail/PFC and unwind36.
Only begin changes from1..16 to literal1; p1/span2 remains. This retains1/16 of
I-D1 geometry and1/256 of the original begin/tail grid, not a full insertion leaf.
Original rel16 means p1..16/spans2..17. Full active-length16 (p15) and maximal
relative-tail16/prefix16/active17 (p16) remain OPEN for all original bases; neither
is discharged or removed by choosing p1.

For at most one next workflow, pair it with **actual positive sort9**, Original
mode, initialized V34/active[1,10), concrete KeyLess<u8>, 25 actual swaps and
current full-value post/frame; no verified/ordinary summary substitution. This
buys an independent positive-network obligation rather than repeating p16 before
learning whether fixed-base p1 helps. Three existing fixed negative controls
precede these two roots. Proposed five-slot order and exact scopes are below.
All new selectors are NOT_REGISTERED/NOT_RUN; no runnable request exists here.

Intake COST distinguishes the two censored observations:

| Root | Compile-to-first-export upper bound | Whole child / sampled PGID trigger | Result |
|---|---:|---:|---|
|i_p01_b1_16, p1/span2|33.306s|131.465s /6361996KiB|local RSS stop, no completed inventory|
|i_p16_b1_16, p16/span17|31.836s|126.130s /6330308KiB|local RSS stop, no completed inventory|

Cap6291456KiB; exit-15/signal15, timed_out=false, cleanup verified, later roots
continued. Neither hit600child,180compile,720slot or global wall. Compile markers
precede stops, but exact symex/backend subphase, uncensored verification duration,
RSS needed to finish and RSS at later kill remain UNKNOWN. These are root-verified
intake/source-reported observations, not independent proof or a cost-cause audit.
Do not divide runtime/memory by16, extrapolate a growth curve, or predict fit600.

Even the shortest legal nontrivial insertion, p1, reached RSS. There is no useful
shorter insertion length under its len>=2/begin<tail contract. Fixed base fixes
one source-level symbolic geometry dimension while preserving backing, full-byte
data and oracles; actual transformed binding remains a separate check. Symbolic pointer/contract-length expressions, frame/canary selection,
CAP32 snapshot representation and PFC instrumentation are source-driven cost
hypotheses, not established causes. p1 has only one possible shift; p16 has up to16.
Post's per-input-value count loops are quadratic in active span, yet this alone
cannot explain the p1 observation. A fixed-base success suggests domain/encoding
sensitivity; it does not identify which compiler/backend phase caused the cap.

## Higher local RSS: a conditional alternative, not the default

Frozen runner562–585 computes available A from host MemAvailable, reduced by
memory.max-memory.current when finite, then group cap min(12GiB,A-2GiB).
Isolated runner1111 additionally clamps to local L=6GiB. Thus:

`effective_local = min(L, 12GiB, A-2GiB)`, with failure when the available budget
is nonpositive. Current code does not require enough A to reach configured L;
it may silently run with a lower effective cap, which must not be labelled a
higher-memory experiment. No current VPS reading establishes future CI A.

Outer Owned supervision samples worker/descendant VmRSS and cuts off above12GiB
(s3_runtime149–186). **The2GiB reserve is subtracted from available memory; it is
not an extra allowance making the outer kill limit14GiB.** The supervisor itself
is not an owned descendant. Local PGID samples and outer owned-PID census have
different timing/scope; sum/difference of their maxima is not a memory model.
Both are non-atomic, with50ms local/20ms outer nominal polling and possible
overshoot. Reading cgroup headroom creates no cgroup/kernel/whole-tree guarantee.

| Proposed local L | KiB | Minimum A for full L plus existing reserve | Outer12 minus L | Above larger prior trigger |
|---|---:|---:|---:|---:|
|6.25GiB|6553600|8.25GiB|5.75GiB|191604KiB|
|**6.5GiB**|6815744|**8.5GiB**|5.5GiB|453748KiB|
|7GiB|7340032|9GiB|5GiB|978036KiB|
|8GiB|8388608|10GiB|4GiB|2026612KiB|

If root selects a memory experiment instead of the preferred domain workflow,
propose **6.5GiB**, a0.5GiB/8.33% local increase, for one unchanged I-D1 domain
and existing native selector.6.25GiB is a possible fine threshold probe, but
adds only about187MiB above the larger observed trigger; with four scarce
attempts its incremental information is weaker.6.5GiB adds about443MiB. These
are design margins, not inferred solver requirements or an optimum.7/8GiB are
larger alternatives, not automatic escalation steps; do not spend a cap ladder.

A prospective implementation must require A>=8.5GiB and effective cap exactly
6.5GiB for that named experiment, otherwise defer/refuse rather than bypass the
available-memory reserve. Leave outer12/headroom2 and every time/output cap
unchanged. Keep substantial arithmetic outer room for other owned processes;
the5.5GiB difference is not a proven overhead bound or guaranteed availability.
Available memory may change after the snapshot. A setup/resource refusal can
still consume an authorized workflow attempt; no automatic refund is assumed.

Changing only request/CAPS would be ineffective or rejected: runner41 and125–133
bind6GiB,1111 clamps it, r5_profile holds shared caps, and portable replay checks
effective RSS against the profile at s32_campaign399–405. Any future higher-RSS
profile must consistently bind admission, actual worker cap, source/compile
receipts and local/upload readers without relaxing legacy6GiB profiles. This
plan changes none of them. Keep singleton/canonical paths, protected epochs,
exact inventory/start selection, cleanup, durable prefix and strict errors.

One same-domain RSS-only run asks whether this exact root completes or crosses a
new observed resource boundary. Completion may expose missing U/location/guard
qualifications; it is not automatic admission. A further RSS stop supplies a
censored observation for that invocation, not a universal minimum memory needed
to solve insertion. It may instead hit600wall. It supplies no p16/full-domain
fit or timing prediction. No time/compile increase is justified by these stops.

## Distinct smaller domains and exact missing extensions

All symbolic bytes stay0..255 subject only to declared order/branch premises.
Every option retains actual body, current semantic post, frame, canary, safety,
normal-return and unwind checks. No few-keys theorem or hidden checker reduction.

| Proposed option | Exact retained domain | What remains |
|---|---|---|
|F1 recommended: i_p01_b01_fullu8|V34,b1,p1,span2|15 other I-D1 bases;255 other original grid pairs|
|F16: i_p16_b01_fullu8|V34,b1,p16,span17,sorted prefix16|15 other I-D16 bases;255 original pairs; not selected next|
|P8: i_p08_b1_16_fullu8|V34,b1..16,p8,span9,sorted prefix8|240 other original pairs; this is not a subset theorem for fixed p16|
|E1: i_p01_b1_16_early_fullu8|I-D1 plus x>=A[0]|Only early-return data subset; strict-sift subset still open|
|S1: i_p01_b1_16_sift_fullu8|I-D1 plus x<A[0]|Only strict-sift data subset; ties/early return still open|
|Tiny: i_p01_b00_v02_fullu8|V2,b0,p1,span2|Different allocation/backing: zero automatic V34 geometry credit|

E1/S1 are disjoint exhaustive **value partitions** for each of the same16
geometries, not32 geometries. For p>=2, generalize to x>=last, x<first, and
first<=x<last under sorted-prefix first<=last. Interior is impossible for p1;
do not register it or demand impossible covers. No subdomain alone has the
original all-value theorem. ALTERNATIVES records feasible roles/covers, and
validation checks partition arithmetic only, not algorithm semantics.

F1 covers early return, full sift, duplicates, nonconstant output and useful
return. Literal base1 needs no impossible base16 cover. E1 needs ties/early and
nonconstant witnesses, not a full-sift cover; S1 needs strict sift/nonconstant,
not duplicates. Existing checker order/count negatives plus the fixed weak13
negative retain exact named failures, full statuses and source binding. Nothing
grants a full generic insert contract or a new caller from PFC registration.

## Source-specific full-obligation decomposition

DAG.json separates pointer/region premises, early path, checked logical gap
transfer, CopyOnDrop restoration, order/full-count equivalence, exhaustive domain
union and caller applicability. Preserve the actual algorithm/CFG/contracts.

Let A be the old prefix, x the old tail, p its relative index. On the shift path
after k copies, g=p-k: prefix[0,g) is unchanged, positions[g+1,p] equal old A[g,p),
tmp holds x, guard.dst=begin+g, and moved values are>x. The logical gap plus held
tmp is value/ownership accounting, **not a claim that a physical byte's init bit
became false**. Never spec-read a hypothetical hole or use manual ShadowMem.
The actual copy at688 establishes the next relation and exact footprint; pointer
decrement and stop at691/697 preserve bounds. At stop g=0 or A[g-1]<=x.

Actual CopyOnDrop::drop at316–329 copies held tmp back with len1 on normal exit.
The completed sequence must be A[0,g),x,A[g,p), with outside values preserved.
Checked lemmas then establish order and exact full-value counts, including ties,
and recover the unchanged current post. These are required proofs, not facts
assumed to discharge the body. Keep full PFC ensures/instrumentation; splitting
assertions does not necessarily remove its cost. Pure u8/KeyLess normal return
does not prove arbitrary callback/panic/unwind/NonCopy ownership behavior.

Missing substantive design step: how stock0aac binds these checked loop/state/
drop relations to the actual transformed body and unchanged contract, without
an unchecked summary or assume-invariant. This needs a bounded root design/review
decision before implementation. Source equality, scalar arithmetic or a ghost
witness is not that binding. No flagON method or trusted model is introduced.

Previously admitted b487 swap/sort4/separate-merge cases are bounded
SOURCE_REPORTED at their own fixtures. Exact ff193cc now admits one bounded
allinit functional/known-value-frame PFC case at MU48/src32,dst0, plus three exact
metadata packets. This supplies no independent init theorem or provider summary.
Partials remain DIAG_INIT_OPEN/nonproviders. None supplies an
insert/Drop summary, a universal swap contract, a masked sort8 provider or caller
induction. Methodplan d8f4's enabled-init storage/layout/mask prerequisites stay
OPEN and separate, with no implementation here.

## At-most-one conditional next workflow and defer rule

Preferred fixed list: checker_order_corrupt → checker_count_corrupt → sort13_weak
→ proposed F1 → proposed sort9_v34_b01_len09_real. Five serial fresh singleton
slots;5*720+180+240=4020s,2880 below existing6900 ceiling. Each600child includes
compile180: do not add5*180 to5*600. Setup/tool build once, fresh compilation per
root. Historical controls' whole children34.224/33.017/32.899s, setup721.402300596s
(tool-build subprocess267.439s) are references only; next compile/setup/backend
times are UNKNOWN within caps. Worst cap arithmetic is not actual job-fit proof.

sort9 uses actual source500–541, independent full-byte active9, snapshot length9
(not whole V34 beyond CAP32), all25 exterior values framed and arbitrary canary.
Its fixed len9/base1 case advances positive9 semantics useful for N2/N4/N5; it
does not qualify slices10..12, other bases, a universal network summary or the
whole caller. Positive13 and insertion-prefix extension still need exact proofs.
Actual sort8 remains behind all34 init/caller contexts; repeating already observed
fixed merge diagnostics adds less value. A long p16 repeat is deferred for now.

Memory-only alternative, mutually exclusive with that list: three controls then
existing I-D1 at proposed6.5GiB, four slots/3300s envelope. No automatic switch,
extra p16 root or escalation after a cap. No per-row mixed cap mechanism is
assumed. Root must pick and review an exact future profile/selection first.

Review14 reporting approval is now bound. Defer dispatch while any further
report binding discrepancy or prospective source/gate/resource admission is unresolved, or if root judges likely metadata rejection makes the information
unusable without a separate prospective diagnostic decision. Local cap can
continue only after verified cleanup/protected post; independent sort9 may still
run under the fixed list. Global identity/readability/cleanup failure stops with
later NOT_RUN. After another fixed-base RSS cap, prefer the decomposition design
decision; do not spend remaining attempts on unchanged p16/automatic cap ladders.

Source/tool/provider/T/F/geometry/init/frame entailment and independently checked
full-value composition remain. Network17 needs p16; general half growth needs
p8..15 in different MU48/base0/h contexts; network32 right base17 is outside the
old insertion base range. Full N16/32 additionally needs positive9/13 contexts,
sort8 init/temp, all-length/odd-center merge, copy/guard/drop, typed Cell/NonCopy/
size>16, dispatch and allocation/locality rows. No reduced case grants that goal.

Item2 reference13/17 leaves FOUR: hypothetical S3-3+S4+S5+failure reserve is only
arithmetic, not a promise, grant or reservation. Item1 31/31/HOLD4591 unchanged.
Strict0/8/producerUNKNOWN history,41U arguments,12SUCCESS guards and exact location
proposals stay as intake reports; oldf740 is original-run only. No admission,
policy, flags, caps, source/control/runtime/CI/accounting change is made here.

## Review handoff

Independent review028531727fc48ef9f26f16dfb95c2b2666c96dd7 was supplied before
sealing and is bound by exact report hashes. It confirms the RSS/censoring facts,
recommends three exact metadata cases, and preserves all scope limits. It applies
no admission; shared emitter/source-MIR origin stays UNKNOWN, general rule PENDING.
Root subsequently supplied exact admission
ff193cc35690a5daabaa849d412c58d9f286d893 before sealing. It admits only the three
exact metadata packets and ONE QUALIFIED_BOUNDED_SOURCE_REPORTED allinit
functional/known-value-frame case. The current three negative labels remain
reviewed observations, without extra control qualification in that note. Strict
0/8/producer history stays unchanged. Partials stay DIAG_INIT_OPEN/nonproviders;
actual init/provider and all34 sort8 contexts remain OPEN. General rule PENDING,
shared emitter/source-MIR origin UNKNOWN; no future-run/ID wildcard or f740 transfer.

Seal READY_PLANONLY_INPUTS_BOUND. Preserve this packet for any later bounded
immutable update. Neither this plan, reporting review nor prior exact admission
changes future caps/policy, qualifies new roots or launches CI. Root chooses
implementation/review/GO separately. No duplicate artifact/location review.
