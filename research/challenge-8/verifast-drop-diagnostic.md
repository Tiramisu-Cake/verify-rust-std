# Generic guard cleanup: pinned-model investigation

Read-only source investigation, 2026-10-06. No cleanup proof or Actions
reproducer yet. VeriFast26.09 source pin
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
