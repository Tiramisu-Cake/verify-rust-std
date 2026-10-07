# Pointer select completion — dependency map and reviewed design

2026-10-07: map completed before implementation; component work IN PROGRESS.
[Authorization/phase](SORT4-SELECT-POINTER-PHASE.md),entrycd44e1bb.
Existing accepted constructor O4 profile325af428 remains frozen.
Complete map and initial storage design were committed before semantic edits.
Accepted as_mut_ptr and S5k intrinsic profiles have separate evidence below;
packaging introduces no proof semantics.

## Complete dependency map BEFORE semantic implementation

Source authority: pinned hint.rs SHA256d94ef86f/blobfe591663, helper body
0d4233fe; unchanged VF26.09 base809de459/nightly2026-02-05 with accepted
constructor patch325af428. Exact pins are in the preceding O4 closeout. All items
below are pointer-only plans; unavailable names are not evidence of impossibility.

| Dependency / exact specialization | Available frozen support / target contract | Source link / proposed trusted delta |
|---|---|---|
| MaybeUninit::new<*const Element>, twice | O4 checked SAFE body; token, defined value own, inner=some(input), no unwind, no pointee permissions. Regression in changed profiles. | maybe_uninit.rs398, runtime body26a6c870; unchanged accepted constructor certificate/body, not a new rule. |
| SAFE MaybeUninit<*const Element>::as_mut_ptr(&mut self) -> *mut *const Element, twice | Existing mutable full_borrow/create_ref_mut/end_ref_mut and PtrToPtr casts. Preserve full modeled storage pointer and existing storage inner option, thread/borrow/frame/no unwind; allow unknown/none/some, no reads or invented initialized cells. | maybe_uninit.rs648 exact two-cast body. Source-local lifetime/type specialization and sole receiver rename; full typed MIR signature/operand/cast/result/CFG admission before external redirect. First diagnostic uses frozen existing model, no redirect. Defined fbc packaging if needed, below. |
| Intrinsic select_unpredictable<*mut *const Element>, twice | No stock intrinsic contract. Exact result=if condition then a else b as complete modeled value; pointer-value ownership only, resources of both storage cells remain independently framed; no unwind. | intrinsics/mod.rs492 has rustc_intrinsic+nounwind and pinned fallback if/forget. NEW explicitly trusted type-exact selection translation; do not claim Rust intrinsic-body proof. Certify identity, generics/types, argument order, destination, edges; reject other T. |
| Intrinsic select_unpredictable<MaybeUninit<*const Element>>, once | No stock rule. Exact selected wrapper value/inner and value own; retain storage resources through caller moves and account for unselected value ownership (empty here). No initialization assumption; no unwind. | Same intrinsic declaration/semantics, separate exact-type rule and source/MIR certificate. Initialized/uninitialized and resource controls required. |
| DropOnPanic<*const Element>::drop(&mut self) | Real body exported; generated structural lemmas do not prove it. Takes inner:*mut *const Element; needs initialized pointer CELL, no Element resources. Prove actual body and thread/storage/frame/no unwind under actual guard ownership/invariant; generic Drop is not enabled. | hint.rs851–855 exact body and local guard fields. Typed pointer specialization of the local destructor must be certified separately; no unchecked arbitrary Drop summary. Guard resource packaging and forget retention must be reconciled with existing borrow rules before implementation. |
| (*mut *const Element)::drop_in_place(), guard and normal path | Method absent; stock generic free ptr::drop_in_place requires initialized CELL + pointer own and returns cell but permits unwind. For this pointer payload target exact cell/content retention, no pointee permission, no unwind. | mut_ptr.rs1514 exact one-call body checked; ptr/mod.rs817 is compiler lang drop glue, recursive text is not actual runtime body. Narrow compiler pointer drop-glue rule needs explicit trust/typed semantic justification (raw pointer has no destructor); no general Drop/copy rule. |
| mem::forget<DropOnPanic<*const Element>> | Stock SAFE contract consumes guard own, returns token, nounwind. Must not lose caller's selected wrapper cell or run Drop. Ordinary ManuallyDrop identity already trusted; requires review of actual guard resource protocol. | mem/mod.rs162 body let _=ManuallyDrop::new(t); verify source-linked pointer-guard body rather than assuming a newly stronger summary. Any extra spec/translation is exact guard only. |
| unsafe MaybeUninit<*const Element>::assume_init() -> *const Element | No corresponding stock contract. Require inner=some(p) and available initialized storage/read resource; exact same modeled p, token/frame/no unwind. Unknown/none insufficient at extraction obligation. | maybe_uninit.rs703 exact assert_inhabited then raw-address value-field cast/read. Source-linked union-field pointer lowering for this exact body only, full MIR; no generic union access. |
| assume_init nested assert_inhabited<*const Element>, cast/read | Existing pointer cast and read support, no new Element rights; initialized wrapper payload must supply read cell. `assert_inhabited` is compiler rule, raw pointer type inhabited; typed nounwind rule if missing, explicit trust. | intrinsics/mod.rs assert_inhabited and actual raw-pointer read/cast bodies pinned separately. Preserve rawptr read as a checked operation; no silently replaced opaque inner extraction. |

No runtime signature/source changes. Free proof adapters instantiate actual generic
body and may remove const restrictions for the pinned compiler; source equivalence
and exported path-string DefId limitation remain explicit. Integration keeps actual
helper body and operations, not a rewritten pointer-only selection shortcut.

## Existing storage and borrowing assessment

Frozen `std/lib.rsspec:462–478` open/close_MaybeUninit maps an owned OUTER wrapper
cell to optional INNER cell at cast storage address. `none` remains uninitialized,
`some(p)` initialized; these stock projection lemmas are declared trusted support,
not newly proved representation semantics. `raw_ptr_own` is defined true, so no
resource for Element arises. Existing `pointer_cast` preserves provenance/address,
only metadata changes according to existing sized-type rules; no usize equality.

`&mut T`.own is full_borrow(k,T.full_borrow_content(t,l)). Stock reference creation
from local cells uses create_ref_mut, yielding the SAME contents at a reference
pointer plus ref_mut_end_token; end_ref_mut restores original-location storage.
Its model changes reference provenance and does not assert pointer equality with
original raw address. A raw pointer escaping such a borrow must remain tied to the
actual reference pointer/resource; never assume end_ref_mut transports permission
to an arbitrary equal-address raw pointer. This is an integration risk to test.
Shared `ref_init_perm` is a different protocol, not a way to conjure raw storage.

Candidate narrow DEFINED full_borrow_content for exact wrapper pointer type:

```
MaybeUninit_pointer_full_borrow_content<Element>(t,l) =
    *l |-> ?v &*& MaybeUninit_pointer_own<Element>()(t,v)
```

This packages existing outer storage and accepted value-own, not ownership creation.
Open/close wrappers have ordinary checked bodies. Proposed type-wide fbc dispatch
is exact `MaybeUninit<*const Element>` inside certified unit; other applications
retain opaque behavior. Existing generic full-borrow opening/closing and stock
MaybeUninit projection can then expose optional pointer CELL storage. No new
ref_init_perm, alias/provenance axiom or mutation of prelude/kernel permitted.
This definition is reviewed here but NOT IMPLEMENTED at S1; first test existing
SAFE body/ref contracts. Later implementation must preserve ordinary closure and
all resources on actual temporary borrow/move/return path. If that cannot be derived
with existing rules, keep minimal causal reproducer; do not assume the bridge.

Guard invariant is still a design question to resolve before its semantic edit:
putting selected storage in guard own enables Drop but stock forget consumes it;
leaking this permission would not meet helper frame/recovery posts. Existing borrow
protocol or checked specialized forget must reconcile both. No guard storage
ownership assumption is authorized simply by a green value fixture.

## S1 — existing-model as_mut_ptr diagnostic and compact evidence

No semantic/tool change: unchanged accepted325af428 patch and all frozen pins.
Hypothesis: exact source-specialized SAFE two-cast body can prove full result
pointer equality and preserve a caller's opaque mutable full_borrow with existing
cast/reference rules. This tests more than name resolution but deliberately NOT
component acceptance or actual helper integration. No constructor rerun solely
for evidence repack; O4 raw acceptance/mutation logs are repackaged and audited.

Adapter<'a,Element> input &'a mut MaybeUninit<*const Element>; pre thread token,
fractional lifetime_token('a) and existing full_borrow; same resources in post plus
complete result pointer equality; on_unwind_ens false. Separate UNSAFE frame caller
requires fractional u8 cell, preserves it. No initialized assumption or Element
pointee permission. No none/some setup calls added to this first cast diagnostic;
concrete option controls follow a proposed storage extension, if needed.

Hosted export/decode/refinement/source-integrity logs and complete MIR retained;
check SAFE prototype, named body/frame return/leak. A green result is only
DIAGNOSTIC_BODY_AND_FRAME_PASS. Frontend/syntax/unsupported/resource/cast failures
remain INCONCLUSIVE and guide within-phase fixes; no negative acceptance claimed.
Next: prove full typed admission/negative matrix for as_mut_ptr; use its first
resource obligation to test defined storage candidate, then continue dependency
integration autonomously. Kernel/general alias/provenance necessity alone stops.
Nearest hosted run packages compact current+O4 evidence with exact source-artifact
manifest<=25MiB, preserving old full artifact. Separate packaging controls hosted.
Budget5400new seconds,job<=1800/proof<=300,one active run; initialspend0.

## S2 — match the actual elided mutable receiver protocol

S1/37607108528/sourcef19f077/profile325af428: export/decode/refinement/integrity
PASS, then SAFE prototype leaks returned full_borrow before body. This is a
contract/adaptation mismatch, not semantic impossibility. gen_contract treats
elided &'_ mut (when result carries no lifetime) as IN/OUT: pre/post wrapper
points-to + value own. Explicit named 'a instead consumes reference ownership
without returning that full_borrow in the generated post. Returning it explicitly
therefore fails the prototype leak check. No template or resource check disabled.

S2 keeps SAFE helper and original elided receiver shape. Pre/post explicitly
transport *storage|->value plus ORIGINAL opaque MaybeUninit value own in unchanged
profile/certificate-disabled diagnostic; no opaque chunk is created. Result equals
full modeled storage pointer, token and no unwind. Unsafe callers preserve their
fractional frame, with unknown/none/some inner premises and unchanged inner posts.
Five diagnostics after checked helper: wrong result/false post, false assertion,
duplicate frame post and omitted wrapper cell (leak). Each must reach its named
predicate/location; wrong-stage failure remains INCONCLUSIVE. Complete MIR stored;
no external method summary/full applicability/actual integration acceptance yet.
Success advances to exact-type source/MIR admission and active-profile resource
protocol integration, not whole-helper acceptance. Tool pins/semantics unchanged.

## S3 proposed trust delta — source-linked SAFE as_mut_ptr admission

Before implementation of its semantic rule: a NEW separate patch includes the
unchanged accepted constructor definition and exact constructor gate, then adds
only a fail-closed source/MIR certificate for the ordinary SAFE as_mut_ptr body
and redirects the exact external pointer-specialized method to that checked body.
No fbc/storage/borrow/provenance rule is changed at this step. The actual elided
IN/OUT contract preserves the existing wrapper points-to chunk and type-wide
accepted defined pointer-value own. Its pre does not restrict inner(v), and post
keeps the SAME v; no initialized reading or Element permissions are introduced.

Prototype/body proof uses explicit MaybeUninit_pointer_own in pre/post when the
certified unit activates existing pointer ownership dispatch, rather than the
S2 inactive/opaque diagnostic interface. Positive callers unknown/none/some and
fractional independent frame; controls wrong pointer/false post/assert false,
duplicated frame, lost wrapper-cell leak and invented initialized inner must each
reach its own obligation after helper body. Named ownership lemma remains checked.

Gate must bind exact pinned maybe_uninit.rs source/hash/signature/two-cast body
with sole receiver/type substitution. Verify SAFE item path/kind/module/generics,
input &mut MaybeUninit<*const Element> (elided method lifetime), result *mut
*const Element, complete typed locals, operands and both cast target types,
no read/write/projection/extra call, exact normal Return graph/no cleanup/unwind,
source/HIR/parameter/contract/body coordinates and forbidden extra structures.
Unknown/changed forms reject BEFORE activation/redirect. For actual helper units,
constructor and as_mut_ptr bodies must BOTH have same-profile checked evidence;
keep exact two external new and two as_mut_ptr typed redirects, independent of
intrinsics. Original exporter path-string limitation remains documented.

Admission negatives directly mutate source and serialized MIR operand, result,
cast/parameter/return type, identity/binding/contract and extra operation. Mutation
records, canonical/mutated binaries/text and exact recomputed diff retained;
invalid certificate exit2 distinguished from proof exit1. New rule active in
its positive/negative units; no unrelated helper blocks baseline controls.
Full O4 constructor matrix + stock/experimental Rust/C/C++ regressions is a required
gate of this changed profile; no SWO/layout dependency exists. Classifier selfchecks
must reject wrong stage/predicate/location/integrity/certification. Complete
as_mut_ptr criterion required before claiming its acceptance/using stronger
summary; source body diagnostics alone remain partial. After acceptance continue
actual helper and its listed intrinsics/drop/forget/assume_init dependencies.
Kernel/prelude/general memory/alias/provenance/exporter/schema/refiner frozen.

## S5 prospective intrinsic rule — review BEFORE semantic implementation

Separate new profile `experimental-source-linked-select-pointer-intrinsics-v1`,
separate patch `verifast-select-pointer-intrinsics.patch`, preserving S3 patch and
O4 original identities. Kernel/prelude/general memory/alias/provenance unchanged.
The only NEW trusted value rule is compiler `std::intrinsics::select_unpredictable`
for exactly `*mut *const Element` or `std::mem::MaybeUninit<*const Element>`:
`result = if condition { a } else { b }` as COMPLETE modeled values, no unwind,
no destruction of the other value. This is NOT a verified Rust-body theorem.
Pinned repository `intrinsics/mod.rs` SHA256
ab781181f967398d514d9fd2b5f3b6aebd16c2c403f3d1a2628e0c7f1fac6ebf,
lines486–500 declares rustc_intrinsic/rustc_nounwind and specifies the exact
fallback `if b { forget(false_val); true_val } else { forget(true_val); false_val }`.
The fixed compiler/exporter identity and exact pointer types delimit this trust.
No address casts/comparisons, Element resources/Copy/Freeze, generic T rule.

Translator returns ordinary `Ast.IfExpr(condition,a,b)` through FnCallResult only
AFTER full applicability certification. Pointer values retain raw_ptr_own=true.
For the wrapper, an ordinary CHECKED ownership-transfer lemma consumes both
DEFINED pointer-own predicates and returns only that of the selected wrapper:
open the definitions/raw-pointer-own cases, close selected own in condition cases.
No opaque result resource or new axiom; the unselected value ownership is empty
and can be discharged against its existing definition. Defined empty ownership
is logically duplicable; resource-loss/duplication negatives must therefore target
actual independent cell/thread resources, not demand failure for two empty owns.
Unknown/none/some selection retains the exact option, not an initialization premise.

Applicability: exact FnDef/path/substitution/type-kind, Bool/T/T operand types and
order, plain Move/Copy source local identities, result T, normal successors and
unreachable unwind, no late-bound/ghost/runtime extras. In actual helper verify
ALL three calls and preceding assignments tying condition to the parameter and
values to true_ptr/false_ptr or wrappers (two calls reverse operand pairs), with
complete admissible typed graph/source-bound body. Counts alone are insufficient.
Standalone SAFE fixtures need their own full typed MIR/dataflow/CFG certificates;
unknown/changed source/function/type/operand/result/extra op/CFG rejects before
proof. Preserve two constructor and two as_mut_ptr gates/checked bodies and source
integrity/export/decode/refinement. Runtime std source/signatures remain unchanged.

Acceptance: symbolic and fixed true/false full-value positives for both exact
T types, wrapper none/some and unknown states, SAFE prototype/body/return/leak,
thread plus independent fractional frame/no unwind. Wrong selected value/inner,
false post/assertion, lost/duplicated frame each must fail named proof obligation.
Source and direct MIR admission negatives must reach exact separate certificate
failure, before proof; classifier wrong-stage/predicate/location/source/identity
mutants fail closed. Full O4 constructor plus S3 asptr regression and Rust/C/C++
baselines required in changed profile. Integration runs ONLY after component
acceptance and keeps original all3intrinsics/guards/drop/forget/assume_init.
First remaining mapped operation is investigated, never a name-only stop.

### Later guard/forget hypothesis, NOT IMPLEMENTED or accepted

Stock local private-field DropOnPanic<T>.own defaults to false; its SAFE Drop
prototype is vacuous, not a source of pointer-cell permission. One potentially
sound pointer-only route leaves the selected cell and reborrow token OUTSIDE the
guard value and verifies the exact Drop body under an explicit initialized-slot
precondition. Its generated SAFE compatibility/vacuity must be disclosed and
checked; a non-vacuous body proof is separately required. Actual cleanup becomes
unreachable only after BOTH exact pointer drop and assume_init are proved nounwind.
Exact source-specialized forget<that SAME local guard nominal type> body merely
wraps its argument in ManuallyDrop under existing identity translation; a token-only
body proof may then avoid changing false guard-own, while framing both child cells.
This is NOT general forget/Drop/ownership support. It requires hosted confirmation,
full nominal/MIR/source binding and leak/SAFE compatibility controls before use.
If it cannot satisfy these criteria, investigate existing borrow packaging before
claiming that an uncheckable resource bridge is necessary. No such bridge is assumed.

S4b applicability correction BEFORE implementation: standalone asptr body/model
has complete acceptance at37611745252/source7c14ab6/profilee9b4d025, but actual
external redirect rejects its valid elided-lifetime shape before body execution.
Raw exported asptr FnDef has SOLE type *const Element and
lateBoundGenericParamCount=1; stock translate_fn_call_rexpr then appends the
synthetic erased lifetime before the redirect match. Thus effective substitutions
are EXACT [Type(*const Element),Lifetime("'erased")], not just [Type]. The new S5
cumulative profile may correct this match while retaining immutable S3 evidence:
require raw sole pointer type AND raw lateBoundCount=1 AND this exact effective
pair; reject every other lifetime/count/type/arity. Local checked helper CallExpr
keeps its sole Element type arg: receiver lifetime is elided/generated, no explicit
Rust helper type param is added. No new borrow/provenance/ownership rule. Same-profile
asptr full acceptance and actual two-call binding are required regressions. Actual
must also retain typed receiver/result and one normal call/unwind continuation.
This is a certified frontend applicability correction, not a new SAFE contract.

S5a/37613525435 refinement of applicability BEFORE next implementation:
exact raw/effective latebound matches and two actual redirects now pass, but VF
reports Incorrect number of type arguments at firstasptrcall38. The previous
"sole Element CallExpr" choice is disproved. Rust signature still has sole TYPE
parameter and an ELIDED receiver lifetime; VF exports that lifetime as a second
ghost type parameter. Stock translate_regular_fn_call represents each
GenArgLifetime by Ast.InferredTypeExpr(call_loc), so the exact redirect must use
[Element,InferredTypeExpr], retaining raw-latebound1/effective'erased restrictions.
This adopts existing lifetime inference, no new lifetime/provenance/borrow axiom
or Rust signature change. Same fullbody/SAFE/state/resource matrix and actual
receiver/result/CFG gates remain required. If lifetime inference cannot match the
existing elided IN/OUT contract, preserve the exact proof obligation instead of
assuming its resource effect. Canonical S5a standalone intrinsic MIR is also now
available; replace the disproved4locals/no-statements guess with its full observed
7locals/ordered copy temporaries and normal/unreachable CFG, never count-only.

## S6 prospective pointer drop-glue and checked method (before implementation)

Exact target: `std::ptr::mut_ptr::<impl *mut T>::drop_in_place`,
`T = *const Element`, receiver `*mut *const Element`, result unit. The local
source-linked unsafe adapter instantiates the method at `mut_ptr.rs:1514–1519`:
`unsafe { drop_in_place(self) }`, with only receiver rename and explicit standard
callee binding. Pin the entire method source file and body, not just its name.
The free `ptr::drop_in_place` at `ptr/mod.rs:813–825` is compiler lang drop glue;
its recursive placeholder is explicitly not a runtime-body proof target.

Stock free drop contract permits unwind and returns an unspecified cell value.
These posts cannot establish exact preservation or no unwind. The prospective
NEW trusted compiler rule therefore applies ONLY to free drop glue for raw
pointer payload `*const Element`: a raw pointer has no destructor, so its drop
is a no-op, preserves the complete modeled pointer stored in the cell, and
cannot unwind. It gives no permissions for `Element`. This is a compiler rule,
not a proved Rust-body theorem. The method adapter itself must be checked.

Do not lower this call to an unchecked empty statement. Insert an ordinary
CHECKED ghost identity lemma requiring `thread_token(t)`, `t == currentThread`
and initialized `*slot |-> value`, and returning the SAME resources/value.
No permission is minted: this precondition is consumed at the call, and the
lemma body merely preserves it. Pointer-value ownership is already defined
empty and can be introduced/closed with its existing definition. Optional
uninitialized/unknown cell contents must fail the initialized-cell precondition;
a wrapper value alone is insufficient. Local storage validity/alignment follows
from the existing typed points-to resource, never from the pointee `Element`.
Kernel/prelude/general memory/aliasing/provenance remain unchanged.

Applicability must certify pinned method/lang-item sources, exact unsafe item,
sole Element parameter and unrestricted Sized predicate, input/output, local
identities/types, parameter-to-call Move flow, free lang-item FnDef exact
substitution, destination unit, complete normal/unwind graph and absence of
additional operations. Only after this certificate redirect the exact external
method to its checked body. Actual helper must retain its original method call
and cleanup edge; a proved nounwind contract makes that edge infeasible, rather
than deleting it. The generic local guard Drop call with T remains outside this
rule until a separately source-linked pointer instantiation is certified.

Required matrix: initialized arbitrary pointer cell and independent fractional
frame, full value/cell/thread/no-unwind body post; wrong preserved value, false
post/assert false, lost cell leak and duplicated independent frame; insufficient
initialization (none and unknown optional contents) at the call precondition.
Source/MIR operand, output, type, nominal binding, CFG/unwind and extra-operation
mutations must fail admission before proof. Classifier mutations require actual
body/target obligation/location/full certificate/source/refinement. Changed
profile reruns accepted constructor/as_mut_ptr/intrinsic components plus
stock/experimental Rust/C/C++ baseline gates; no SWO/layout dependency. Unknown
forms reject, no general pointer Drop or union theorem. Integration first proves
wrapper-to-cell projection using stock open/close and existing reborrow tokens;
if that fails it is a separate obligation, not permission to remove the drop pre.

S5e profile identity BEFORE use: `experimental-source-linked-select-pointer-intrinsics-v2`
adds only the complete actual helper applicability whitelist to the earlier v1
compiler selection rule. Cumulative patch SHA256
`1c9637f5269d464685ca0fe4e5600571a7618658e4da804e073629fc1ece661f`.
Standalone bodies/semantics remain identical; v1/2cd1a04a evidence remains separate.
Actual whitelist checks source/header/contract/HIR spans, local guard nominal
field/type/span, all31 typed locals, all14 blocks/ordered statements, ten exact
callee identities/substitutions/operand/destination/CFG paths, cleanup Drop and
flag switch. It certifies the graph before modeling exactly2 pointer and1 wrapper
intrinsics; it does not model Drop/forget/assume_init or accept the whole helper.
Changed v2 must rerun all component matrices/baselines/classifiers before actual
intrinsic-on diagnostic. Future authorized drop profile uses its separate identity
`experimental-source-linked-select-pointer-drop-v1`, never relabels v1 evidence.

Latest priority correction: freeze all further semantic patches. Activeprofile
remains experimental-source-linked-select-pointer-intrinsics-v2/7bb39a84; separate
04d67f4b assume diagnostic draft is NOT RUN and not in workflow patch chain.
Sameprofile savedS5j replay reclassifies exact admission reasons only, retaining
original evidence/classifications/profile hashes. No proof transfer across profiles.
Independent diagnostics write own exit/status/source/refinement records and never
gate intrinsic acceptance; critical matrix and actual prerequisites remain fail-closed.
S5k actual source-linked full typed graph/refinement passes, first blocker
pointer drop_in_place57. Final helper proof still missing. Refiner RawPtr failure
in assume S5k and aftertail annotation failure S5j do not test storage permissions.
Details and compact evidence/SHA/run links in SORT4-SELECT-POINTER-RESULTS.md.

S5r2 replay acceptance is classification of the saved S5j proof run at identical
semantic7bb/v2 identity, not a new proof theorem. Exactly8 reasons corrected;
all32 other admissions and16 proofs byte-equivalent classifications, profile/stage/
message mutants reject, original logs/source/MIR/classifications retained. See
results for fullSHAs/run37626031885/compact11483952705 and S5k actualdrop blocker.

## S6 authorization and trust review — 2026-10-07, BEFORE implementation

Owner resumes ONLY pointer drop from bea6248; the broader 04d67f4b draft remains
frozen. Same phase budget: 2398/5400 consumed, 3002 job seconds remain.
Exact payload is `*const Element`, not Element; receiver `*mut *const Element`.
Element is arbitrary Sized with no Copy/Freeze or pointee rights. Method source
mut_ptr.rs SHA256 d35858d6b1ec693d5e01b994e2d8248f73c7062c151e75e73ea635456fc82098;
lang-item source ptr/mod.rs SHA256
325d69d3ce0fef9099f985febc5b712bbdb3563364648adc1396a365699987aa.

The checked theorem is the non-const, exact-type method adapter, solely renaming
self to slot and qualifying the scope-bound free call. The compiler lang-item's
recursive placeholder is NOT the executable body and is NOT proved. A separate
trusted rule maps that exact free drop-glue call to a checked identity lemma.
Rust's destructor semantics makes raw-pointer payload drop empty: pointers own
no referent, have no user destructor or fields to recursively drop. Hence there
is no read/write, pointer reconstruction or callback that could change the full
stored modeled value/provenance or unwind. This rationale is an explicit compiler
correspondence assumption, not a result established by proving the ghost lemma.
[Reference destructor operations](https://doc.rust-lang.org/reference/destructors.html)
and [Drop documentation](https://doc.rust-lang.org/stable/core/ops/trait.Drop.html)
support that rationale; the pinned compiler/exporter remain trusted.

Rule pre: thread_token(t), t == currentThread, initialized typed *slot |-> value.
Rule post: SAME thread_token and SAME complete *slot |-> value, unwind false.
Independent caller resources frame through ordinary separation; none are minted,
consumed or duplicated. Cell validity/alignment comes from that existing typed
resource. No rights on Element, numeric-address coercion, ownership bridge or
extension of general Drop/guard/forget/assume_init/union/refiner/kernel is allowed.
Checked identity lemma preserves the resources; its proof does not prove the
Rust-to-lemma correspondence. Full method typed MIR/source certificate must pass
BEFORE free-call model activation or external method redirection: exact item,
input/result/local types, callee substitution, operand dataflow, destination,
all normal/unwind blocks/ordered operations. Unknown shapes fail closed.

S6 gate: full independent positive/proof-negative/source-MIR matrix, exact-stage
and location classifiers, all accepted ctor/asptr/intrinsic and Rust/C/C++
regressions in new drop-v1 profile. Collect every case even when a classification
fails. Preserve original classifications; reason-only fixes use hosted replay.
After semantic changes require new proofs. Actual integration runs only after
acceptance, retaining runtime calls and cleanup CFG. Derive the initialized-cell
pre from actual current wrapper/storage/reborrow resources using existing lemmas;
if impossible STOP at that precise obligation. If drop passes STOP at next blocker.
Whole helper/sort4 claims remain forbidden.


S6 actual projection hypothesis (review before integration annotations): stock
asptr returns the exact receiver address and its existing wrapper points-to;
stock create_ref_mut leaves ref_mut_end_token and that cell alive (StorageDead
is ignored by existing translation). Use the asptr result cast back to the typed
wrapper pointer, apply unchanged open_MaybeUninit once for each wrapper, and
constructor inner==some(input) to obtain the two initialized payload cells.
Pointer select binds drop to one of those addresses; split condition ghost-only
if needed, consume/preserve selected cell at drop and frame the other. Close
wrapper projections after successful drop using stock close_MaybeUninit before
recording the next runtime blocker. No Element cell, union field pointer, new
borrow rule or assumed ownership bridge. This is a falsifiable proof hypothesis,
not accepted evidence. Certificate admits only the exact declared ghost sequence
with source/MIR spans; full runtime body/typed MIR/cleanup edges stay identical.
If existing projection/equality/reborrow obligations fail, preserve exact trace
and STOP at that obligation rather than weakening initialized-drop pre.

## S6v2 admission correction — BEFORE implementation, 2026-10-07

The owner authorized only this pointer drop component and its actual integration.
S6v1 is COMPONENT_ACCEPTED in37642650884/source4d0e307, samecd660fe9 profile:
2positive+11intended proof negatives+22admission controls, with original proof and
regression provenance retained. Actual baseline enters and reaches checked drop;
`verified/lib.rs(110,55-58): No matching heap chunks: points_to<*Element>(__result2, _)`,
callsite57,14–29. This is its initialized-cell requirement, not a method-resolution
failure. Projected actual export/decode/refinement0 but fails source admission
before proof: `actual projection ghost source span`. No projection resource result.
Job113s15:17:47–15:19:40UTC, cumulative2995/5400,2405remain; one relevant hosted run.

Falsifiable admission hypothesis: the pinned exporter encodes ordinary span hi
of //@ ghost annotations at the LAST character, while annotation-specific
startLine/startCol,endLine/endCol describe the FULL half-open parser range. Five
raw MIR observations agree: first ghost line40 regular translated5..93, explicit
start5/end94; others41/59/61/62 likewise differ by one. translate_annotation uses
explicit fields; translate_span_data adds1 to regular0-based columns. Current
certificate compares regular hi to half-open end, hence rejects the exact source.
Independent read-only reviewer confirmed all five observations and existing APIs.

Allowed correction ONLY inside this exact5ghost source certificate: require
ordinary regular lo=position(at), hi=position(at+rawLength-1), AND separately
explicit start=position(at), end=position(at+rawLength). Require exact raw strings,
order, source body/contract, all typed locals/callees/operands and normal/unwind
CFG. No OR fallback, approximate coordinates, new ghost statement or runtime
rewrite. Contract annotation span convention remains unchanged. This is a
TRUSTED ADMISSION semantics change, not merely a classifier fix; write rationale
and enforce fresh regression gates before it is used. Compiler drop-glue mapping,
lemma/method initialized pre/full-value-thread-frame/nounwind posts are unchanged.
No general annotation parser, Rust compiler/exporter/schema/refiner/kernel/prelude/
memory/aliasing/provenance/guard/forget/assume_init change. This is within the
owner's narrow S6 authorization, not a reopened broader frozen phase.

New profile `experimental-source-linked-select-pointer-drop-v2`, cumulative patch
from frozen cd660fe9 plus ONLY that certificate correction. Before actual use:
NEW complete independently collected2+11proof/22admission drop matrix, accepted
constructor/asptr/intrinsic matrices and14stock/experimental Rust/C/C++ baselines;
no proof reuse across changed semantic profile. Then two separate actual MIR
coordinate negatives: regular ghost hi changed+1 (ordinary source span predicate),
explicit ghost endCol changed-1 (explicit full parser range predicate). Both must
export/decode/refine with integrity and exact mutation record, reject precisely
at their named certificate obligation BEFORE actual proof; setup/other errors
are not intended negatives. Collect independently and retain every original
classification, source/MIR and full logs. Exact canonical projected source is the
positive applicability case; no extra standalone body abstraction is introduced.

Target domain still arbitrary thin *const Element payload/*mut *const Element
receiver, no Copy/Freeze/Element permissions. Full actual target normal selected
pointer/thread/frame and unwind false are unchanged. Test stock open/close
projection using the existing wrapper cells/some states/receiver equalities and
reborrow resources. If projection/drop pre cannot be established, record exact
obligation/resources and STOP. If drop passes, record next blocker and STOP.
Any non-admission semantic extension requires a separate owner decision.
Budget2995/5400used,2405remain; <=1800/job,<=300/proof,hosted-only,one active run.

S6v2 implementation pin before dispatch: cumulative patch SHA256
8e62e6c3044fda7533637d242fb5e8a575eac0d7600213e8e3ba00a182dc0d7c.
Independent static review sees only8narrow ghostcoordinate-certificate lines and
patch offset metadata relative tocd660fe9; std spec/body/glue unchanged. Two new
MIRmutants distinct predicates, fullnewmatrices beforeactual. Projected proof
requires bothcontrols plus baseline source/MIR/intrinsic/drop infrastructure;
expected baseline initializedcell proof failure is allowed, setup failure is not.

## S6v2 reassessment and normal MIR diagnostic — BEFORE implementation

Fresh37645561507/source85ec171: fullctor/asptr/intrinsic/S6/14baseline matrices
PASS at8e62/drop-v2;173s,cumulative3168/5400,2232remain. Both actualcoordinate
controls are SETUPfailures, not intended negatives; projectedactual NOTRUN.
Their first readonlyexporter invocation mutates successfully, while second normal
invocation fails the readonly-high guard. Existing source hashes and exporter
bytes match; no nondeterministic claim follows. Source+trace reassessment: frozen
preprocessor injects32byte `crate::VeriFast_ghost_command();` before in-function
//@ only in NORMALmode. GhostRange.span uses shiftedbyte positions; explicit
start/end line/col stay original. All5normal trace highs are readonlyhigh+32.
The previous S6v2 design checked readonly geometry as if it were normal. Preserve
that failed hypothesis/evidence; do not declare admissioncontrols accepted.

Next diagnostic ONLY, sameauthorizedS6/compiler/exporter/schema, semanticpatch
unchanged8e62: hosted stockexporter normalmode fullMIR capture of exact accepted
projectedfixture from37645561507 pinnedcompactSHA b160edcd347c02ffafcd94ac0258e805d488bed10a500b64cd3e632b5d8d49ae.
Validate manifest/source/run and original/verified hashes37e5/8a82, stockarchive/
exporter2b8ebb/schema7f3eb/base809/compilernightly2026-02-05 pins and sourceintegrity.
No proof verifier/consolebuild/refiner invoked: exporter/decode success is a
DIAGNOSTIC, not component/helper acceptance. Preserve complete normaltypedlocals,
blocks/callees/normal-unwind CFG and5ordinary+explicit ghostcoordinates. It tests
applicabilitygeometry, not the full normal/unwind target proof or cell projection.
If data supports an exact narrowS6source+stockinjection correspondence, review it
withnewprofile/fullregression gates BEFORE further semantics. If broader parser/
frontend/refiner/kernel/memory changes are needed, stop atthattrustboundary.
Budget3168/5400used,2232remain,onehostedrun,<=1800/job,<=300/proof,sameworkflow30.

## S6v3 exact normal scaffold admission — BEFORE implementation

Normal diagnostic37649244205/sourcef6fdf5ba4c3a1bee44bdb3566ab354d1e558fe6d
export/decode/integrity/effectiveargsPASS (not proof), compact11495097694 innerSHA
`ead2a0c8a501becdbf0bbcf6c521d356a3457fb232f5e5a4b09793a618e2c093`.
Independent worker/reviewer reads identify exact stock scaffold, not count-only:
36locals19BB. Runtime-local map R0–11=N0–11, R12–21=N+2, R22–23=N+3,
R24–30=N+5; five new unitlocals N12,N13,N24,N27,N28.
Runtime-BB map R0–3=Nsame,R4=N6,R5=N7,R6=N9,R7=N12,R8=N13,R9=N14,
R10=N15,R11–13=N16–18. Synthetic BB4/5/8/10/11 call exactly
VeriFast_ghost_command with zero type/value args, unitdest12/13/24/27/28,
normal5/6/9/11/12 and unwindContinue/Continue/Cleanup18/Cleanup18/Cleanup18.
Actualdrop N9 retains Move26,unitdest25,normal10,cleanup18. All original runtime
calls/return/dropflag/cleanup branches remain and must be checked, not assumed.

Falsifiable hypothesis: exact full NORMAL projected graph can be admitted by a
projected-only source/typed-MIR certificate without changing execution translation
or resource semantics. New profile experimental-source-linked-select-pointer-drop-v3
extends8e62 ONLY this certificate. Preserve baseline31/14 cert unchanged; check
full36/19 localtypes/mutability/HIR/debug, every ordered statement/terminator,
callee/substitutions/operands/results/normal/unwind, five call-span↔raw-ghost pairs
on unique source lines40/41/59/61/62, and no extra operations. Ghost regular spans
use EXACT frozen normal tag length32 (including shifted inclusivehi); explicit
parser coordinates remain original half-open. No permissive OR, generic graph
normalization, AST/MIR rewriting or changed runtime source. Redirect only after
complete matching. The stock exporter's source/bytes/tag and source stripping
remain pinned; no new exporter/parser/refiner/kernel/prelude rule.

Trust boundary separate from compiler raw-pointer glue: pinned stock translator
already substitutes each placeholder by its line-matched ghost statement, ignores
its synthetic unwind target, and treats StorageLive/Dead as empty. This existing
frontend correspondence is trusted, not proved by a ghost resource lemma. Exact
source/scaffold admission constrains its applicability; it is no general license
for ghost rewrites or new Rust compiler semantics. Actual runtime cleanup stays.

Domain/full target unchanged: arbitrary thin *const Element values, receiver
*mut *const Element, thread+independent frames, selected full modeled value,
normal resource contract and on_unwind_ens false. Existing initialized-cell drop
contract/body/glue lemma unchanged. No Element/Copy/Freeze/purity restriction,
ownership bridge or new memory/alias/provenance resources. Try ONLY stock
open/close_MaybeUninit on existing wrappers with inner=some(input), exact returned
receiver pointers and reborrow resources; if drop pre fails STOP there, otherwise
STOP at next actual substantive blocker. GeneralDrop/guard/forget/assume_init/
union/refinement and04d67f4b stay frozen.

Acceptance gate BEFORE actual proof: fresh full S6 independent2positive,
11proofnegative,22source/MIR/pin admissions; complete accepted constructor/asptr/
intrinsic matrices and14stock/experimental baselines at NEW profile, no reuse of
old semantic-profile proofs. Independently collect actual NORMAL admission mutants:
regularhi/explicitend, ghost callee/args/substitution/unit type/destination/normal
and unwind targets/call span/missing or extra scaffold, runtime drop operand/
callee/cleanup and final return/cleanup. Each must preserve pinned source/export/
decode/readonly-refinement integrity and have exact changed NORMAL MIR evidence;
reject only at its named certificate predicate BEFORE proof. Readonly export has
no placeholders: preserve it byte-for-byte for those mutants, separately record
normal invocation rather than overwrite readonly evidence. Setup/unrelated
failure stays INCONCLUSIVE; all independent results retained. Canonical projected
proof only after full gates and original actual infrastructure checks pass.

Outcome map: gate failure -> inspect/reassess no acceptance; full gates + projected
cellpre failure -> record exact existing/required resource and STOP; drop passes ->
record next obligation and STOP. Broader frontend/resource semantics needed ->
STOP trust boundary, no implementation. Budget3302/5400used,2098remain (entry2398
never reset), <=1800/job,<=300/proof,one relevant GitHub-hosted workflow only.

S6v3 implementation pin before dispatch: cumulative patch SHA256
`94ffc64ce15811ac0de62e55489fb1e61242883b7258aa22969bbefa9ec184e8`.
Independent cert+18NORMAL-only mutant review found no static blocker; entire
stdlib-spec patch section is byte-identical to v2. Baseline31/14 unchanged;
exact36/19 projected check only, no AST/MIR rewrite or changed stock execution.
Readonly source/export/decode/refinement bytes pinned separately; normal mutation
files/records preserved independently. Fullfresh component/regression gates and
all18 exact intended certificate failures precede canonical projected proof.
