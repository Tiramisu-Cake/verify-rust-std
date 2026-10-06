# Generic guard cleanup: pinned-model investigation

Source investigation and hosted proof progress, 2026-10-06. The actual
destructor body passes gate37419989766; compiler-cleanup reuse remains open.
VeriFast26.09 source pin
`809de4596839b739dd999f9e462242c835e3af46`; actual std source unchanged.

The pinned MIR translator lowers Rust `Drop` terminators to a call to
`std::ptr::drop_in_place`:
[translator lines2743-2780](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml#L2743).
The generic specification requires the object and its `T.own` predicate,
but both normal and unwind postconditions return only thread_token and
unknown object storage:
[lib.rsspec lines533-536](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/bin/rust/std/lib.rsspec#L533).
It does not explicitly expose effects on the guard's destination range.

A contract on the actual `CopyOnDrop<T>::drop` method can be checked separately.
The repository already uses method-local contracts on `RawVec<T,A>::drop`.
However, such a method contract does not by itself replace the generic
drop_in_place summary used at compiler-generated cleanup. No supported verified
specialization route was found in this investigation. This is a source-level
model concern; an Actions gating probe is still needed before treating it as
a demonstrated cleanup-proof blocker.

The destructor contract needs initialized source elements, writable destination,
non-overlap, valid lengths, and a rule transferring the current held values and
generic ownership into the gap while preserving the surrounding range. Its
actual len is arbitrary in bidirectional_merge; insert_tail uses len1. The
pinned copy_nonoverlapping summary has exact normal byte effects and
on_unwind_ens false for valid inputs. The enclosing insertion proof must still
recover an initialized owned range after comparator panic. Generic references
permit interior mutation, so preservation of original keys/bytes requires a
separate functional assumption; safety must not assume that preservation.

Next gating experiment: exact-source guard body with a proved restoration
contract, plus a one-cell scope that requires destination ownership after its
actual compiler-generated cleanup. Compare direct method proof with the
translated drop_in_place call. If the latter cannot recover the resource, use a
principled, independently validated model extension or another approved route.
Never infer restoration from a skipped destructor or an assumed summary.

## Read, held value and first shift: model preparation

Read-only investigation at the same source pin, 2026-10-06. The translator
lowers `ptr::read` and pointer `.read()` to a typed dereference
(`vf_mir_translator.ml:2396-2399`). In `verify_expr.ml:2628-2630`, the
`read_lvalue` dereference branch consumes the matching object chunk to read
its value, then puts that chunk back with `chunks @ h`. The read therefore
preserves the modeled physical bytes; it does not remove the destination's
`points_to<T>` chunk. A logical ownership gap must be tracked separately.

`ManuallyDrop<T>` maps to `T` (`vf_mir_translator.ml:792`), and its `new` and
dereference operations are identities (`:2413-2416`). The next prefix
milestone is to recover the actual tail cell, verify its read and wrapper
construction, and initialize the guard around the held value. These prefix operations now pass in hosted run37417173472 at source
3eb19991b1d8c2312d9feae535b02068335f5162. The first physical shift and guard
destination update also pass; logical ownership transfer and cleanup do not.

The copy summary at `bin/rust/std/lib.rsspec:545-548` preserves the source's
physical values and writes those values to an initialized destination slice.
The retained tail bytes can supply that destination resource after the read;
the summary does not transfer or duplicate logical `<T>.own`. Ghost bookkeeping
must transfer ownership from tail to the held value, move each sift ownership
into the gap, and restore the held ownership through the actual guard cleanup.
Do not invent an uninitialized-destination blocker from the logical gap alone.
The generic ZST case still needs validation: distinct element positions may
have equal addresses and zero byte extent. No non-ZST assumption is added.

## Actual compiler cleanup reached

Hosted run37417173472 reaches the sift==begin break after the first physical
copy and dst update. Its actual compiler-generated drop requires
`own(CopyOnDrop_type_info(T))(t, guard_value)` at std/lib.rsspec567 and fails
there. The actual Drop method is still specless and skipped; this error is
neither a destructor proof nor proof that supplying opaque own would expose
restored destination resources. Next gate must check the actual method and
its reuse through compiler cleanup separately.

## Restricted compiler cleanup design review

Sol investigated the pinned frontend and Astra independently reviewed the
proposed boundary. This is an implementation plan, not a tested extension.
The current Drop translator always calls generic drop_in_place and ignores
DropData.unwindAction. Its ordinary trait-call specializer ignores impl
predicates and is unsuitable for unchecked reuse here.

A restricted direct lowering must resolve a bare local's exact ADT, match all
substitutions and supported predicates, deduplicate identical impl entries
by full identity, and require an annotated actual Drop body in the same unit.
The direct call can consume that body's concrete verified precondition; a
new guard own predicate is optional, and cannot be replaced by own=true.
Initially require exactly two raw pointer fields and one usize field, whose
drop glue does not destroy pointees. Account for all fields/padding through
ordinary storage predicates and leave no second owned guard. The caller
receives one logical element ownership sequence and the exact destination
values from the actual proved method.

Represent normal and unwind branches and CFG successors using the recorded
DropData.unwindAction, even when on_unwind_ens false makes the method's unwind
branch infeasible. A successful Drop called during comparator cleanup must
continue the original unwind path. Returning the held source fraction is
not enough: end_ref_readonly must run after guard Drop and before tmp storage
free, on both normal and comparator-unwind paths. Before-brace annotations
run too early; after-brace annotations alone miss cleanup paths.

No exporter/schema change is needed solely to capture Drop.replace: the
[pinned rustc MIR definition](https://raw.githubusercontent.com/rust-lang/rust/db3e99bbab28c6ca778b13222becdea54533d908/compiler/rustc_middle/src/mir/syntax.rs)
assigns that flag diagnostic significance only. The pinned exporter consumes
drop-elaborated MIR. The first implementation should remain restricted and
fail closed on unsupported places, fields, impl predicates or method contracts.

Hosted acceptance must include the actual method proof, normal and panic
caller cleanup, and negatives for missing source permission, missing element
ownership, mismatched/unsupported impl and a broken actual method postcondition.
The direct body gate passed37419989766 at19e74b59f9f2235c26b208cc3c9a96149e3d6cb5.
The next restricted local-Drop gate uses one-cell callers with raw source and
destination arrays, preserving exact copied values and ONE logical element
ownership sequence. These fixtures isolate compiler cleanup from the held
reference used by actual insertion; they do not establish tmp storage recovery.
After this gate, actual insertion still needs a proved release of held_ref
after Drop and before tmp storage is freed on both normal and unwind paths.
All insertion-loop invariants remain open.

## Held-reference recovery after the caller gate

Read-only preparation identifies a possible next checked contract variant.
For len1, the actual Drop body could require its existing fractional source
array, `ref_readonly_end_token(src, origin, f)` and `ref_initialized(src)`.
After the original copy, ghost-only code can open the singleton source array
and its empty tail, then call the existing `end_ref_readonly(src)` lemma.
The method would return the source fraction at origin, exact destination values
and ONE logical ownership sequence. The complementary origin fraction remains
in the caller's frame and must be merged before tmp storage cleanup. This needs
a separate proof of the actual method and normal/unwind callers at the same
source version; it is not supplied by the arbitrary-length direct body proof.

The current actual-insertion diagnostic still uses COMPARISON_DEBT_POST on
normal and unwind exits. After the successful strict cut those first-comparison
resources have been discharged, so that post is unsuitable for a completed
normal insertion proof. Crossing guard cleanup must not be confused with a
successful function exit. A next prefix experiment should keep the unrestricted
T/F,n>=2 domain and report its precise next failure; a green actual-function
proof requires accurate exit resource accounting as well. The readonly source
route must not be extended across the second comparison with `&tmp` without
handling generic interior mutability through the real sharing model.
