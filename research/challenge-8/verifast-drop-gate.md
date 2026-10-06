# Direct `CopyOnDrop<T>::drop` body gate

This gate extracts the actual 364-byte `CopyOnDrop<T>` type and `Drop` impl
from [SmallSort](../../library/core/src/slice/sort/shared/smallsort.rs).
The source file is pinned to SHA-256
`32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`;
the block is pinned to
`caff1edbfa3a8d9fd29459e49c43abd0f8f987f9061c75e7bf6ecedbbba26a6a`.
[extract-verifast-drop.py](extract-verifast-drop.py) emits isolated
`original/lib.rs` and `verified/lib.rs` crates. Their only difference is
three ghost contract comments inserted at the original `fn drop(&mut self)`
signature. Removing those exact comments restores the original crate bytes.
The extractor records full source, block, contract and crate hashes in
`extraction.json`; the hosted runner must also pass the refinement checker.
The report names the expected `<CopyOnDrop<T> as core::ops::Drop>::drop`
verification target and the exact line of its `copy_nonoverlapping` call
in `verified/lib.rs` for log auditing.
No Rust field, signature, statement, unsafe block or algorithm changes.

The explicit method contract requires the actual three guard fields and
padding, a fractional initialized `src[..len]`, a full initialized
`dst[..len]`, a thread token, `type_interp<T>`, and exactly one logical
`foreach(src_values, own<T>(t))`. The normal postcondition returns all of
those resources while establishing **`dst[..len] |-> src_values`**. The
source bytes and single logical ownership sequence remain available; copying
does not mint a second `T.own`. Its unwind postcondition is false because
the method only invokes the pinned `copy_nonoverlapping` specification,
which also has `on_unwind_ens false`. The contract has arbitrary `T` and
arbitrary `len`; it does not assume `T: Copy`, no-drop, or positive size.

The actual method body must verify under this satisfiable explicit
precondition, with trace evidence that the `ptr::copy_nonoverlapping` call
in the extracted source executes. The check must not count a vacuous
compatibility proof against the automatically generated safe-`Drop`
contract as method-body verification. Because `CopyOnDrop` has private
fields, VeriFast's default `<CopyOnDrop<T>>.own` is `false`; this gate does
not replace it or pretend that the actual compiler-generated cleanup can
already consume a guard ownership predicate.

The current `insert_tail` prefix has passed guard construction, the first
shift, and the `gap_guard.dst = sift` update on hosted Actions. At the first
cleanup path, the pinned generic `std::ptr::drop_in_place` summary requires
`<CopyOnDrop<T>>.own` and returns only the thread token and unknown guard
storage. Proving this direct method contract does **not** specialize that
generic summary, establish the guard invariant at construction, or restore
the destination range on normal or unwind cleanup. Those are separate proof
and model obligations. The extracted body gate is a prerequisite for any
future specialization: a summary may be used only after the actual callee
has been verified at the same source version.

The gate uses the already pinned VeriFast 26.09 source profile with tuple,
HRTB, lifetime-cut, address-taken, and tracked `ManuallyDrop` reference
patches. Compilation, refinement checking and verification run only on
GitHub-hosted Actions; the editing server performs static reading and
editing only.
