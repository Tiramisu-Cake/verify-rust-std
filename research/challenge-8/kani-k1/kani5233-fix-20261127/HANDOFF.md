# Kani 5233 fix handoff

The candidate is a local commit in `/root/kani-5233-fix-w11` on `fix/vv-array-element-cast`. It is one commit above upstream `main` `8c6dba5935`, fetched from GitHub on 2026-11-27. It has not been pushed.

| Identity | SHA |
| --- | --- |
| Commit | `7d5e549f4672e838e4f55aa2d7f69ea6ada2568e` |
| Tree | `82e3723adcf70194b49ce5b169e32a1c5425cce5` |
| Parent | `8c6dba5935e8b37a905145c57572d1b67489bae2` |

Author and committer are `Tiramisu-Cake <igkharin@gmail.com>`. The message has no `Co-Authored-By` and no `#<digit>`.

## Why the pass rejects mutable casts

The check is in `visit_rvalue`, `CastKind::PtrToPtr`, in `check_values.rs`. A cast `*mut S as *mut U` gives a pointer through which a store writes a valid `U` into memory the program reads as `S`. Nothing at the store checks that the bytes are a valid `S`. They can be invalid at the cast's own address if `U` allows a value `S` doesn't. Pointer arithmetic on the new pointer moves in steps of `size_of::<U>()`. `q.add(k)` can therefore reach offsets in `S` whose requirements differ from `U`'s, and the write stays in bounds, so pointer checks don't fire.

Before #5205, the pass did not track how bytes were written. Values were checked where they were created (transmutes, aggregates, union reads, raw-pointer derefs), but a later read of `S` through a reference or through the owning local was not checked. The only defence was to reject the cast unless `U`'s per-offset requirements list equals `S`'s.

After #5205 (the parent commit), most of this is covered by the untyped-write model in `library/kani_core/src/valid_value.rs`. `record_store` marks a store through any pointer as untyped when the stored type's validity is expressible (`untyped = through_pointer && validity.is_ok()`). That includes restricted types: the comment cites `*mut NonZeroU8` cast from `*mut bool`. Typed reads through a dereference, or of an address-taken local, then check the full requirements of the type read. `untyped_paths.rs::ub_store_of_other_restricted_type` already reaches a `bool` through `*mut u8 as *mut NonZeroU8` (the `u8` source bypasses the cast check) and is caught at the read. The cast check still guards these cases:

- A target whose validity can't be expressed (`Err`). Its stores clear the mark instead of setting it, so the model would not see them.
- A source whose validity can't be expressed.
- Reads the pass does not instrument, as defence in depth: Kani's own functions and models, and closure captures inside the closure body.

## Choice: array-element rule, not the prefix rule

The commit accepts the cast when the target pointee is the element type of the source array, or of an array nested in it. This holds only inside the existing branch where both validity lists are `Ok` and the source list is non-empty, so every `Err` case above is still reported. The argument does not depend on the untyped-write model:

1. Array elements sit at multiples of the stride, and the stride equals `size_of::<T>()`. Nested arrays are contiguous, so `[[T; M]; N]` has a `T` at every `k * size_of::<T>()` for `k < N * M`. Every slot that `p.add(k)` reaches inside the array is a `T` slot with exactly `T`'s requirements. A store of a valid `T` there can't make the array invalid. Past the end of the array, the situation is the same as for any element pointer obtained without a cast.
2. The pass already accepts the same pointer (address, provenance, pointee type) without the cast check. Unsizing `*mut [T; N]` to `*mut [T]` is a `PointerCoercion`, which isn't checked. Then `*mut [T] as *mut T` (`<*mut [T]>::as_mut_ptr`, and also `arr.as_mut_ptr()` through auto-deref) has a source pointee `[T]` whose `ty_validity_per_offset` is `Ok(vec![])` (`FieldsShape::Array { count: 0 }`), so it returns before the comparison. The checks after the cast depend only on the pointer's type, because the pass has no dataflow. The rule therefore lets the program do nothing it couldn't already do.
3. Bytes that are invalid for `T` can still reach the array through untyped writes on the element pointer (`write_bytes`, copies, `*mut u8` casts). These are marked and checked at the next typed read of the array. The `ub_invalid_byte_through_elem_ptr` test covers this.

I rejected the prefix rule from the issue text (target requirements equal the source requirements in `[0, size_of::<T>())`). It constrains only the slot at offset 0. Counterexample: `#[repr(C)] struct S { a: NonZeroU8, b: bool }` with `T = NonZeroU8`. The prefixes agree, but `(p as *mut NonZeroU8).add(1).write(NonZeroU8::new(2).unwrap())` is in bounds and writes `2` into `b`. Under the prefix rule, only the untyped-write model would catch that. If maintainers want to rely on the model for every expressible cast, the consistent change is to drop the comparison for `Ok` validity altogether. That is a larger policy decision and is not this patch.

Other decisions:

- The rule requires the exact element type, compared as interned stable `Ty` values. Other targets with the same requirements, such as a `#[repr(transparent)]` wrapper of `T`, or a shorter sub-array `*mut [T; M]` with `M < N`, are still reported. The existing equal-lists path still accepts them when the lists match.
- `is_array_element` stops at a pattern type before calling `ty.kind()`. This follows the file's existing guards against converting the stable kind of pattern types.
- Not verified and outside scope: the existing equal-lists rule ignores the type size. For example, a `#[repr(C)]` pair of `NonZeroU8` and `u8` may produce the same list as `NonZeroU8`. Such a cast would rely on the untyped-write model in the same way as the prefix rule.

## Diff summary

- `kani-compiler/src/kani_middle/transform/check_values.rs`: the mutable-cast comparison now also skips the report when `is_array_element(tcx, src_pointee, dest_pointee)` holds. The new helper peels array types and compares each element type with the target pointee. 22 lines in total, including one comment.
- `tests/expected/valid-value-checks/array_element_cast.rs` and `.expected`: a new expected test (6 harnesses, `-Z valid-value-checks`). It sits next to `untyped_store.rs` and `untyped_paths.rs`, where the existing valid-value expected tests live.

## Tests and expected outputs

| Harness | What it does | Expected |
| --- | --- | --- |
| `array_elem_cast_nonzero` | The issue MRE: `MaybeUninit<[NonZeroU8; 4]>`, `as_mut_ptr() as *mut NonZeroU8`, write, cover | verifies, cover `SATISFIED` |
| `array_elem_write_then_read` | `[NonZeroU8; 4]` → `*mut NonZeroU8`, `add(2).write(7)`, read the whole array, assert | verifies, cover `SATISFIED` |
| `nested_array_elem_cast` | `[[NonZeroU8; 2]; 2]` → `*mut NonZeroU8` (`add(3)`) and → `*mut [NonZeroU8; 2]` (row write), read the grid, assert both | verifies, cover `SATISFIED` |
| `ub_invalid_byte_through_elem_ptr` | `write_bytes(element.add(2), 0, 1)`, then read the array as `[NonZeroU8; 4]` | fails: ``Undefined Behavior: Invalid value of type `[std::num::NonZero<u8>; 4]` `` |
| `bool_array_to_nonzero` | `*mut [bool; 2]` → `*mut NonZeroU8` (different element requirements) | fails: unsupported `mutable cast` for `*mut [bool; 2]` |
| `nonzero_array_to_wider_nonzero` | `*mut [NonZeroU8; 4]` → `*mut NonZeroU16` (a zero byte is a valid `NonZeroU16` byte) | fails: unsupported `mutable cast` for `*mut [std::num::NonZero<u8>; 4]` |

Summary line: `Complete - 3 successfully verified harnesses, 3 failures, 6 total.`

Expected-file risks for CI:

- Type printing: `std::num::NonZero<u8>` and `*mut [std::num::NonZero<u8>; 4]` match the issue's actual output. `[bool; 2]` and the bare array type `[std::num::NonZero<u8>; 4]` in the UB message are assumed to print the same way.
- The `NonZeroU8` values are `const`s (`NonZeroU8::new(n).unwrap()` evaluated at compile time), so the passing harnesses don't depend on runtime checks inside `NonZero::new`.
- The casts use typed `*mut [..]` locals, so rustc lowers them as `PtrToPtr` and not as an array-to-pointer coercion from a reference.

## Validation

`git diff --check HEAD^ HEAD` passed. `/root/rustfmt-toolchains/bin/kani-fmt-check.sh /root/kani-5233-fix-w11 HEAD` gave `FMT_OK`. The first commit had a rustfmt line-wrap difference, which was fixed by amending. Compilation, clippy and the expected test are pending coordinator fork CI. No local cargo, rustc, Kani or CBMC was run.

## Draft PR

**Valid-value checks: accept mutable casts from an array to its element type**

Under `-Z valid-value-checks`, casting `*mut [T; N]` to `*mut T` was reported as an unsupported `mutable cast` whenever `T` has validity requirements, because the requirements of the whole array differ from those of one element. `core` uses this cast for the scratch buffer of its small sorts.

This accepts a mutable cast whose target is the element type of the source array, or of an array nested in it. Pointer arithmetic from the element pointer only reaches slots that hold a `T`, and the pass already accepts the same pointer when it comes from a slice (`*mut [T] as *mut T`). Casts that change what an element may hold, such as `*mut [bool; 2]` to `*mut NonZeroU8`, are still reported, and invalid bytes written through the element pointer are still caught when the array is read.

Resolves #5233

Testing: [pending fork CI]

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
