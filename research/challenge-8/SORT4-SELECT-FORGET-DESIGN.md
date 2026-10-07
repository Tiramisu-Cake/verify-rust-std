# S7 exact local-guard forget design

Current: **STOP at independent positive dead-code gate; forget NOT ACCEPTED.**
[Closeout/evidence/budget](SORT4-SELECT-FORGET-RESULTS.md):4411used989remaining,
noactive; v4 and original classifications unchanged. Historical BEFORE cards follow.

Owner2026-10-07 resumes from ffa370a5197ecb06fc74e4352371453ac67523d6.
Same5400 summed jobseconds;3954used/1446remaining, no reset. S6v4 accepted/frozen,
original classifications retained. All executable work hosted-only, one relevant run.
S7 authorizes exact source-linked forget for local DropOnPanic<*const Element> only.
No assume_init/generalDrop/union/refinement/memory/provenance/kernel extension.

## Proposed route and trust before implementation

Repository core::mem::forget<T> at mem/mod.rs162–164 is exactly
`{ let _ = ManuallyDrop::new(t); }`; file SHA256
1db195d24508e4eef81163672d008667765c2c121f4fa70f8752742e11106273.
ManuallyDrop source SHA17e8e41866d3eadcfdc6f1a516e4ed9dd5555e10ad725aac3b04aec7c759731b;
its new uses MaybeDangling::new(value). Existing pinned stock translator maps
ManuallyDrop<T> to T and new(arg) to arg, without own precondition. This existing
trusted representation/operation correspondence is not proved by checking forget.
No new general ManuallyDrop rule is proposed; qualify only lexical imports.

Stock generic forget still requires thread_token & <T>.own. Private local guard
has false own in the frozen translator. SAFE compatibility under false own can be
vacuous: it neither supplies actual guard-own nor establishes body correctness.
Do not change that predicate, introduce guard-own=true, or derive arbitrary slot
rights from pointer bits. A new guard ownership model would require a separately
reviewed protocol consistent with actual Drop and inaccessible-slot negatives;
if needed here STOP before implementing it.

Candidate: nested unsafe checked_forget_guard<Element>(t:DropOnPanic<*const Element>)
inside the unchanged actual select owner/guard declaration scope, with exact
source forget body and reachable explicit req thread_token(?tid)&tid==currentThread;
ens same token, on_unwind_ens false. Unsafe proof adapter avoids relying on SAFE
prototype compatibility; actual Rust forget remains safe and unchanged. This is a
narrow body/call correspondence proof, not a generic token-only forget declaration.
Arbitrary valid guard raw-pointer values acquire no targetcell/Element permissions.
Wrappercells/value/thread and external borrow tokens remain independent frames.
Positive callers retain distinct initialized cells and tokens, without consuming
wrapper ownership into guard. Nonempty body must execute, return and pass leak;
helper header alone or false-own compatibility cannot count.

Exact nominal identity must include ADT defpath select_unpredictable::DropOnPanic,
struct kind, Element substitution *const Element, sole private inner:*mut T,
source declaration/generic owner, actual Drop implementation hint.rs851–855 and
its typed relationship. Never use a same-shaped external surrogate as acceptance.
Source hintSHA d94ef86fbdac952fe7c9a6028536e15539b33dc188966fa4e9340fa7d94c30f8.
Actual Drop dereferences inner; no proof of it is implied. Integration needs exact
caller MIR showing drop flag cleared, guard moved to forget, normal+cleanup edges
retained; accepted drop/no-unwind and checked forget/no-unwind must exclude every
reachable guard destructor in the admitted prefix. If reachable guard cleanup
requires a new guard/Drop resource protocol, STOP with its exact obligation.

## S7a first diagnostic, before any new admission semantic change

No captured forget-body typed MIR exists. First capture both NORMAL and readonly
full MIR on a disposable copy of actual v4 projected source plus a lexical ManuallyDrop import and two nested
include! items for helper and frame probe, each a single fn in a separate source file. Preserve exact actual body/guard/Drop and runtime
forget invocation; helpers are source-linked additions, not an actual redirect.
Explicit source-insertion manifest, ghost-strip original/verified identity and
source/refinement checks over lib.rs AND both included file pairs must hold.
Pinned import/include items add declarations only; full actual runtime MIR confirms no
new executed operation. The original local guard/Drop source remains unchanged. Use frozen v4 tools/patch c7cc08a9 unchanged,
compiler/nightly/schema/exporter/refiner frozen. Explicitly unset all admission
REPO_ROOT flags: the inserted includes intentionally fail the old exact-source
certificate, so that gate is INACTIVE and no redirect occurs. Isolate the actual
function prefix from v4: omit only unused appended constructor/asptr/drop adapter
declarations whose union bodies need active source certificate translation; record
the omitted declarations and unchanged full actual function/guard/Drop source.
This is a diagnostic isolation, not an actual-integration admission change.
A diagnostic label is separate
from tool profile, not a new semantic proof profile or accepted component.

Pinned focus matches inclusive file/range, so a helper defined directly in the
parent file would ALSO select and fail the actual parent before the helper.
Use one lexical `use std::mem::ManuallyDrop` item and two include! items in the
exact local guard scope, with helper/probe definitions
spanning separate files; focus on their actual file/line excludes parent lib.rs by
path. This lexical-isolation hypothesis is not yet tested. Record macro expansion
filepaths and nominal defpaths, and require actual intended helper/probe body entry;
parent/setup failure is never an intended result. Focus explicitly leaves every
other function unproved. Record
focus argv/line/function, satisfiable explicit pre, body execution/return/leak and
full raw log. Execute positive body and frame preservation; independent negatives
false body assertion, wrong post/framevalue and thread/frame loss or duplication
must reach their specified body/post/leak obligations, matching exact focused
function, first-error location/line derived from annotation and diagnostic predicate.
Thread/frame loss requires named body return+leak-check with intended leak error;
duplication requires exact missing thread/cell chunk at named post, wrong-value
requires its post equality. Any other error in same file remains INCONCLUSIVE.
S7a only tests payloadcell/frame/thread: separate borrow-token regressions remain
NOT RUN until full admission/matrix stage. Setup/frontend/unrelated
failures remain INCONCLUSIVE. These are diagnostic hypotheses, not a full matrix
or admission acceptance. No redirect/actual integration in S7a.

Expected full MIR includes sole typed ManuallyDrop::<exactguard>::new with moved
argument, typed discard temporary, unitreturn, exact normal/unwind CFG and no
Drop/extraoperation. This is an unconfirmed hypothesis; first hosted capture will
fix exact counts/spans/operands before any checker is implemented. Diagnose cleanup
rather than weakening expected graph. No extra path ignored for acceptance.

Workflow new selector forget_guard_stage defaults drop_v4 (preserve old route),
forget_diagnostic selects isolated new runner under existing proof selection.
Cap new job20min/1200s including preparation+120s cleanup reserve, proof<=300;
actual duration charged to1446remaining. Original v4 runner/checkers/patch unchanged.
Outcome: setup -> narrow repair; reachable helper-body resource/memory barrier ->
record and STOP if separate model needed; nonvacuous body+exact MIR -> design full
S7 admission/profile/matrix/regression BEFORE implementation, then accepted-only
redirect actual forget until next blocker. No allpaths helper claim from a prefix.

## Required acceptance after S7a (not yet implemented)

New redirect profile must preserve byte-pinned v4 and rerun necessary full ctor/
asptr/intrinsic/drop/14baseline+19actual controls. Independent S7 positive body,
frame/thread/token cases; insufficient resources, false/wrong post, cell/value/
thread/borrow loss or duplication and no assumption guard-own. Admission negatives
source/body/import/nominaltype/field/substitution/Dropbody and full typed MIR callee/
Move operand/result/unitreturn/noadditionaloperations/normal+unwind CFG. Each negative
only counts at its named required obligation, retain all independent results.
Fullsource/readonlyrefinement/NORMALmethod+caller cert before redirect; actual runtime
forget and cleanup retained. Canonical actual only after these gates. On forgetpass
STOP at next substantive blocker; assume_init remains outside authority.

## S7a first outcome and source-pair repair BEFORE implementation

37665233357/2ba63774:133s,4087used1313remaining. All9 setupfailed beforeexport/proof;
no MIR/runtime-body evidence. Exact ghost strip keepsfour newline separators after
removing3contractblocks. Originalhelper/probe must retainthat EXACTscaffold, justas
prior source-linked fixtures derive original fromstrip ofverified. Preserveverified
runtimebody and exactsignature+scaffold+body comparison, no generic normalization.
Hostedall9 constructionpreflight precedescoldbuild, thensamev4/newrun full diagnostic.
No changed expecteddiagnostic/classifier or admission semantic; all originalresults
remainINCONCLUSIVE. This is a harness correction, not a new semantic hypothesis.

## S7a expression-isolation card BEFORE implementation

37666273705: all9 source pairs PASS construction, but compiler rejects statement
include containing fn; no MIR/body/refinement evidence. Preserve those raw results.
Reviewed isolation candidate: retain lexical ManuallyDrop import, replace the two
statement includes with `const _: () = include!("forget-items.rs");`. Included file
is exactly one block expression containing both independently generic unsafe fn
items and final unit `()`. Single actual guard declaration/Drop unchanged. No
runtime call introduced. Compiler include make_expr and exporter recursive HIR
walk support this hypothesis, not proof of nominal/spans or frontend compatibility.

Full original/verified included-file bytes must match after exact ghost stripping;
preflight/regeneration hashes cover all four files. Focus on separate fn lines in
forget-items.rs must exclude parent lib.rs and the sibling. Nine independent
body/frame/thread cases and intended predicates unchanged; first-error line is
recomputed from exact annotations/function closing brace, not relaxed. Compiler,
export, nominal/macro-span/refinement failures remain INCONCLUSIVE. Existing v4
patch remains byte-identical, admission flags inactive, no actual redirect.

Capture exact anonymous-const helper defpath, original local guard ADT and typed
substitution, both full MIR exports, focus body entry/return/leak and refinement.
Actual MIR must show no extra runtime operation; expansion spans require evidence
before a future source-pinned admission. No general const/frontend/refiner patch
is authorized. If body demands a new guard/Drop/memory protocol STOP with precise
obligation; a proved body only permits designing full new-profile matrix BEFORE
implementation, not accepting the component or redirecting actual yet.

Remaining1191/5400 summed jobseconds (4209used). Next diagnostic cap18min1080s,
120s reserve, per-proof300s; charge actual duration, no reset, one hosted run.
V4 default25min route unchanged. Routine isolation repair only; no classifier or
expected-predicate rewrite, no admission semantic change.

## S7a macro-item isolation card BEFORE implementation

Run37667942855:99s,4308used1092remaining. All9 readonly export/decode/refinement0,
NORMAL/focus1 incomplete_include; no body proof. Frozen preprocessor unconditionally
appends3fnstubs to every non-toolchain file. No per-file option; no lint allow,
toolchain-path bypass, no-preprocess or preprocessor/refiner change. Direct impl
include unsupported (MacResult make_impl_items=None); inline const focus also
selects actual parent first. These are rejected source-isolation candidates.

Next falsifiable source-only hypothesis: crate item module forget_items contains
one macro_rules definition plus its pub(crate) re-export. At the same actual local
guard anchor, retain lexical ManuallyDrop import and invoke that macro with sole
ident argument DropOnPanic. Macro declares exact helper/probe items; only guard
identifier is supplied by caller, no runtime call generated. The macro-file EOF
stubs are legal module items. Original actual guard/Drop and target contract/body
remain unchanged. Four original/verified files and both exact insertion sites are
source-pinned; full ghost-strip/preflight/regeneration/stage hashes required.
Exact forget runtime body unchanged; template signature uses $guard, its MIR MUST
resolve to original nominal local guard, never a new type or ownership assumption.

Same9 independent cases and exact assertion/post/leak predicates, locations from
selected macro fn segment; no classifier change. Require body focus/contract spans
in macro file, parent excluded, exact nominal/generated FnDef, normal+readonly full
MIR and source/refinement. Expansion status is captured, not a generalized v4
admission relaxation; all admission flags remain inactive/no redirect. Existing
v4 patch/source/tools unchanged. Retained MDnew cleanup must be discharged by body
under existing model; no-unwind is NOT inferred from readonly syntax. Independent
cells/thread/resources and own=false boundary unchanged; borrow full gate NOT RUN.

Any failed macro ghost/focus/MIR association -> record exact failure and STOP for
source-isolation/frontend design reassessment, no further syntax guesses or general
frontend extension. Body memory/guard protocol need -> STOP with obligation.
Nonvacuous body success -> BEFORE-design full separate profile/gates, not acceptance.
One hosted diagnostic cap18min1080/reserve120/perproof300 fits1092remaining; charge
actual duration, same5400 summed jobsecond budget, no reset.

## S7a final decision

37669436220: macro source/focus/ghost association works; both exporter modes and
refinement pass all9, exact nominal helper/probe bodies captured. Both positives
execute body/return/leak under reachable thread/cell/frame premises, but complete
focused verifier exits1 on mandatory global dead-code gate. Seven exact intended
raw errors are not an accepted full matrix; all9 original INCONCLUSIVE retained.
Negative regex counts both execution header and note; no classifier repair mixed
with this experiment. Full admission/newprofile/regressions NOT RUN, no redirect.
STOP for independent acceptance design preserving complete dead-code/source/MIR/
nominal checks; don't suppress checks or reverse callee-before-caller ordering.
No body guard-own/Drop protocol necessity established; actual still at old forget
own obligation. Same4411/5400used989remain; no active job, no further dispatch here.
