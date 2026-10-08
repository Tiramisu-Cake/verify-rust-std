# Actual `MaybeUninit::new` linkage on 26.10 — review before implementation

O4 proof SHA `86e84ace` captured the unchanged pointer-specialized actual
`select_unpredictable` body from std `cd371e03`. NORMAL/readonly export/decode
and refinement passed. The capture-only fixture has no S6 activation variables
and no checked local constructor. Its full verifier entered the actual function
and stopped at verified line 25, `No such function:
std::mem::MaybeUninit::<T>::new`. Complete typed MIR contains two calls with
exact def path `std::mem::MaybeUninit::<T>::new`, one `*const Element` type
argument each, `Move` from `_5`/`_7`, destination `_4`/`_6`. Both normal and
reachable cleanup graph remain present; this first failure does not settle the
later ownership, guard, forget, intrinsic, or `assume_init` obligations.

The accepted S6 translator already has an actual-body branch that expects
exactly two constructor redirects. It activates only after certification of a
local `sort4_certified_maybeuninit::MaybeUninit` union and
`sort4_checked_maybeuninit_new` body within the same exported compilation, with
`SORT4_MAYBEUNINIT_REPO_ROOT` set to the pinned repository. The local union and
constructor are a source-equivalent copy of `MaybeUninit::new<*const Element>`;
the translator maps their certified type and aggregate to the std model. A
bare environment variable or name match is insufficient because the local
source, full typed MIR, contract, spans, and actual redirect count must pass.

Proposed minimal experiment: append exactly that O3-accepted local constructor
module to both original and verified actual fixtures. Preserve the actual
function signature and entire runtime body byte-for-byte, and keep the original
equal to verified after ghost stripping. Activate only the constructor S6 gate
for this one hosted case. Require source pins for hint/maybe_uninit/manually_drop,
the exact helper body and local module, a complete NORMAL/readonly typed MIR
record, successful exporter/decode/refinement, S6's local constructor source/MIR
certificate, local constructor proof with return/leak check, and exactly two
redirect markers. The expected first remaining error is the next unsupported
actual operation, likely `as_mut_ptr`, and is diagnostic only. No actual helper
postcondition is accepted from reaching a later error.

Negative controls should mutate the *auxiliary* constructor operand or union
field with the original/verified runtime pair still equal after ghost removal.
The existing S6 certificate must reject before local body proof. A separate
actual-call-count mutant may replace one of the two `new` calls only as a
negative fixture; it must fail either the exact actual-source certificate or
the two-redirect gate. The production actual body is never changed. Keep
full logs and original classification for all controls; setup/frontend errors
are inconclusive, not intended negatives.

Trust boundary: exact std source to local-copy constructor and exporter
`def_path_str` applicability remains an explicit source/MIR correspondence,
not DefId equality. `MaybeUninit_pointer_own` is defined in the accepted S6
spec and owns no `Element` cell (`raw_ptr_own<T> = true` in stock). The checked
local lemma/constructor do not provide actual storage ownership or a generic
helper proof. S6 accepted patch, target std runtime, exporter, decoder,
refinement, and verifier safety/leak/unwind switches remain unchanged.

The scope of this component is **constructor linkage only**. After its hosted
result, a distinct reviewed step can add the accepted `as_mut_ptr` adapter and
then typed intrinsic/pointer-drop linkage, with fresh exact actual MIR gates.

## Implemented diagnostic gate

`check-constructor-linkage.py` implements the one-component fixture and two
source mutants. The auxiliary module precedes the actual function so VeriFast
checks its return/leak behavior before the actual body reaches the next missing
operation. The script imports the exact O4 actual-source preparer and the O3
constructor source builder; it has no independent rewrite of their runtime
bodies. It records full NORMAL and readonly MIR, stage/source hashes, the
unpinned-next-error log, and separate classifications. The positive requires
the existing S6 certificate marker, both redirect markers, the exact `2/2`
counter, the checked local constructor body/return/leak, actual function entry,
and a single first unsupported `as_mut_ptr` error. The two negatives require
their exact S6 source-certificate reason before any function proof. These are
falsifiable expectations, not claims already observed. Any other error is
`INCONCLUSIVE` and must guide the next revision.

The script is hosted-only. Python AST parsing and `git diff --check` passed
locally; no exporter, verifier, refiner, Rust compiler or fixture preparer was
run on the server. Hosted invocation on the existing S6 console:

~~~bash
python3 research/challenge-8/overnight-linkage/check-constructor-linkage.py \
  --tool-home "$source_home" \
  --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" \
  --compiler-sysroot "$compiler_sysroot" \
  --evidence "$ev/constructor-linkage" \
  --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))"
~~~

## O6 result and classifier repair

O6 run `37703486878`, proof SHA `40c66d4e`, used the accepted S6 console
unchanged. Its positive case passed NORMAL/readonly export/decode and
refinement, certified the exact local constructor MIR/source, verified its
return and leak checks, redirected both actual `new` calls (`2/2`), and entered
the unchanged actual body. The first remaining error moved to
`No such function: std::mem::MaybeUninit::<T>::as_mut_ptr` at verified line 65.
This is `CONSTRUCTOR_LINKED_DIAGNOSTIC`; the helper is not proved. The
`wrong_active_field` control rejected at its intended source certificate.

O6 originally classified `extra_union_field` `INCONCLUSIVE` despite export,
decode and refinement exit zero, verifier exit two, no proof entry, and a single
fatal certificate error. Its actual first reason was `certified union fields or
types differ`, from the typed ADT field check, while the classifier expected
the later source-text reason `local union fields differ from repository`.
This is a reason-order change, not a weakening: the mutated extra field is
still rejected before proof. The local classifier now pins the **observed exact
earlier reason**. O6's original outcome remains recorded as `INCONCLUSIVE`;
the repaired classifier requires a fresh hosted result before calling its
three-case matrix accepted.

## Next component: actual `as_mut_ptr` linkage — before implementation

The O6 complete actual MIR has two calls with def path
`std::mem::MaybeUninit::<T>::as_mut_ptr`, the sole `*const Element` type
argument and one erased lifetime each. Their moved receiver locals are `_9`
and `_11`, respectively, matching the existing S6 actual-call gate. The calls
retain `unwindAction=continue` and successors 3/4 in the observed NORMAL
graph. The accepted local as_mut_ptr adapter has a source-pinned two-cast body,
full five-local typed-MIR certificate, pointer-cell/defined-value ownership
contract and 17/17 source/MIR admissions in O3. It does not read the
MaybeUninit value or grant `Element` rights.

The next fixture should keep the O6 constructor module, add the exact O3 local
as_mut_ptr adapter **before** the unchanged actual body, and activate the same
`SORT4_MAYBEUNINIT_REPO_ROOT` gate. The S6 translator certifies both local
bodies and demands two constructor and two as_mut_ptr redirects, including the
actual receiver locals `_9`/`_11`; no new translator patch is justified by the
observed graph. Require both adapters' local proof return/leak checks, all four
redirects, NORMAL/readonly export/decode, refinement, source hashes, and the
exact actual body. The expected next missing operation is typed intrinsic
selection, but any different first error is diagnostic. Auxiliary as_mut_ptr
body and source/typed-MIR mutants must reject before proof. The constructor
source controls continue independently. This stage still proves no whole
actual helper postcondition, ownership of DropOnPanic, or SAFE forget.

## Implemented `as_mut_ptr` linkage diagnostic

`check-asptr-linkage.py` composes the unchanged actual body with the O6
constructor and the O3 source-certified local `as_mut_ptr` helper. It imports
the accepted S6 source builder, retains its exact source mutation logic, and
uses the existing S6 translator gates. The positive requires both complete
local MIR/source certificates, local return and leak checks, exactly two
constructor redirects and two as_mut_ptr redirects, and the first remaining
typed-intrinsic error after entry into the actual body. The sole auxiliary
negative mutates the two-cast operand and requires the exact pre-proof S6
source-certificate rejection. Both cases preserve equal original/runtime and
verified/ghost-stripped Rust, full NORMAL/readonly MIR, and refinement.
The result is diagnostic even if its classifier passes: neither the actual
helper nor DropOnPanic/forget resources are proved by this fixture.

Static Python AST parsing and `git diff --check` pass. This script has not
been executed on the server. Hosted invocation after the S6 console build:

~~~bash
python3 research/challenge-8/overnight-linkage/check-asptr-linkage.py \
  --tool-home "$source_home" \
  --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" \
  --compiler-sysroot "$compiler_sysroot" \
  --evidence "$ev/asptr-linkage" \
  --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))"
~~~

## O7 result: constructor and `as_mut_ptr` actual-call linkage

O7 run `37705052264` produced complete source, NORMAL and readonly MIR,
export/decode/refinement and full-verifier logs. The three constructor cases
all met their intended exact classifiers: the positive linked two actual
`new` calls, proved the local constructor return/leak and stopped at the
first missing `as_mut_ptr`; both auxiliary source mutants rejected before
proof. This is the fresh hosted validation of O6's narrow classifier repair.

The `asptr-linkage/positive` case passed all five exporter/decode/refinement
stages with unchanged source hashes. Its actual-body hash was
`0d4233fe67c243c9d46201603fb143182ba2f5caa35f5d63907a3d5c50ed9613`,
the same as the constructor controls. The full verifier certified both local
complete typed MIR graphs and checked both local bodies through return and
leak; translation logged exactly two actual constructor redirects and two
`as_mut_ptr` redirects (`2/2` each). It entered the actual body and stopped
at the next unsupported `std::intrinsics::select_unpredictable` call, line
92 in this fixture. The auxiliary `source_operand` case passed
export/decode/refinement, then rejected the exact mutated two-cast body
before any function proof. Both classes match the intended checks and no
false negative was counted. The `asptr-linkage/summary.json` classification
is `CONSTRUCTOR_ASPTR_LINKAGE_ACCEPTED`, with `actual_helper_proved=false`.

The complete positive NORMAL and readonly graphs retain the three intrinsic
calls, the actual pointer-drop call in block 6 with unwind to common cleanup
13, and the same cleanup-13 predecessors from forget and assume_init. Blocks
11/12/13 remain cleanup blocks, with block 13 switching to resume 11 or
guard Drop block 12. The diagnostic proves linkage and local callees only;
actual ownership, normal helper postcondition and unwind remain open.

O7 also reran the full S6 matrix on the new combined experimental console.
Its eight stages (`stock_controls`, constructor, asptr, intrinsic, pointer
drop and three classifier checks) all completed and reported `ACCEPTED` for
the explicit scope `stock+CFG and four separate S6 components; no actual
helper`. This is compatibility evidence for the combined console, not a
promotion of the actual helper or of unreviewed A1/tuple components.

## Next components: actual typed select and pointer drop — before implementation

The O6 complete actual MIR contains two intrinsic selects specialized to
`*mut *const Element`, in blocks 4/5 with no unwind, and one specialized to
`MaybeUninit<*const Element>` in block 8 with no unwind. S6's intrinsic gate
has an actual-only branch requiring exactly one pinned actual body and **no**
local intrinsic adapters. It certifies the std intrinsic fallback source,
`rustc_intrinsic`/`rustc_nounwind` declaration, the nominal `DropOnPanic` ADT,
and every actual local, statement, call, successor and cleanup block before
admitting the typed compiler value rule. Its two separately checked local O3
adapters corroborate these pointer and wrapper rules, but the compiler
intrinsic's correspondence to Rust remains trusted. Inserting those adapters
into the actual fixture would violate the existing exact actual branch.

The same MIR has an actual `*mut *const Element::drop_in_place` call in block
6, normal successor 7, unwind cleanup 13. S6's pointer-drop gate requires
one local unsafe `sort4_checked_pointer_drop` body, source-specialized from
the pinned `mut_ptr.rs` method, and the pinned `ptr/mod.rs` free function and
compiler `drop_glue` mapping. The accepted O3 method proof requires an
initialized pointer-valued cell and returns that cell plus thread without
unwind. The actual redirect is allowed only after the local typed method MIR
and source certificate pass; it is expected once, with one modeled compiler
glue call. This rule owns no `Element` pointee. It does not prove the nominal
guard's Drop implementation or create its missing resource invariant.

The proposed diagnostic keeps the constructor/as_mut_ptr fixture and exact
actual body. First run only the intrinsic gate and require the complete actual
MIR certificate and counts `ptr=2, wrapper=1`. Then add only the certified
pointer-drop method and activate its gate, requiring local method return/leak,
one glue and one actual redirect; a source-operand mutant must be rejected by
the exact certificate before proof. Each case records NORMAL/readonly complete
MIR, all stages, source hashes and first verifier error. The intended next
unsupported call after both gates is `std::mem::forget`, but an earlier missing
ownership chunk in the actual guard path is a meaningful blocker, not a
negative control. No ghost `guard.own=true` bridge, cleanup deletion or
assumption about successful actual-call resources is authorized by this
diagnostic. No whole helper claim follows from translation counts alone.

The eventual actual-helper normal post must preserve the caller thread and
return the selected input pointer (`condition ? true_val : false_val`) while
accounting for the actual initialized wrapper cells and nominal guard's
destruction/forget rights; no `Element` pointee permission may be fabricated.
An eventual no-unwind post must be justified from each pinned callee and the
real cleanup graph, including the common block 13 from pointer drop, forget
and assume_init. These posts are **outside** the diagnostic classifier; its
acceptance means source/type/CFG linkage and local callee proofs only.

`check-intrinsic-drop-linkage.py` implements these three isolated hosted cases.
The first has constructor/as_mut_ptr plus the actual typed-intrinsic gate. The
second adds the exact O3 pointer-drop method. The third mutates only its
auxiliary call operand and requires the exact source certificate rejection
before any function proof. Positive classifications require the intrinsic
source and complete actual MIR gate, typed `2+1` call count, earlier `2+2`
redirects and local proof checks. The pointer-drop case also requires its
complete local MIR gate, local return/leak checks, one modeled glue call and
one actual method redirect. It records the first actual verification error
without interpreting it as an intended negative; a later ownership error
does not count as a complete helper proof. All variants retain the unchanged
actual Rust body and original/verified runtime identity. This script uses no
new translator patch. Python AST parsing and `git diff --check` passed; no
executable stages ran on the server.

## O8 gate failure and narrow fixture repair — before amendment

O8 run `37706123317` used the reviewed driver. All three cases completed
NORMAL/readonly export+decode and refinement with unchanged source hashes.
Every full verification stopped before function proof with the same exact
S6 fatal: `SORT4-SELECT-INTRINSIC: certificate mismatch: actual SAFE
contract/source signature`. The new intrinsic actual-source gate expects the
same full `thread_token`, conditional pointer-result and false-unwind
postconditions as the O4 capture fixture, but it pins different **ghost
annotation formatting**: adjacent annotation blocks, eight spaces before
the conditional expression, and a single-line `on_unwind_ens` block. O4's
source preparer emits separated blocks, four spaces and a multiline unwind
block. Runtime body, signature and Rust MIR are unchanged; this is not an
ownership or intrinsic semantics failure.

The next driver revision should replace exactly one byte sequence of the O4
ghost contract with the S6 gate's reviewed exact bytes, asserting that ghost
stripping both old and new source yields identical runtime Rust and that the
three complete clauses remain unchanged. No verifier patch, new condition,
post weakening, cleanup edit or source-body edit is justified. The original
O8 three `INCONCLUSIVE` outcomes remain recorded; only a fresh hosted run
can assess actual intrinsic/drop admission and the next causal proof blocker.

O9 run `37707055478` failed during fixture construction, before any of the
three cases. The original replacement gate compared the *entire* ghost-stripped
files byte for byte. The exact O4 contract has newline separators after each
ghost block; the S6 gate contract has adjacent blocks. The constructor-family
ghost stripper removes block contents but retains those separators, so the
comparison rejects harmless whitespace between the signature and actual
body. O9 is a setup failure, not a negative or intrinsic admission result.

The revised gate splits at the unique, reviewed contract bytes and checks
that the following suffix starts with the exact actual body's opening brace.
It replaces only that ghost span, requires both spans to strip to whitespace,
and compares their complete clause token sequences after whitespace
normalization. The prefix and suffix, including every actual body byte, are
unchanged. `make_case` still checks the source-certified body appears exactly
once in both original and verified files and records the source certificate;
the typed MIR and full source gates remain mandatory on the hosted runner.
No proof or admissibility status changes until O10 completes.

Hosted invocation after the as_mut_ptr result has been inspected:

~~~bash
python3 research/challenge-8/overnight-linkage/check-intrinsic-drop-linkage.py \
  --tool-home "$source_home" \
  --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" \
  --compiler-sysroot "$compiler_sysroot" \
  --evidence "$ev/intrinsic-drop-linkage" \
  --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))"
~~~
