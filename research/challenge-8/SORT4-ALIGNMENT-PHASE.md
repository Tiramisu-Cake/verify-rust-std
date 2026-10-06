# Independent sort4 alignment geometry gate

## Stock generic and fieldless layout prototype — 2026-10-07

**AUTHORIZED / IN PROGRESS** from e170656b7ff00e8de8ac9d5ebc949d2dbf3cfd75.
Entry clean, local/remote exact match, correct fork/branch, no active experiment.
Previous phase and two runs37537448952/37537868053 remain historical INCONCLUSIVE.

Stock gate result: run37540829027/source968c073, both generic VF0 with integrity/
refinement PASS. One NEW run,43seconds; concrete stock ZST failures kept separate.
Transition to Step2 permitted; prior full evidence in results/journal.
Prototype runs2/3 stop at console build; matrix NOT RUN. Budget3/6,235/10800s.
Run4 candidate only qualifies Ast.RustLayout after measured compiler diagnostic;
same domain, acceptance matrix and profile semantics.

### Step 1: stock gate, before any layout patch implementation

Hypothesis: reachable ordered ghost cases i<1, then i<2, then i<3, otherwise,
expose integer bounds and derive respectively i==0/1/2/3 without unreachable
proof statements. Last run discharged posts but dead-code gate rejected assertions
in impossible branches. This directly addresses that measured failure.

Keep original six cases, source Rust after ghost removal, .add, outer req/resources,
all target assertions and normal/unwind posts. Generic domain is arbitrary valid
Sized T, array_<u8>(base,4*sizeofT,bytes), nonnull aligned/live base and usize i<=3.
Normal post: same byte array, result==base+i, pointer_within_limits(result),
result-address%alignT==0; on_unwind_ens false. No i equality assumed.
Official unchanged VF26.09/source809de4596839b739dd999f9e462242c835e3af46,
nightly-2026-02-05, old flags/specs/classifier. Both generic bodies must exit0,
with export/decode/refinement, source integrity, dead-code/leak/unwind checks intact.
Stock original ZST layout/add may stay INCONCLUSIVE independently. Source/destination
negatives still must fail only at intended alignment assertion after add/cast.
On generic failure fix only checked proof steps within budget; no profile transition
until BOTH pass. Original std sort4 blob e555fce440872898e47fd5114f32eb15401d07df
and adopted normal/five-unwind contract unchanged; this remains partial geometry.

### Step 2: separately identified experimental fieldless layout profile

Only after stock gate PASS, implement a reproducible patch over the same 26.09 pin,
store patch/provenance under research/challenge-8; apply/build on hosted runner only.
Stock archive/runner/profile stays separate. No historical patch-chain reuse.

Allowed semantic changes: original-source fieldless, nongeneric-definition Sized
Rust struct (repr Rust/C, optional align) gets pinned compiler layout size/ABIalign
through exporter/schema/AST/translator/engine. Explicit absent/present wire variant,
original field/generic/support checks and same type/source/target binding required.
Exclude packed/transparent/fielded/generic-ADT/enum/union/DST exact facts; never use
PhantomData-filtered field list to select support. Rust struct size lower bound
may become >=0, while C/C++ retain >0. Generic T remains symbolic; no sampled
layout constant for generic ADTs. No field-offset, ownership, alias or copy rules change.
Trust premises: pinned rustc query describes SAME source Ty/target as MIR and .add;
wire decoding preserves values/absence and identity; exact facts attach to same
engine typeid; existing layout/offset constraints remain consistent. Review is
experimental, not a model-soundness theorem or accepted upstream tool profile.
If any further semantic change is required, STOP and document boundary.

### Pre-recorded regression/acceptance matrix

| Obligation | Required outcome / intended stage |
| --- | --- |
| Original Z | Original #[repr(align(8))] struct Z; size0/ABIalign8 assertions and full posts, VF0 |
| Z const/mut add | For arbitrary admitted i0..3 with original zero-byte resources/aligned/live base, unchanged .add preserves pointer and limits/alignment; VF0 |
| Generic baseline / application | Both exact stock-proved generic bodies remain VF0 under experimental profile; checked calls instantiated at original Z and nonzero u64 preserve original resources/posts |
| Unsupported layouts | Original-field PhantomData example, fielded nongeneric, generic ADT and excluded representations emit absence, no fabricated sampled facts; relevant abstract Rust proofs retained |
| Rust/C/C++ compatibility | Selected pinned existing regression bodies finish with unchanged checks; C/C++ positive-size behavior and empty C++ complete-object nonzero control retained |
| False Z size/alignment/stride | Each VF failure at its NAMED target assertion, after setup/layout/add as applicable; setup/other failure INCONCLUSIVE |
| Contradiction control | assert false under ordinary satisfiable req true with original Z layout context must fail exactly there; never count unreachable body or inconsistent premise success |
| Absent metadata | Exact Z size/align assertion stays unproved when exact metadata intentionally absent; no fallback zero. Independent generic baseline may still pass |
| Corrupt metadata | Malformed size/align/support identity rejected at explicit translator validation; export/decode artifacts preserved, no model proof accepted |
| Wrong binding | Wrong ADT/source/target metadata rejected at named identity validation before engine facts; never silently attached to a different type |

Metadata variants operate only on disposable exported artifacts on hosted runner,
with original immutable artifact and transformation/source/profile digests retained.
Their explicit translator rejection gate is distinct from intended VF assertion
controls; parse/setup failure does not count. Negative classification remains strict,
old six-case classifier untouched; new controls get named explicit gates, no weakened
exit/status checks. Positive whole-unit VF0 and all integrity/refinement checks required.
Patch regressions include source type/target/wire/AST/profile identities, operation
reachability and full logs/artifacts. Success is limited to this struct subset and
geometry, not whole-model soundness, automatic copy UB or sort4 ownership safety.

Budget max6 NEW manual hosted runs, SUM jobs <=10800s including build/preparation.
Reserve 30min allocation per run (smaller actual time counted), never duplicate,
one active experiment, exact pushed/head_sha match, inspect full logs/artifacts.
Every next run must test a concrete change grounded in preceding data; no unchanged
Re-run. At criteria met, budget exhausted or out-of-scope semantics needed, STOP.
Only static text/edit/diff/shell syntax inspection locally. No local executable
checks/builds/compiler/verifier/extractor/runner. Update compact STATUS, historical
results/journal/plan/coverage and commit/push after meaningful evidence.
RAPx CLOSED / NO-GO; B/C NOT RUN. No full sort4, historical FnMut/Drop, external
issues/PR/messages. Prior phases below remain historical.


## Current generic completion and layout review — 2026-10-07

**CLOSED at2-run limit;2/2 NEW runs,85/3600 summed job-seconds.**
[Run1/37537448952 and run2/37537868053 closeout](SORT4-ALIGNMENT-RESULTS.md#generic-completion-and-layout-review--two-new-runs):
direct i==0 assertion initially unproved; checked ordering then derives0 and
finishes original alignment/resource/return/leak checks. Three unreachable
assertions trigger the unchanged dead-code gate, so whole generic const/mut remain
INCONCLUSIVE, no VF0. Concrete ZST still blocked; negatives/replay pass. Layout
review/regression design complete. No active run; STOP at2/2, no further proof
edit/dispatch/check weakening. Card below is historical authorization of this
completed scope; no tool patch or patch-regression check implemented.

Owner explicitly resumes from b523959d2032b28086aa8b11dd35a50a2eb7c7e0. Entry clean,
local/remote match, correct fork/research branch, no active/queued experiment.
Previous three runs and phases are preserved below and in the results; unused
slots from the preceding closed phase are not reused.

Two independent authorized tasks: (1) complete generic const/mut H_align on
unchanged official VeriFast26.09/nightly2026-02-05, (2) documentation-only review
of minimal Rust layout correction versus a concrete independent component, with
live upstream/release source pins and a future regression plan. No layout patch
or executable patch-regression test is implemented in this phase. The known
concrete ZST model boundary does not stop this separately authorized generic task.

Historical run1 hypothesis: the residual ghost branch i!=1,2,3 can explicitly prove
i==0 from the original usize bounds and discharge the old alignment post via
result==base. Add only checked ghost assertions; no assumed i==0, new axiom or
outer req. Prior run37535499783 passed helper/local bounds and i=1,2,3 full checks,
so this is a specific remaining-path correction, not an unchanged rerun.

Exact generic domain: arbitrary valid Sized T (symbolic size0 retained), original
array_<u8>(base,4*sizeofT,bytes), nonnull aligned base/provenance, usize i<=3.
Original normal post: same byte array, result==base+i, pointer_within_limits(result),
result-address%alignT==0. Original on_unwind_ens false. All six runtime texts and
.add operations, case order, external contracts/final posts, tool pins/flags/specs
and classifier are frozen at b523959. Concrete original Z cases stay size0/align8
and zero-offset-add controls, honestly INCONCLUSIVE if model blocks them. Both
negative byte-offset cases must fail at exact intended line25 modulus8 assertions
following line22 .add and line23 cast. No overall green-workflow requirement.
The actual std sort4 blob e555fce440872898e47fd5114f32eb15401d07df and adopted
full normal/five-unwind resource target remain unchanged; fixtures are only geometry.

Budget maximum2 NEW GitHub-hosted manual runs, summed jobs INCLUDING setup/replay/
upload<=3600s; cap30min per dispatch, one active experiment. Every follow-up must
correct a failure measured in the preceding run. Exact source/head_sha and full
logs/artifacts audited, commit/push before dispatch. No Re-run old source or local
compiler/verifier/runner/extractor/test execution. Only static edits/text/syntax
checks locally. At generic success, budget exhaustion or a new generic-only
model/contract requirement, stop proof iterations; finish review/documentation.

Review must distinguish Rust and C/C++, closed and generic types, exact size/align
facts versus weakened bounds, shared typeid consistency, existing proofs/trust
requirements, concrete independent component/source/domain bridge and avoiding
contradictory concrete Z facts. Recommend one route with minimum implementation
scope and acceptance criteria; regression checks are DESIGN ONLY / NOT RUN.
No tool semantic changes/new axioms, ZST exclusion, weakened contract/checks,
historical insertion/FnMut/Drop expansion, B/C or external issues/PR/messages.
RAPx CLOSED / NO-GO and Kani prior evidence unchanged. Update results/STATUS/log /
plan/coverage/composition/layout audit, commit/push; no further phase auto-authorized.

<a id="current-bounded-no-patch-proofreclassification-phase--2026-10-07"></a>

## Historical bounded no-patch proof/reclassification phase — 2026-10-07

**CLOSED at a concrete ZST model boundary;1/3 NEW runs,38/5400 job-seconds used.**
[Run37535499783/sourceea635ea closeout](SORT4-ALIGNMENT-RESULTS.md#bounded-proofreclassification-continuation--closed-at-model-boundary):
classifier replay and intended negative controls pass; checked generic helpers /
local bounds and i=1,2,3 branches pass, residual alignment post remains INCONCLUSIVE.
Concrete original Z layout/add cannot close faithfully under the positive struct
size model and missing repr-alignment metadata. No model extension implemented;
no active run. STOP: remaining two slots are retired, no further proof fix/dispatch.
The authorization/card below records this completed scope, not standing permission.

 Owner explicitly
resumes from checkpoint f1c0774b3a8662ca4e9d838a4a1ad06f7f625e55. Entry clean,
local/remote heads match, correct fork/research branch, no active/queued experiment.
Two previous runs37529855468 and37532204465 remain historical INCONCLUSIVE with
unaltered logs/JSONs and separate historical budgets.

Scope: fix actual source-prefixed VF header recognition with exact named body,
operation and negative location/content requirements intact; hosted replay/tests
on pinned artifacts of BOTH historical runs, separate derived outputs only.
Develop checked generic const/mut helper/local-bound proofs from existing byte
resources/provenance and valid-layout/size_align specs. Local helper req may become
more explicit ONLY if discharged at every call; outer req and final posts unchanged.
Audit existing array__inv, provenance limits, is_valid_layout_size_of_align_of,
size_align as hypotheses until body/call proofs actually pass. Trace original
repr(align(8)) Z from Rust/export to VF size/alignment model, using existing
unchanged tool facilities only; no assumed size0/align8 or replacement type.
All six case names/runtime bytes/.add operations/domain/final posts preserved.
Official unchanged VF26.09/nightly2026-02-05 pins/flags/checks remain as original
card below; no new axiom, tool/spec/kernel patch or check suppression.

Budget maximum3 NEW manual GitHub-hosted runs, SUM of all relevant job durations
including setup <=5400seconds. Allocate <=30min job cap per dispatch; one active
experiment, log elapsed job duration and remaining sum before next dispatch.
Replay and verifier checks share the same hosted job so all execution is charged.
Every next SHA/run must test a specific correction justified by preceding evidence;
no unchanged rerun, no Re-run historical source. No local executable tests,
compiler/verifier/runner/extractor execution. Allowed static reading/editing /
syntax/document checks only. Commit/push and exact head_sha audit each run;
inspect full logs/artifacts; classify geometry/layout/controls separately.
Stop at achieved goals, run/time exhaustion or a concrete model/contract boundary
that needs prohibited extension. No further authorization queries within this scope.
No full sort4, RAPx/Kani rerun, B/C or external message/publication. Final report /
STATUS/log/plan/coverage commit/push; RAPx stays CLOSED / NO-GO, B/C NOT RUN.

Initial hypothesis for next correction: explicit nonnegative ghost-helper req is
provable at actual call from original array/provenance/valid-layout resources;
source-prefixed header recognition recovers exactly one intended body without
accepting parse/resource failures as negatives. Original full eventual normal /
five-unwind resource posts and deliberately partial geometry post remain below.
ZST calibrated layout is a separate gate; geometry/control success cannot replace it
or establish automatic copy UB coverage. Decision mapping unchanged for positives /
intended negatives; new semantic/model requirement means checkpoint without patch.

## Historical syntax-only continuation — authorized 2026-10-07

**CLOSED / INCONCLUSIVE,1/1 additional NEW runs used.**
[Run37532204465/source9474453 closeout](SORT4-ALIGNMENT-RESULTS.md#syntax-only-continuation--one-new-run):
syntax parsed; generic helpers fail nonnegativity before callers, ZST layout/add
unproved. Both negatives reject intended assertion on manual audit; raw automatic
all-six INCONCLUSIVE due missed header format. Export/decode/refinement6/6 pass.
No active run or further code/run authority. The authorization below is historical;
STOP after documentation closeout/commit/push regardless of result.

Owner explicitly
permits the correction described in SORT4-ALIGNMENT-RESULTS.md at b1ae937 and
exactly one additional GitHub-hosted manual H_align run,90min including runner
preparation. Entry clean matching local/remote
b1ae937f901ad34aeef8bcdbd98997abd1fd1969; correct fork/research branch, no active
experiment. Initial37529855468/source17ad1f4 remains historical INCONCLUSIVE.

Allowlist: remove the signature semicolon from aligned_step_const/mut and split
req/ens/on_unwind_ens into separate supported annotation blocks in all six Rust
functions. Statically compare checked examples, unchanged ghost payloads and
Rust after ghost stripping before dispatch. No predicate, lemma body, assertion,
case, hypothesis, domain, post, classification, runner/workflow, flag, tool/spec,
trusted premise or runtime-source change. Official unchanged VF26.09 /
nightly-2026-02-05 and all original pins/checks below remain frozen.
Commit/push correction, ONE new manual dispatch at the corrected SHA, match
head_sha, monitor and inspect full logs/artifacts, then document/commit/push.
No Re-run37529855468. Stop after this run regardless of outcome; no further
proof corrections/runs without a new decision. RAPx CLOSED / NO-GO, B/C NOT RUN.
No local compilation/verifier/research-runner execution or external message.

## Historical initial authorization — CLOSED / INCONCLUSIVE

Budget1/1 initial runs used. Run37529855468/source17ad1f4 passes six exports /
decodes / refinements but fails all VF annotation parses before proof obligations;
no geometry/layout/negative proof result. [Initial closeout](SORT4-ALIGNMENT-RESULTS.md).
The original scope/card below stays unchanged; its no-second-run limit governs
that historical budget. The current owner instruction grants a separate one-run
syntax-only continuation above.

Owner authorized on 2026-10-06 by “Давай запустим предлагаемую тобой проверку”,
from clean matching local/remote research HEAD
98c0f4f53eca6467a1e0ead8f0260f96b7d53dbc. Fork/branch correct, no active/queued
Actions at entry. This opens only the H_align gate proposed in
[SORT4-COMPOSITION-ASSESSMENT](SORT4-COMPOSITION-ASSESSMENT.md#one-next-bounded-check--proposed-not-run).

## Scope and budget

One NEW GitHub-hosted manual diagnostic, at most90min including runner preparation,
official unchanged VeriFast26.09/nightly-2026-02-05. Prepare handwritten isolated
fixtures/runner under research/challenge-8 and a minimal workflow_dispatch
selection; commit/push, dispatch exact SHA, inspect full logs/MIR/refinement and
artifacts, document/commit/push closeout. No second run granted by this budget.
No local compiler/verifier/executable tests/extractor, verifier/spec/kernel patches,
new trusted axioms, actual std runtime/signature changes, callback/copy full proof,
RAPx/Kani reruns, B/C, other targets or external messages. Stop after result,
inconclusive setup/domain failure or exhausted budget; semantic changes require
a separate decision. Ordinary preparation is performed before the one run.

## Experiment card

Target obligation: actual sort4_stable source and dst .add offsets0..3 preserve
alignment of valid Storage bases, including ZST. Std blob
 e555fce440872898e47fd5114f32eb15401d07df unchanged. H_align: existing pinned
size_align, valid-layout, division facts and actual typed pointer-add representation
suffice to prove that property without Copy/Freeze or semantic extensions.

Eventual target is the adopted contract's full current SrcOwn(s,V5), Shadow(dst,
pi(V5)), storages, F/frame normal post and all five current SrcOwn + RawDst + F/
frame panic posts, exactly one owner/no local debt. This diagnostic deliberately
proves only pointer geometry, with untouched raw storage permissions/frame,
normal aligned result and no applicable unwind. It has no comparator or copy,
creates no owner, reads no T or padding, and proves no caller/selection theorem.

Domain: arbitrary valid sized T, aligned nonnull bases with four logical legal
positions, raw byte permissions/bounds corresponding to four T slots, i0..3.
Base alignment is the adopted Storage premise, not an inferred fact from generic
points_to or RAPx. Source/reference initialization and ownership are not consumed
by a pointer-only operation; no functional/purity premise is introduced. Require
no independent result alignment. Positivity must derive from existing valid
layout; legal limits/offsets from byte storage and the existing pointer model.
ZST empty byte regions retain separately stated nonnull/aligned base/provenance
facts; the fixture does not invent four same-address T.own chunks.

Cases are isolated at export/verify/refinement:

- Generic const/source and mut/destination actual .add(i), i0..3: expected checked
  alignment result and preserved byte resources. Checked arithmetic helper body,
  no bodyless bridge or new automatic lemma. Source-linked operation, not a whole
  actual sort4 extraction.
- Concrete #[repr(align(8))] ZST model/layout calibration and aligned .add control:
  must establish size0/align8 from model/exported source, not an assumption.
- Two byte-offset1 false source/destination alignment conclusions from aligned
  bases with live raw-byte backing: expected failure at marked alignment assertion,
  no impossible typed cell premise. Fixed modulus8 states the actual Rust layout
  fact independently of whether the VF layout control succeeds. They check the
  arithmetic/post protocol, not automatic UB detection.

Frozen VF source809de4596839b739dd999f9e462242c835e3af46; official Linux release
SHA256 da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa,
nightly-2026-02-05. Record archive/executable/prelude/schema hashes, effective flags,
compiler target, exact fixture/runner/std/run source, per-case MIR/export/refinement,
full verbose proof and resource statistics. No skip_specless flag, no changed
unwind/leak/refinement policy; ghost-strip exact original/annotated byte audit.

## Operation-enforcement audit and decision map

Read-only pinned-source audit: size_align proves divisibility, valid layout plus
is_power_of_2_pos establishes positive alignment. Typed pointer addition preserves
provenance but must check legal limits. Typed points_to/array resources and the
copy_nonoverlapping summary omit an alignment clause; byte-to-typed conversion
requires it. No legitimate misaligned typed-cell copy pair has been found without
assuming the contested resource. Report this source-model boundary, not a counted
intended negative or a new runtime detector. No rewrite/manual assertion can
repair that boundary under this phase. repr(align8) model support is unconfirmed
and tested separately rather than encoded as a trusted alignment axiom.

Classify generic geometry, concrete layout and false-post controls separately.
Geometry PASS requires actual operation reached, both generic proofs/helper bodies,
full normal/no-unwind/resource post, export/decode/refinement and no skipped errors.
Negatives count only at their own marked alignment assertion after the operation,
with source/export/refinement intact; frontend/helper/resource failures are
INCONCLUSIVE. Layout-control failure means align8/ZST calibration unestablished;
never promote negative results under an unmatched layout to target detection.
A false conclusion proved in the corresponding valid domain is a scoped NO-GO
for that model/route. No automatic copy alignment coverage follows even if geometry
passes. Need source/selected-pointer/caller/operation/resource integration later,
not an automatically approved phase. Any missing support or semantic extension
triggers STOP without patches; RAPx0.7.50 A remains NO-GO and B/C NOT RUN.
