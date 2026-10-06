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
construction, and initialize the guard around the held value. This has not
yet been verified by the current insertion probe.

The copy summary at `bin/rust/std/lib.rsspec:545-548` preserves the source's
physical values and writes those values to an initialized destination slice.
The retained tail bytes can supply that destination resource after the read;
the summary does not transfer or duplicate logical `<T>.own`. Ghost bookkeeping
must transfer ownership from tail to the held value, move each sift ownership
into the gap, and restore the held ownership through the actual guard cleanup.
Do not invent an uninitialized-destination blocker from the logical gap alone.
The generic ZST case still needs validation: distinct element positions may
have equal addresses and zero byte extent. No non-ZST assumption is added.
