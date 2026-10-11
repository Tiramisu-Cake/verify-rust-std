# Actual caller entry and exact slice pointer projection — experimental candidate

The consumer is the first `sort4_stable(v_base, scratch_base, is_less)` at
`library/core/src/slice/sort/shared/smallsort.rs:254`, within the actual
`small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T, &T) -> bool>`.
The entry must preserve `len < 2`, the evaluated `scratch.len() < len + 16`
check and its `intrinsics::abort()`, both actual `slice::as_mut_ptr` calls,
the `scratch_base` cast, and the original `if const { size_of::<T>() <= 16 }
&& len >= 16` / `else if len >= 8` decision. No new positive-size assumption
or ZST return is permitted: ZST with `8 <= len < 16` reaches the selected
first-call boundary. The source fragment stops at that boundary; it cannot
provide a callable summary or prove the rest of the function.

The first falsifiable hypothesis is narrow. The pinned implementation of
`core::slice::<impl [T]>::as_mut_ptr` in `slice/mod.rs:778` has body
`self as *mut [T] as *mut T`. A generic native-reference component with those
exact runtime cast operations should verify its complete generated normal,
unwind, lifetime, local-free and leak posts. Then the previous source-specific
`as_ptr` translator arm can admit only the exact compiler-derived
`std::slice::<impl [T]>::as_mut_ptr` symbol, lowering its one receiver to the
existing typed metadata-stripping pointer cast. This returns a pointer value;
it adds no ownership, source cells, scratch permission, lifetime, type
interpretation or alias fact. Both `v` and `scratch` instantiations must retain
their complete native arrays/foreach owners, with `scratch` still opaque
`MaybeUninit<T>` storage. A fresh wrong-pointer assertion and a missing-raw-
permission assertion must fail at their intended points after the projection.

This one-symbol rule is rebased from the historical own-lane
`verifast-slice-as-mut-ptr.patch` (SHA-256
`f200a5812149bb2278ded1d1ccb27a104b3dec3c03c5e40c79e30409d0d06916`)
onto the exact current ZST/C1/C4 experimental translator. The historical O26
profile, unrelated `MaybeUninit::as_mut_ptr` rule, kernel, solver, parser,
prelude, ownership/alias model and generic callback rules are not imported.
The source method body, generated component source, source-pair hashes, full
normal/read-only MIR, pre/post AST, before/after translator and all non-
translator tool hashes are admission pins. The component checks the copied
canonical operations; source and MIR identity checks are required before it
can justify this exact method rule. A separate maintainer trust review remains
necessary; even verifier exit 0 does not accept the profile.

The second case is an unfiltered actual-runtime-prefix diagnostic. It retains
the original guards and both method calls through the first sort4 callsite
boundary, with no selected-path precondition, artificial ZST return, or
supplied comparator/scratch resource. The boundary is a diagnostic cut; other
branches and later calls have no proof credit. Expected first obstruction from
historical evidence is the `len + 16` overflow VC or the absent explicit
`std::intrinsics::abort` binding, before pointer calls. Either is classified
as an open entry obligation, never an intended negative or a completed caller
bridge. Only if the pointer calls are reached may CURRENT `v` source and
foreach owners, opaque scratch, current F, thread/lifetime/type resources,
pointer provenance and full normal/unwind/early resource restoration be
credited, each at its actual verifier obligation and source span.

Positive gates: exact std source SHA and method body bytes; native generic T
and `MaybeUninit<T>` instances; full generated posts on normal and unwind,
local free and leak checks; all registered physical AST nodes executed;
paired normal/read-only full MIR and refinement. Negative gates: wrong pointer
value and missing raw authority fail at their exact assertions; malformed,
wrong source, extra body and default-off modes refuse before proof. A setup,
frontend, earlier overflow, abort or unrelated helper failure cannot count as
a negative. The entry diagnostic records its first actual obligation even if
it cannot complete. No `MaybeUninit` inverse, arbitrary writable `T`
destination, external caller-to-callee applicability, C5/select/copies, whole
`sort4_stable`, or full SmallSort claim follows from this experiment.
