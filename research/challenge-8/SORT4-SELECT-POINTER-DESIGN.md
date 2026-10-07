# Pointer select completion — dependency map and reviewed design

2026-10-07: read-only mapping IN PROGRESS; no new semantic rule implemented.
[Authorization/phase](SORT4-SELECT-POINTER-PHASE.md),entrycd44e1bb.
Existing accepted constructor O4 profile325af428 remains frozen.
Complete map and initial as_mut_ptr/storage design will be committed BEFORE
semantic edits; packaging work is independent and introduces no proof semantics.

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
