# First actual comparator: semantic card, before implementation

Status: DESIGN / NOT_RUN / NOT_PROVED. Owner merge; separate phase
MERGE-FIRST-CALLBACK-CLOUD-2026-10-17. Start 2026-10-17T00:32:42Z;
main deadline 02:32:42Z; finishing-only deadline 03:02:42Z. Fresh ceiling
960 Cloud seconds, at most one Build, timeout <=900 plus 60 queue reserve;
no carryover or automatic retry. Existing v3 coordinator only.

Policy read: WORK-POLICY at 6e1a8e59c56669abe5e6ec2013478e45ed2cc267,
addressed adoption 1e65f562994220a909ccf97903c36cb054576b76; local Evidence
Brief policy revision 2026-10-17 takes precedence. Preserve local instruction
changes and all three previous sessions. Baseline project checkpoint proof/infra
9e15014b5c62f94eb797e044d1f4ca9bd8cb74f1, Build
30bce9a0-29e8-4535-9060-ee6d9df2dccc, tool
a158398e336edce9817f62a55733a3470a986d7b, experimental v8 profile
0e67b038f940a9892dcb840747fbcc340532a31649979601af545acc41a0c68b.
Current project parent 7c02d329 includes later infrastructure history, not a new
proof result. New profile must be independently reviewed and exactly pinned
before any Build. Neither old nor new profile is accepted for integration.

## Exact source CFG and domain

Unchanged SmallSort blob 40939f922bcb6fdc7ee0d30427fa861827043827,
SHA256 85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1;
insert_tail body SHA256 9bc00f3913373e5879769b9970d66b1a56ada05a10205d51cafdf6533ecc2f29.
Mechanically specialize only T=u64; retain generic F: FnMut(&u64,&u64)->bool,
all legal comparator effects and panic. Actual wrapper initializes [10,20,5].
No runtime std or generic signatures are changed in the repository.

The CFG is: entry -> tail.sub(1) -> first &*tail and &*sift -> first actual
FnMut::call_mut at source541. Normal false -> original early Return.
Normal true -> original tail.read -> ManuallyDrop -> guard construction ->
loop copy -> update gap -> sift==begin? -> decrement -> late FnMut source566.
First panic -> original Continue (no live guard) -> caller unwind exit.
Late panic -> original Cleanup -> actual guard Drop -> Resume. Normal loop exit
-> separate normal guard Drop -> Return. Those paths must stay distinct.
Numeric bb IDs are deliberately not inferred from historical logs: fresh
compiler MIR spans, call identities and successors must bind this graph, and
an absent binding is INCONCLUSIVE. Full-body diagnostic retains every runtime
statement and identical final normal/unwind posts.

## Resource provenance and obligations

Entry owns array(begin,3,xs), length=3, foreach(xs,own<u64>(t)), tail=begin+2,
thread_token(t), type_interp<u64/F>, and current *is_less + F.own. Wrapper cells
come from its actual local array; comparator from its canonical input borrow.
No supplied receiver/FBC/origin/end-token/gap permission or assumed bridge.
The first cell remains framed. Existing proof splits singleton sift/tail cells
and their corresponding sole owners, closes full-borrow contents, borrows/shares
under fresh cmp_k, derives precreate and genuine ref_initialized resources,
opens two tracked fractions with their lifetime tokens, and packages the tuple.
No extra owners are introduced. The compiler-derived FnMut and Output clauses,
binder identities/order, type substitutions and lifetimes justify the callback;
a registration flag or reached statement does not establish this contract.

On BOTH normal outcomes and panic, consume exactly the returned temporary
reference fractions/tokens, close their fractional borrows, leave the local
lifetime binding, end cmp_k, borrow_end both original full borrows, open their
contents and rejoin singleton arrays/foreach owners with the framed first cell.
Restore CURRENT *is_less/F.own, thread/type/lifetime resources and caller frame.
Final posts existentially describe CURRENT arrays and F, not entry comparator
state. False must reach original Return; true must reach tail.read/guard with
all three initialized cells. Panic must run recovery before original Continue.
No loan or lifetime may escape its binder; no leak/assume and no purity/no-panic.

## Proposed narrow trusted delta and admission

Exporter/schema already preserve trait/projection boundRegions. Translator
currently discards Trait binder lists and recognizes only Param referents;
u64 cannot match either bound collection or call substitution. Preserve Trait
binders and admit exactly u64 in addition to the pre-existing generic case.
Require matching compiler trait/projection binder identities/order, exact bool
Output, two shared refs, same F/referent, unique clause and matching call MIR /
ghost substitutions with explicit same instantiated lifetime. Equality stays
call-local; no global HRTB instantiation and no new prelude/kernel rule.

First-call ghost recovery must be separately opt-in and bound to source insert_tail,
its unique first actual FnMut span, original normal successor and Continue.
Reject Cleanup, a second marker, wrong type/call, ignored unwind and late callback.
Use explicit close/scope-end/recover annotations and existing strict lexical
lifetime machinery. Attach the panic recovery to the first call alone, at a
local continuation outside its ended lifetime binding, preserving the actual
Continue return. Never use the old function-wide shared synthetic unwind
epilogue, or redirect late Cleanup to first recovery. If a local continuation
cannot preserve lexical environments without changing the kernel, stop with that
blocker; do not weaken scope checks. All commands remain ordinary checked ghost
proof commands and consume existing resources.

Official refiner: narrowly compare first source-bound Call unwind actions,
requiring original Continue == verified Continue. Mutation to Cleanup/Terminate/
Unreachable must reject at that check. Late cleanup remains explicitly
unqualified. Refiner exit0 without an affirmative first-edge check is insufficient.
No change to kernel, memory/alias/layout model or prelude.

## Controls and decision gate

Source-linked prefix check (explicit cut after first callback recovery, before
tail.read) must cover false, true and panic with full CURRENT resources. It is
partial and cannot substitute for full-body insert_tail. Full-body unchanged-post
diagnostic separately reports the next actually reached frontier.

Proof negatives: lose one ref_initialized fraction or corresponding token;
lose CURRENT F; lose one cell owner. Count only the intended resource predicate
at recovery/post, after verified HRTB admission. Earlier error is INCONCLUSIVE.
HRTB controls: wrong Output, missing projection, wrong F/referent, mismatched
instantiated lifetimes, wrong binder count/order/identity, binder/ref mismatch,
ambiguous projection and cross-body leakage. Refiner mutant: change first Call
Continue to another action, require the new official first-edge rejection.
New mechanism on late Cleanup must refuse at admission. Keep B1 positive/six
proof negatives/ten admission/four receiver-end-retirement controls, helper4,
normal/unwind, default-off and existing HRTB regressions. None are claimed run.

Independent patch review and exact source/tool/compiler/spec/profile/patch pins
are mandatory before Build. If candidate or controls are incomplete, no speculative
Build: checkpoint prepared work and precise blocker, with zero new proof credit.
After terminal Build only smallsort-brief UUID; no raw archive/log access, including
local copies. Missing/insufficient Brief limits claims; separate admin audit only
with explicit authorization. B2 remains open through full shift/gap/latepanic/
realcleanup/Drop/caller posts; generic T, ZST and profile I integration excluded.

## Implementation decisions recorded during preparation

The isolated prefix is named insert_tail_first_callback_prefix. It retains the
actual source segment through the first comparator/false return, cuts immediately
before the comment introducing tail.read, and closes the unsafe/function braces;
its true path returns at that explicit cut. The source-owned [10,20,5] wrapper
calls this renamed prefix only in that isolated case. This is a partial resource
theorem, not the full insert_tail body. Full-body diagnostic remains separate.

Three adjacent one-line annotations after the first if head configure the new
first_callback_close / first_callback_scope_end / first_callback_recover protocol.
The six checked fraction/token-close commands execute on both callback outcomes
inside the strict lifetime binding. A local normal-edge block leaves that binding,
runs the sixteen existing lifetime/borrow/owner/array recovery commands, then jumps
to the original normal successor. The first panic exits the same binding to a
local continuation immediately after it, runs those recovery commands and returns
the original unwinding outcome. No whole-function unwind epilogue or late callback
rewrite is installed. These are only admission facts until proofs succeed.

Exporter encode_region already maps ReVar/ReErased to the sentinel '<erased>.
Translator encodes that as InferredTypeExpr. The method's one late-bound argument
is synthesized as 'erased from late_bound_generic_param_count. New HRTB admission
checks those source forms rather than treating arbitrary source lifetimes as
wildcards; explicit source ref regions must match their ghost instantiation.
The compiler's universal clause, with retained ordered trait/projection binders,
is instantiated to the explicit ghost lifetime. Erased source regions themselves
are not identity evidence, and cannot replace actual reference-own/call proof.

Resource-loss fixtures are intentional negatives only: malformed fraction and
a stronger token assertion at the close step; a source ghost leak of CURRENT F
on false-return AFTER the markers; and opening the restored foreach, discarding
one cell owner and attempting to close it again. The last two are ordinary
negative-source instrumentation, not commands accepted by the new marker gate.
Positive source rejects leak/assume and retains every full normal/unwind post.
A negative that fails admission or before its intended recovery/post is
INCONCLUSIVE. This clarifies the no-leak invariant for all positive proofs.


Control clarification: u64's logical own predicate may be duplicable/empty;
therefore the cell-owner loss control splits off and discards the actual first
singleton array ownership chunk, then attempts array_join. Its intended rejection
is the missing physical cell owner at that join, not failure to recreate u64.own.
Only this explicit negative contains that discard; no positive proof does.


## R1 source correction rationale — before implementation,2026-10-18

Task merge-first-comparator-2026-10-18-r1; T019:04:30Z/main21:04:30Z/absolute21:34:30Z.
Tool52ba7e25/profile84949dd9 unchanged. Updated Brief now confirms translator,
exporter,decoder,console,refiner,tracked-md-compile exits0; first-comparator data
still absent. No new request for build confirmation; only unmatched gate/actual
first-comparator status requested for a separate bounded audit.

Source flow: profile selection in overnight/run.sh → selected-drop-minimal-v1
in insertion-onecell/prove.py → helper+selected.run → generated admission,
receiver,compatibility gates → matched → first-callback.py.run → prefix/fullbody/
negatives/classification.json+aggregate.json → dispatcher aggregate → package-evidence.
B1 matched false prevents invocation; absence in old Brief is not proof of NOT_RUN.

Concrete source defect in generated-glue-compatibility-controls.py:
_synthetic_defaults_gate always requires e232312e5f24ca98e25fe32fe0be5300eca4deda69438af2ebf90985061b3dc8
(old v8 refiner core), while selected profile pins d20a433c93563b87ff0a48241c94e366df06dba2f87b5e7f85ba47edb6980dd1.
Current tool52ba7e25 reproduces the latter Git blob. Both existing legacy synthetic
Drop constructors retain the exact defaults; two occurrences required. Thus a
source-level false refusal exists for the selected profile if this gate is reached.
Do not retroactively declare this the old Build's cause without its receipt.

Authorized correction: explicit reviewed profile→expected-source-hash mapping:
v8 retains olde232; first-callback-v1 requires exactd20a. Unknown profiles fail
closed; no wildcard/current-file-derived expected hash. Preserve two exact default
constructors and source+binary hash linkage, all compatibility/admission/receiver
controls and predicates. Tool/profile identities stay unchanged. Add an existing
classification.json compact source-gate receipt and a first-comparator dispatch
classification.json with prerequisite statuses/reasons and exact source/profile
binding. No proof credit from source gate or dispatched flag; future NOT_RUN only
when the actual fresh branch explicitly skips invocation. No trusted/refinement
semantics or proof contracts change.

Gates affected: legacy source-compatibility gate, aggregate matched, first-callback
invocation observability. Tests: both supported profile pins from immutable Git,
synthetic valid/mutated/unknown/default-count failures; synthetic actual dispatch
prerequisite false/success/exception receipts; publication/source closure and18base
pins. Independent Luna High review before one concrete corrective Build. Outcomes:
new Build establishes whether mandatory B1 gates qualify and first-comparator
campaign reaches real obligations; any next failure handled in existing scope,
never weaken guards or treat setup negative as intended proof rejection.


### R1 next hypothesis: consumed-marker placeholder bookkeeping (before implementation)

Fresh Build2f7ba4a0 executes first-callback prefix/fullbody cases, both report
INCONCLUSIVE/verifast exit2. Sanitized Brief context observes Not_found at
translate_fn_call List.find line3138; not an independently causal whole-Build verdict.
Source52ba7e25: exporter preprocessor.rs283 emits VeriFast_ghost_command for the
in-body first_callback_scope_end annotation. After exact first marker/protocol
validation, translator5982 filters that marker. The first_strict_scope_ends branch
6020 supplies only Noop at original closing brace, whereas old callback branch
supplies end_stmt at cut_l. Generic placeholder lookup3138 remains exact List.find.
Thus the validated first scope-end placeholder has no source-location statement.

Candidate minimal neutral bookkeeping correction: ONLY for the existing validated
first_strict_scope_ends branch, retain Ast.NoopStmt cut_l in addition to original
Ast.NoopStmt closeBraceLoc. Do not emit an extra logical scope end: real end stays
in existing generated scope_end_bb. No change to marker admission, strict-scope
checks, HRTB/binder/resource checks, CFG edges/labels, continuation placement,
cleanup actions, contracts/posts, kernel/model/prelude/exporter/refiner/runtime.
No general lookup fallback or accepting unknown marker. This maps an already
consumed control marker to a no-op, not a new ownership rule or unwind mechanism.
Independent reviewer must confirm this neutral boundary before candidate Build;
if it requires changing binding/CFG semantics, return decision to owner.

Hypothesis falsifier: new pinned Cloud cases must get past this lookup; successful
build alone does not confirm it, nor prove CURRENT normal/unwind resources. Keep
prefix/fullbody and all original positive/negative gates separate. Static checks:
exact one-line tool delta from52ba7e25, exact annotation retained, full ordered
patch reconstruction/sourcepins18basepins, no new changes outside translator;
existing synthetic dispatch/source gate tests unaffected. New identities for
translator/tool/combined patch/profile; refiner core pin remains d20a unchanged.


R1 receipt-path follow-up (before path-only correction): fresh v6 index projects
19 `/cases/` cases and first-callback target results, but neither standalone
outside-`/cases/` service classification is projected. Packaging source saves
all files; Reader support for other paths is unverified. Relocate ONLY the two
new no-credit classification files to `<existing-directory>/cases/<identity>/`
using the already observed nested `/cases/` convention. Keep outer directory
names, record contents, gates, statuses and proof predicates unchanged. This is
an evidence-path correction paired with the independently needed translator fix;
no extra Build is justified solely for reporting. Update synthetic receipt-path
assertion and source-only preflight expected path list; independent review before
submit. Reader nested-field projection remains a reporting limitation, not credit.


### Owner-authorized CURRENT admission correction — before implementation

2026-10-18T20:02Z owner explicitly approved the narrow proposal in
R1-CURRENT-RECOVERY-DECISION-20261018.md and independent review within the existing
R1 main deadline21:04:30Z. This is a separate authorized trusted admission delta,
not a neutral-typing claim. Exact checked recovery uses18commands: two current
points-to assert binders, owners/singleton arrays/foreach at those values,
existing foreach_append twice instead of undefined foreach_join. Framed first
cell, CURRENT final posts, physical resources/F/thread/type/lifetimes preserved.

Change only first recovery annotation assembly + its exact marker AST whitelist.
No new semantic primitive, permission/axiom, memory/layout/model/prelude/kernel,
HRTB rule, marker binding, CFG/unwind route or late Cleanup behavior. Both named
current binders must bind the exact tail/sift pointer respectively; exact own,
cons/nil, array pointers, append arguments/types and order checked fail closed.
All recovery remains ordinary verifier-checked ghost commands. Historical source,
profile and patch identities preserved, new candidate receives new identities.

Preflight: exact2a507868→new translator-only diff plus18base/14profilepins/14patch
reconstruction; synthetic pure annotation assembly and negative fixture mutations,
no local extractor/compiler/verifier. Independent Luna High source+admission GO
required. Full unchanged Cloud matrix checks prefix false/true/Continue-panic,
separatefullbody,4resource-loss negatives, compiler/HRTB/binder/lateCleanup/
firstunwindmutant and B1/helper/smoke/defaultoff/receiver/end/retirement. Earlier
setup/refusal is never an intended resource negative. No unchanged retry.


### R1 singleton-tail normalization — before implementation

Build3e7b74165/sourcee87f0d09/tool08d6a578/profile82973e1e: bothcases reachfirstcall,
localContinue/refinement, thenVF1 atsecondcloseforeach. Brief boundedcontext
fullbodylogf210c13e…713-716 showsfirstcloseforeachproduced atverified188:432 and
secondatt188:487 failspinnedlist181 foreach(t3,own<u64>). Currentownerclosureold
entryvalueblocker has passed; no prefix/normal/unwind success claimed.

Proof-only hypothesis: oldtail singleton's foreach tail t3 lacks explicit zero
length/nil normalization. Functionentry length(xs)=3, existing checked length_drop
and length_take establish both oldsingletonlengths1, hence their residual empty
tails align with nil. Insert exactly5pure checked ghostcommands before fresh
begin_lifetime and outside let_lft: length_drop(1,xs);length_take(1,drop(1,xs));
length_drop(1,drop(1,xs));note(length(take(1,drop(1,xs)))==1);
note(length(drop(1,drop(1,xs)))==1). No array/owner/resource production, assume,
leak, entry/current value equality, marker/whitelist/CFG or contract change.
Tool08d6a578/profile82973e1e/patch4aa84aa5 remainexact. Onlyproof/infra/closure
identities change. Ordinary proofannotation scope already authorized.

Gates: exactuniqueentryanchor, pure source annotation test/staleanchor refusal,
full14patch/16files/14pins/18base closure +independentLunaHighsourceGO; mandatory
matrix/5newadmissionnegatives unchanged. FreshBuild falsifieswhethertailforeach
nowrejoins; do not claimnextstage or weakenpostsifitdoesnot.

Before dispatch, strengthen only the pure normalization (6commands total): after
the two length1 notes, call existing drop_length(drop(1,drop(1,xs))). Its checked
post gives drop(length(lastSingleton),lastSingleton)==nil; length1 then makes
the opaque last foreach tail explicitly nil. First sift slice already succeeded;
no need new heap close or solver-dependent entry/current equality. Same proof-only
scope; exact recovery/tool/profile/controls unchanged.


### R2 source preparation — 2026-10-19T11:57:00Z, before implementation

Assignment merge-first-comparator-2026-10-19-r2; main13:57Z, absolute14:27Z;
phase MERGE-FIRST-COMPARATOR-R2-2026-10-19, stable owner merge, separate ledger
FIRST-COMPARATOR-R2-BUDGET-20261019.json. Policy checkpoint4c744fc5 plus preserved
owner2026-10-19 Reader update. Old accounts CLOSED; no carryover.

Old Build5f668cd9 Brief retains prefix214 placeholder and fullbody203 missing
points_to(tail0,_). Reader catalogue returns EXPLORATION_NOT_AVAILABLE_IN_REPORT,
index60c851a0dbe37bb68d9ff8131e4723d23ccc9139eeacff72133e136a02e0549b;
narrow reprojection request sent, no raw fallback. Exact prefix statement/hash
not established; do not edit it merely from line number.

Independent fullbody hypothesis: CURRENT18 rejoin closes array(begin,3,CURRENT),
so points_to(tail) is encapsulated. Immediately before original tail.read,
bind CURRENT array list, checked array_split(begin,2), open its tail singleton.
Pinned prelude_core.rsspec252-285 defines physical array and checked split;
no ownership synthesis, entry=CURRENT equality or assumed pointer permission.
Framed prefix array and foreach CURRENT owners remain. This is outside exact
first-call recovery marker/whitelist; runtime, generic F, CURRENT F/thread/type/
lifetime/frame, normal/unwind posts and prefix cut stay unchanged.

Expected falsifier: fullbody must pass tail.read points_to obligation, then
report next actual frontier; new unsupported/assertion failure is not success.
Prefix+all controls and B1 regression matrix run unchanged; incomplete prefix
remains no-credit. New Build for this proof candidate, never for missing reports.
Tool08d6a578/profile82973e1e/patch4aa84aa5/translator2ff7b16f/compiler
nightly2026-09-25 frozen;14patch closure/18basepins/run.sh unchanged.
Independent Luna High GO, source closure/config publication before submit.
Technical ceiling18960s =9000s absolute window +960s max reservation +9000s
rounding/bookkeeping headroom; client representation only, deadlines and one
owner Build govern, max timeout900, project-wide task limit2 despite v3 max3.

R2 safe-boundary adoption2026-10-19T12:27Z: owner ITERATION-PROCESS.md
SHA256c35810ee84013947aac27fe8289ce95043aa819ffb7e58bf9c19da7488f31289
read from newly supplied local docs. T0/deadlines/Build1release/tool unchanged.
Build1 type=proof; measured590Clouds/execution589, stage setup/compile/proof
durations not obtained; elapsed wait for bounded source separately unmeasured.
Closed full-target obligations0; observed fullbody frontier advanced from read
points_to to next guard address expression, prefix/controls still open.
Existing compile-preflight.sh is invoked through run.sh modes from merge.sh
403ff/BUILD-MODE selected-drop-minimal; do not claim a new gate merely from
presence. Next proof-only candidate should use exact target then all mandatory
dependent controls, no redundant separate compile-only experiment or cache.
Unchanged first-callback runner already explicit NOT_RUNs dependents if prefix
fails; baseline B1 gates remain dispatch dependencies. No runner/collector result
shape changes here; new tail annotation's unique/absent/duplicate anchor synthetic
test and phase fail-closed checks already PASS. No additional test or Cloud run
solely for this documentation adoption.

R2 closing evidence-only followup 2026-10-19T14:00:01.678801+00:00: ownerv0.9 guide/tasks queries
read; targeted fixed prefix210–216 with expectedSHA returned OK/exactTrue,
request09896cf5d49efd171e190aba4a60739a577f5fcc32cea43c4612cd75197a7e9d.
Line214 is values.as_mut_ptr wrapper, columns17–23 array receiver values;
sourcehashdd2e5689 matches old catalogue/preparation and exact pinned wrapper
literal. Missing-source blocker resolved, cause/type/lifetime binding not proved.
Main13:57 cutoff elapsed before response; no new proof edits, experiments or
Builds. LedgerCLOSED1Build590s, no own active/unresolved/reservation/request.
Next newly authorized window: minimal wrapper receiver typing investigation,
checked annotations within frozenprofile, LunaHighreview, fullgates.


### R3 session opening — 2026-10-19T16:09:27Z

Assignment merge-first-comparator-2026-10-19-r3; owner merge; main18:09:27Z,
absolute18:39:27Z; separate FIRST-COMPARATOR-R3-BUDGET-20261019.json, explicit
3600Cloud seconds, max timeout900+60reserve, existing v3 coordinator only.
Policy HEAD020ed4cc plus supplied local ownerv0.9/ITERATION-PROCESS adopted;
old accounts CLOSED/no carryover, tool08d6a578/translator2ff7b16f confirmed clean.
Target actual u64,array3,genericF firstcallback source-linked prefix false/true/
firstContinue-panic/fullCURRENTposts +4resource/admission controls; second path
fullbody guard frontier after preserved R2 checked split/open. Full B2 stays open.
First necessary evidence binding: archived prefix214 arrayreceiver values to
actual proof-AST/MIR type/region node, not an inferred erasedlifetime diagnosis.
Exact Rust fragment already retained; do not request again. AST catalogue
identity34ea04bf…/SHA3193176b… known but retained projection unsupported. Seek
source-location/node localization before narrowrefresh; no guessedoffsets or
window reconstruction. Secondary read-only guard investigation assigned to
LunaHigh, no nested agents/no refresh without coordination; no tool writes.
No proof/runner candidate or Cloud experiment yet. Any future hypothesis/gates
recorded here before implementation; exactclosure/config/publication+GO required.

R3 explicit owner extension: «Добавляем полтора часа к основному времени».
T0 remains2026-10-19T16:09:27Z; newmain19:39:27Z, finishingabsolute20:09:27Z.
Original deadlines18:09:27/18:39:27 preserved as history, not reset. Cloud
ceiling remains3600, no new trust/profile/runtime authority or oldbudgetcarryover.
Owner also directs work without forthcoming AST-locator projection in this
session; no guessed offsets, raw fallback or source-cause invention. Continue
available retained evidence/source tracing and independent fullbody path.

R3 phase registration preflight before implementation: add exact R3 branch to
existing control.py authorization only (owner/ledger/lane/3600ceiling/T0/new
deadlines/timeout90..900/pinned source), and existing lastmoment recheck.
No common coordinator/transport/tool/proof changes. Synthetic service checks
cover valid account and wrong/missing identity/deadlines/lane/timeout/closed.
Fresh Cloud still requires an independently reviewed concrete proof candidate;
registration alone cannot justify a reporting-only or speculative Build.

R3 prefix AST evidence: exact archived proof-ast.ml SHA3193176b…, index3e3e6bad… .
Header1 gives source_lines925; one EOF final-declaration window914–925 binds
wrapper source215/216. Bounded call context902–913 binds source215 callee; its
immediate predecessor890–901 contains source214 CastExpr. Four target requests
are retained separately,37lines total/925, no file reconstruction, byte offset
guessing, withheld bypass or raw archive access. Request dd82ccf0… establishes
AST895 at source214:17–23 with RustRefTypeExpr(InferredTypeExpr,Mutable,Slice<u64>).
Checker CastExpr4910 strictcheck→RustRefType2226→Inferred2240/2252 explains
observed placeholder. MIR region itself was not read; frozen Cast3777→ref1541→
region568 is the source-inferred origin, not a separate MIR observation.
Targeted's parser_input_bindingNOT_ESTABLISHED and wholecausalUNKNOWN preserved.
Call AST897 at214:17–36 has different Inferredgeneric; altering callghostargs
does not modify earlier cast895. Schema CastData has no ghostarg annotation,
FnCallData does. No currently established permitted proof-only correction yet.


R3 Literal Locators v0.10 follow-up, instruction52da95cb: resumed19:46:16Z,
after extended main19:39:27Z, T0/absolute20:09:27Z/Cloud3600 unchanged. Adopted
current guide/locators at safe boundary; no new proof hypotheses/edits/Builds.
Existing AST895 observation reused. Addressed old prefix decode.out SHA70be7daa
now directly exposes move_5→_4, target erased region/mutable slice_u64 and
pointerCoercion; local type/whole enclosing binding still incomplete. Exporter
records PointerCoercion subtype as unit, so Unsize is not an observed MIR fact.
Nine MIR targeted delivered responses;10th budget-exceeded, no quota bypass.
Guard fullbody **R2 Buildc78529d0** separate AST SHA2757ca2a locate returned
LOCATE_WITHHELD; stopped that file without alternate selectors. Both remaining
projection needs sent for administrative safe handling. Prefix metadata gate
now traced through pointer model/ptr_len/slice borrow and identity Upcast;
no established length3 construction for this coercion. Proposals updated with
minimal future Cloud reproducer and distinct exporter/model decisions. No new
proof credit or control execution; frozen tool/runtime/posts remain unchanged.


R3 closed-account v0.11 follow-up, instruction6b688232, start21:02:57Z;
recorded 2026-10-19T21:14:37.072412+00:00. New guide/reference adopted: economical-exact-v1/schemaV2,
old quota/WITHHELD lifted, client0b14d80b. Actual MIR local5 mutarray3/u64 and
local4 mutslice/u64/erased regions, body/span and stageargv now available;
guard actual scalar declaration/merge/address bound. Previous admin projection
requests resolved for those fields. Metadata actual arrayStorageLive→none→
identityUpcast still lacks length3 construction. Guard missingcont consequence
source-derived; checked finitefraction ghosthelper is alternative only ifactual
resource decomposition is proved. No code/proof/tool/Build or closedaccount
change; no new proofgatecredit. Current diagnosis/proposals/provenance updated.


## R4 trust decision BEFORE implementation — 2026-10-19T21:24:56Z

Owner task merge-guard-addressability-2026-10-20-r4, instruction56aad505.
New T0 2026-10-19T21:24:56Z/main23:24:56Z/absolute23:54:56Z, own ledger3600Cloud
seconds, no prior headroom carryover. Baseline tool08d6a578, profile82973e1e,
translator2ff7b16f, verify_expr8883a76d (CRLF). Authorize exactly one change:
MergeFractionsStmt scans its assertion then invokes existing cont locals once.
CPS tail visitation marks actual later AddressOf uses under existing rules;
no new ownership, memory/alias/layout or prefix coercion rule. Preserve every
other tool byte and old14patch chain. New experimental profile retains all
source pins except verify_expr plus explicit new tool/patch/profile identities.

Actual obligation: source-exact fullbody CopyOnDrop src:&*tmp after CURRENT
read with original full normal/unwind posts. Falsifiable hypothesis: resumed
prepass sees actual tmp address, performs existing physical allocation, and
passes prior error20749–52; a new failure is a new frontier, not whole proof.
Cloud gates on the actual candidate: address before/after/within merge and
multiple merges; unrelated local/unicity; physical allocation identity and
normal/unwind/storage resources; intended missingowner/beforeLive/afterDead/
unsupportedoperand negatives. Existing compile-preflight first, then controls,
actual fullbody and full retained mandatory matrix by dependencies. Prefix
lifetime+metadata known failure stays separate, prerequisite skipped negatives
are not PASS. PASS permits proof-only iteration in same scope; setup failure
requires delivery repair; other trusted changes require a new decision.
Independent Luna High actual-diff GO before submit; local activity remains
hashes/static composition/small service tests only. No fractional helper inR4.

R4 candidate before first submit: toola42d50becbc84a45e33a58269358eee105f1fdcb,
verify_expr97f5e50cbba0423338b096410ecbcc77d541b73efce30ef15220c6485891a5cd, patchf17866533a1cce7365d432a0d66cbcd9472a87cc44b027d67a78aa46bbbfd3e6,
profileSHA77164792cfca039fe8b2a993a198a545a74a074480371dba5f454a5e86709c66. Static15patch/16files/14sourcepins/18base
PASS;4wiring tests+syntheticcaseclassifier error paths PASS. Independent LunaHigh
GO_SINGLE_PINNED_CLOUD_BUILD in R4-REVIEW-20261020.json. FirstBuild hypothesis:
compile exact tool then new controls actualflags/normalunwind/storage; original
fullbody proceeds past unsupported AddressOf(tmp)207 to a new checked frontier.
Preserve CURRENT array split/open and full final posts; known prefix placeholder
remains expected independent limitation, NOT proofnegative success. Build type
mixed (tool/classifier/proof), timeout900/account reservation960 within3600.
No source/infra SHA claimed executed until fresh terminal receipt.


R4 Build1 terminal f6627644/sourceca1d6cb1: FAILURE,649Cloud/execution648,
all7toolmilestones exit0. Actual sourceexact fullbody now reaches create_ref at
originalguard20749–52; next diagnostic aliasing.rsspec88 missing
ref_precreated_token<u64>(tmp_addr,_). Prior unsupportedAddressOf not observed.
No guard/fullbody theorem. Prefix remainsINCONCLUSIVE/resourceadmission skipped.
Addressability negatives missingowner/afterDead sourceEXPECTED_REJECTION;
positives andothernegatives INCONCLUSIVE, including normalunwindE0596 immutable
local rawmut fixturebug. No toolqualification or formalcredit.

NEXT hypothesis BEFORE edits: frozen precreate_ref requires true and returns
only reference-init permission/token; init_ref_readonly consumes actual physical
tmp points_to coefficient f and splits it into f/2 parent +f/2 reference, with
readonly-end token. Add these existing checked operations only after original
tmp initialization before original guard, typeu64/physical &tmp, fullbody-only.
No numeric equality bridge or new kernel/model rule. Full CURRENT finalposts
and resource/leak checks remain, including outstanding readonly-end obligation;
this is deliberately partial guard-frontier diagnostic, never wholefunction
proof if later cleanup/loan restoration fails. Do not touch lateCleanup lowering.
PASS means prior tokenprecondition passes andnextcheckedfrontier observed;
missingpermission means inspect actual fraction/source, not assumeownership.
Same tool/profile strictpins remain. Separately repair controlfixturemutability
and strengthen multiplemerge physical alias identity/readwrite checks; adjust
oracles only after exact intended errors/stages are observed, not arbitrary
setupfailures. Independent LunaHigh newdiffGO before newpublishedBuild.

### R4 candidate2 controls hypothesis, 2026-10-19T22:15Z
Targeted Build1 after-merge verifier fragment155–166 confirms successful return/leak check followed by `verified/lib.rs(15,5-24): dead code` at the deterministic runtime `assert!(local == 8)`. Exporter/decode/refinement were0, verifier1. Hypothesis: constant-condition assert panic branches trigger retained dead-code rejection. Replace deterministic fixture value/identity assertions by checked ghost assertions; keep physical pointer write/read as runtime operations and dynamic flag panic branch for normal/unwind. This preserves dead-code checking and full posts, without classifying Build1 as PASS. The real candidate must discharge the new ghost checks in Cloud. No classifier oracles relaxed.

Candidate2 negative fixture follow-up: exact Reader unsupported error is Parse error at9:20–22 (`1u64` ghost literal), not intended AddressOf refusal. Use ghost integer literals `(1 + 2)` instead of Rust suffixed literals, keep same non-lvalue shape/message gate. beforeLive is Unbound variable local at9:19–24, remains INCONCLUSIVE; no frontend failure upgraded to intended storage rejection.

R4 emitted-flag limit: exact Build1 Rocq flag catalogue contains no `local` entry. Frozen verifast.ml deferred Rust storage declaration branch (guard includes address_taken, lines1113–1135) registers storage and returns without calling rocq_print_local_addr_taken. Thus absence is not false, and guessed generated binder names are inadmissible. Retain strict local gate/INCONCLUSIVE and distinguish future actual exit0/resource/target-path observations from final-flag qualification. Do not modify the frozen emitter or infer full profile qualification. Original actual Const tmp AddressOf frontier remains independently observed through the checked create_ref precondition failure.

Policy read at safe boundary, 2026-10-19T22:31Z: user replacement AGENTS instructions and local PROOF-AGENT-AUTONOMY owner decision read. New-task autonomy does not enlarge explicit active R4 prefix/emitter/model scope; current T0, source25e7c1c7, reviewGO, ledger/reservation unchanged. No automatic maintainer handoff or Actions dispatch.

### R4 candidate3 first-shift geometry hypothesis
Build2 d43ddfb4/source25e7c1c7 reaches original first copy at verified215; exact source error std/lib.rsspec627:143–145 cannot prove sift alignment. Precreate/initreadonly/actualguard passed, no theorem credit. Hypothesis: existing physically owned CURRENT prefix array still hides the source cell; open its second singleton and invoke already checked concrete initialized_storage_alignment/points_to_limits and destination uninitialized_storage_alignment/points_to__limits. Establish all literal-count1 copy geometry (nonnull/alignment/extent/objectlimits/disjoint) from actual resources and same-allocation offset relations, not numeric equality as ownership. Prepare only the initial shift before original loop; later loop preservation/callback/readonly-end/cleanup obligations remain checked under full original normal/unwind posts, and failure there is a new honest frontier. Do not introduce a partial loop invariant or change source CFG/posts. Success: original shift call passes and actual update or later checked frontier is observed. Failure in the new annotations: inspect CURRENT resources/arithmetic, no assumptions/model relaxation. Same tool/profile/pins/matrix and independent Luna deltaGO before dispatch.
