# S3-2 capped roots — READY PLANONLY / intake bound / review14 pending

Task `e61fdc2c3f0af10106451f8372f8f9c05e960778`, Fresh13, high/FastOFF,
no subagents. PLANONLY / NOT_APPLIED. This is an independent source/design
preparation with root-supplied verified W11 intake
`d29ab46dbbb45d7106fa30c3ac04bb419a2ac286` incorporated before commit. W11 owns
artifact intake, qualification, cost and cap-cause analysis; W13 consumed only its
four authored summaries, with no artifact acquisition or repeated analysis.
**Independent14/S1 admission and sort4same location-only disposition remain pending.**
There is zero proof credit and no implementation or campaign approval.

The starting contracts remain conditional plan `3e453471291056ed6a52774567703bc57b6aac30`
and S4 matrix `9e013a2683afbf64de762e570a052c11917e52f7`; neither is changed.
Source is frozen `513341f41ce53833a279571401c924bdddddb6c8`, stock tool
`0aac16ef62da9e9d5645782d458593e5d78143ba`. Package008f/controlcb6303/review12c4/GOc59
are exact provenance dependencies in INPUTS.json, not new authorization.
SOURCE-CITATIONS.json binds source ranges and dependency bytes; PLAN.json holds
domains, selectors, obligations and cost scenarios; INTAKE-BINDING.json records
the exact W11 input and its limits. All new selectors are proposed,
NOT_REGISTERED/NOT_RUN, with no substituted callee.

## Exact roots and source-driven hypotheses

`S` denotes frozen smallsort.rs; `H` sorting_s3_leaf.rs; `V` sorting_model.rs;
`P` sorting_s2_span.rs. All intervals below are half-open element offsets.

**Insertion** [S615–702; H103–128]: actual `insert_tail<u8,KeyLess<u8>>`
uses initialized writable V34, begin b=1..16, relative tail p=1..16, span p+1=2..17,
and sorted prefix V[b,b+p). Every byte is arbitrary 0..255, subject only to that
ordering. Tail>=previous returns early; otherwise a ManuallyDrop value and
CopyOnDrop gap guard shift strictly greater predecessors right, then restore the
tail at the gap. Safety requires same-allocation pointers, initialized readable
and writable active span, alignment and nonoverflow. Modifies is precisely that
span. Guarded contract and harness require order plus full-value multiplicities;
H additionally checks every outside V34 byte. The nine covers include both length
and base endpoints, early return, full sift, ties, nonconstant output and return.
No generic comparator, unwind or panic theorem follows.

**Merge** [S837–1017; H153–193]: one raw MU48 allocation, src s=0..40, dst d=0..40,
with disjoint eight-element ranges; source halves4+4 sorted. Exactly dst starts
uninitialized; **all 40 outside-dst bytes are initialized arbitrary full bytes**.
Only src is borrowed as a shared slice, while dst retains disjoint raw provenance.
Four iterations each write a low and a high output via actual merge_up/down;
left/right selection and tie directions differ. Pointer ends must agree after
consumption or the original panic branch remains. The odd-center branch is
inactive at8, and remains an obligation for later lengths. Typed output reads
follow the actual writes. Contract/harness post checks full-byte order/count;
harness checks full outside frame, source frame, arbitrary outside canary and
11 covers, including (32,0) and (40,16).

V's CAP32 is adequate for snapshots of spans<=17 or8, not for whole V34/MU48.
`active_post` checks order and, for each old element, scans old/new values to count
its multiplicity: quadratic nested loops, not a reduced-alphabet oracle. P reads
only initialized active spans and is active only for u8/KeyLess<u8>. KeyLess is
the actual stateless full-byte `<` comparator [V21–60,82–125; P20–41].

The following are complexity hypotheses from source, **not explanations of the
native computational causes**: insertion combines symbolic span length, symbolic base, up to16
shifts, guard effects, old/current capture and quadratic post; same-allocation
merge combines two symbolic offsets, disjointness, conditional MU48 initialization,
symbolic gathers/scatters,48 frame checks,8 source checks and count/post checks.
Contract instrumentation may repeat semantic work. Splitting assertions while
leaving the guarded PFC ensures active may leave that work intact. Verified W11
COST reports insertion stopped by sampled6GiB PGID RSS at112.349s, trigger sample
6326988KiB; it was **not a600s wall timeout**. Compile-to-initial-export observation
upper bound is34.680s. Exact RSS at later kill and precise backend/symex phase
remain UNKNOWN. Merge8same stopped by whole-child timeout at600.205s, including
compile-to-export observation upper bound35.105s; sampled PGID maximum2558128KiB.
Neither capped root has a completed native result. These are source-reported
intake observations, not independent proof of a source-level cost cause. Thus
fixed-p/fixed-base insertion is a memory discriminator; fixed-offset merge is a
time/geometry discriminator. Neither is an unchanged full-root retry.

## Preferred full-domain decomposition and its admission boundary

First retain actual bodies, current predicates and all checks. **I-PART** proposes
16 exact leaves `i_p01_b1_16` through `i_p16_b1_16`: literal p, symbolic b1..16,
V34 all initialized, full-byte sorted prefix, complete original post/frame.
Their union is exactly256 (b,p) pairs. This partitions a quantified length; it
does not prove that any length represents another. Proposed unwind36 retains
V34 frame/capture and stock unwind checks.

**M-PART** proposes `m8_src_before_dst_all48` and `m8_dst_before_src_all48`:
retain MU48, arbitrary bytes, sorted4+4, raw uninitialized dst and full outside
initialization, with respectively s+8<=d or d+8<=s. Each contains561 pairs;
union1122 is the original complete offset domain, including adjacent, distant,
boundary and both sort8 geometry witnesses. Proposed unwind50 retains all loops.
This removes one direction disjunction per leaf; it supplies no fit guarantee.
If still expensive, a fixed-src family s=0..40 retaining every legal symbolic d
is a further exact partition, **41 leaves, not one next-campaign request**.

Separate obligations are explicit in PLAN.json: active semantic post, exact
relational transfer, frame and destination init, actual PFC pre/post, exhaustive
domain union, caller context and checked composition. Separate roots must each
execute the actual body if they claim an actual-body relation. Passing order,
count or frame alone cannot replace any other assertion or qualify a full leaf.
The full PFC post is retained in these partition options; decomposition alone
does not remove its instrumentation cost.

A second, conditional **REL** design can reduce duplicated semantic reasoning:
for insertion define k=#prefix elements<=old tail; check the actual output is
old[0,k), tail, old[k,p), then prove, for every p1..16/full-byte sorted prefix,
that this relation entails the existing order/count predicate. For merge check
an explicit permutation pi of0..7 and actual out[j]=old[pi[j]], plus order and
source/outside frame. Pi must be obtained by checked comparison/consumption steps
or a proved bounded relation, never assumed. Count preservation can use arbitrary
query q:u8 equality of full-span counts; a separately checked equivalence must
recover V's existing per-old-value post. No few-keys theorem is assumed.

REL would require reviewed proof-only relations/lemmas, checked actual-body and
contract bindings, and evidence that stock0aac can express and compose them
without a new trusted model. None exists here. Do not disable an old ensures or
delete count/frame checks to make REL cheap. If it needs unsupported summaries
or an admission waiver, defer REL and use actual-body finite leaves. No provider
edge becomes qualified from registration, a ghost witness, or address equality.

**Provider mismatch:** insert's guarded contract covers spans2..17 without V34/
b1..16 restrictions; merge's covers lengths2..32 without MU48/outside-init/offset
restrictions. A restricted PFC does not prove either universal contract. The
separate-allocation8 root cannot supply same-allocation8, nor can same8 supply
merge32. Any future modular use needs an exact bounded wrapper/guard whose
requires includes the proved domain, actual checked provider at identical source/
tool/cfg/T/F, and independently checked caller entailment. Otherwise inline the
actual body. `sort8_registration_only` remains unqualified.

**Partial-init bridge:** actual sort8 is two actual sort4 calls into temp followed
by same-allocation merge8 [S262–311,815–834]. For n16..32, h=floor(n/2), its34
merge pairs are (n,0) and(n+8,h). At the first call only [n,n+8) in scratch is
initialized; at the second, [0,8) plus[n,n+16) are initialized. These cases do not
entail H's all-outside-dst initialization. A new exact partial-init provider
must preserve initialized values and the MU mask outside dst, initialize dst,
never spec-read MU slots, and prove actual same-allocation separation/provenance.
Numeric disjointness is necessary, not ownership evidence. For n32 the diagnostic
first mask is[32,40); second is[0,8) union[32,48), dst[16,24).

## Smaller-domain options and one conditional campaign

Every option keeps arbitrary full bytes and the actual comparator. None reduces
the alphabet. IDs differ from the capped originals. PLAN.json specifies exact
selectors, premises, oracle, roles/covers and missing coverage.

| Distinct option | Exact smaller domain | Missing extension |
|---|---|---|
|I-D1 / `i_p01_b1_16`|V34, p1, b1..16, spans2|p2..16:240 pairs|
|I-D16 / `i_p16_b1_16`|V34, p16, b1..16, spans17|p1..15:240 pairs|
|I-FIX / `i_p16_b01`|V34, p16, b1, span17|255 other original pairs|
|M-FIX / `m8_s32_d00_allinit`|MU48, s32,d0; all outside dst initialized|1121 other original pairs|
|M-BRIDGE-L / `m8_s32_d00_partial`|MU48, s32,d0; only[32,40) initialized|other33 sort8 contexts and original outside-init domain|
|M-BRIDGE-R / `m8_s40_d16_partial`|MU48, s40,d16; only[0,8),[32,48) initialized|other33 sort8 contexts and original outside-init domain|

The preferred first workflow candidate is an **eight-slot diagnostic/leaf package**,
conditional on independent14/S1 decisions, exact implementation, review and
separate root GO (verified intake has now been supplied):
three original controls (order/count/weak-network), then I-D1, M-FIX, I-D16,
M-BRIDGE-L, M-BRIDGE-R. Every row is a serial fresh singleton with stock tool;
no stubs, root batching, automatic retries or runtime root substitution.
Run literal controls before geometry, small insertion before long insertion,
and fully initialized merge before its partial-init variants. These are cheap
discriminators by structure only; their native cost is UNKNOWN. If support for
mask/frame checking is unavailable, seal a smaller exact request before GO;
do not silently replace the roots at runtime.

All new positives retain the semantic full-count post, precise frame and stock
safety/init/unwind checks. Fixed options have their own feasible length/offset,
tie, early/full-sift or left/right, nonconstant and useful-return covers; impossible
old endpoint covers remain obligations of other full-domain partition leaves.
Require complete same-invocation role/producer-ID binding and SAT covers. At most
this candidate could cover32/256 original insertion pairs and1/1122 original
all-outside-initialized merge pairs, plus two distinct partial-init contexts.
None is currently proved. The union of both partial masks is not a full-mask
theorem. A reduced length/offset subset never grants all-offset/N16/32 credit.

Stop/defer heavy work if controls are not admissible, protected identities drift,
cleanup is unverified, role origins/init masks are unsupported, or a cheaper
discriminator exposes a semantic defect. Local cutoff/error may continue only
under the existing verified-cleanup/protected-post rules; an unqualified result
is not a provider. A failed/capped discriminator warrants a changed, reviewed
candidate or independent remaining work, not unchanged capped-root retries.

## Caps, scenarios and value of the next attempt

| Reference/scenario | Seconds | Meaning and limits |
|---|---:|---|
|merge8 separate|151|Rounded native-verification reference; W11 exact150.963607091s, source-reported provisional S1|
|sort4 same allocation|212|Rounded native-verification reference; W11 exact212.237510446s, location-only decision pending|
|8 hypothetical rows each like151 / each like212|1208 /1696|Arithmetic reference scenarios only; not predictions or phase estimates|
|8 child caps, compilation included|4800|Each600 includes compile subcap180; do not add compile again|
|8 slots + controller180 + cleanup240|6180|8*720+420;720 below6900 campaign ceiling|

The151/212 references are rounded native verification times, not whole-child
wall times: W11 reports completed child elapsed191.767s and254.769s respectively,
with compile-to-export observation upper bounds34.998s and36.942s. Those bounds
are not exclusive compiler CPU/phase measurements. Problems, domains and possibly
effective flags differ. No timing regression, linear extrapolation, speedup,
memory-fit or fit600 conclusion follows. Source loop counts are not solver-time
models; censored roots supply no completed native verification duration.
Retain campaign6900, child600 including compile180, slot720, sampled owned-PGID
RSS6GiB, outer12GiB+2GiB headroom, setup1800 and job180min. RSS is sampled,
not a kernel/whole-tree peak guarantee. Retain canonical paths, fail-closed
before/after protected provenance, precise cleanup, serial fresh singleton
invocations and durable portable prefix. Caps cannot be raised here. Envelope
arithmetic does not prove the complete job or phase will fit.

Budget reference is12/17 with five attempts left: working one S3-2 + two S4 + S5
+ reserve. This is no reservation or accounting mutation. Full I-PART alone
needs16 leaves; it cannot be promised inside this one eight-slot campaign.
Preserve every unrun partition rather than claiming the diagnostics close it.

The two partial-init leaves target the real sort8 blocker more directly than a
blind all-offset retry, but still need all34 contexts, exact sort4 V34->MU48
providers, sort8 init/temp posts and actual caller composition. Positive actual
9/13 remain an independent alternative from the old plan: sort networks need
their own full-byte ordering and prefix/suffix/frame proofs; insertion leaves
then support checked prefix extension (not proof of the networks themselves).
Network17 needs p16; network32's right base17 lies outside original b1..16.
General inserts use MU48 bases0/h with different init masks. Full N16/32 still
needs final merge2..32, odd center, seeding/copy-back/CopyOnDrop, allocation/view
and dispatch matrices, Cell/non-Copy/size>16 types and remaining caller induction.
No promise to solve S3/S4/S5 in four attempts follows from these options.

Current U proposal stays DISABLED and REJECT_ALL; strict expected matches remain
0/9. W11 reports three positive and three negative S1-eligible observations as
**provisional source-reported**, with42 individual U arguments awaiting independent
assessment. No summary is accepted. sort4same has one successful system
`unreachable.1` property with present-null normalized file/line and retained
`library/core/src/lib.rs:0:0` display; its true source origin is UNKNOWN. Its five
assertion roles and seven covers have valid exact sites, but they cannot repair
that other record. No missing-location waiver, producer fix, policy exception or
admission is applied here. Independent14/root owns the S1/U/location decisions.
If qualification prevents new roots being usable, defer the costly root and
spend no attempt until a separately authorized candidate addresses the obstacle.

## Intake and handoff

Root supplied exact verified W11 intake `d29ab46dbbb45d7106fa30c3ac04bb419a2ac286`
for run44416629057/trigger7497ecdb3934585634f5f04e4ff7c6cc42450c0b before W13
commit. INPUTS.json binds only the four consumed authored summaries by commit,
blob and SHA256; INTAKE-BINDING.json records exact cost fields, qualifications,
metadata gap and root's verification claim. Root reports32files/30manifest hashes,
compact digest and5deps/42U source+member hashes MATCH; W13 does not repeat that
artifact investigation or upgrade its assurance to independent proof.

This replaces PENDING_INTAKE with **INTAKE_BOUND_PENDING14**, without changing
caps, full-byte/domain/frame/init/offset goals or budget. Precise backend phase,
source-level cost causality and independent proof remain UNKNOWN/unproved.
Root checks pins/manifest/premises/budget; held14 reviews intake/S3-2 separately.
Any further post-commit evidence update must preserve this package and use one
small immutable sibling. READY/review does not automatically permit implementation,
acceptance, policy edits or a new run. Tool4591 HOLD31/31 remains untouched.
