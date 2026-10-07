# S7 exact local-guard forget design

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
