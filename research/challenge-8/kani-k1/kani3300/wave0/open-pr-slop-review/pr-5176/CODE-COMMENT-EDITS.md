Suggested edits only; source checkout remains untouched.

At typ.rs:1319 replace the seven new comment lines with:

```rust
// CBMC reconstructs this wrapper from a bitvector during union copies.
// Use an empty struct for zero-sized payloads containing arrays of
// zero-width elements (diffblue/cbmc#9487). Rustc layout is available
// while recursive GOTO types are incomplete. The union field below
// retains its logical type for projections.
```

Keep the condition, codegen_ty_unit call, ty.clone branch, padding and unionfield
arguments unchanged. Preserve all unmodified upstream documentation above it.

In both recursive files replace the comment above the union with:

```rust
// The pointer field reaches this union while the enclosing struct is incomplete.
```

Replace the comment before the inferred null cast with:

```rust
// The inferred pointer type reaches the union through the enclosing struct.
```

Keep the casts, black_box, null assertions, derive/repr and allow(dead_code).
Change only these two cover strings and their matching expected descriptions:

| Harness | Old string | Suggested string |
| --- | --- | --- |
| recursive_arm | recursive_arm retained null root | recursive_arm retains null pointer |
| recursive_zst_arm | recursive_zst_arm retained null root | recursive_zst_arm retains null pointer |

In the five edge modules remove the repeated comment “The ZST arm is deliberately
first, including for the nested shapes.” The array_first harness name already
documents order; each concrete type shows its own first field. Keep the bytes-
span-full-extent comment where it explains why reading byte data is valid.

In array_typed_copy replace the new negative construction “This union's byte arm
covers every byte: there is no padding to read.” with:

```rust
// The byte arm spans the full initialized union storage.
```

Above padded_typed_copy_c use:

```rust
// Check the payload's initialized fields after the typed copy.
```

Retain the useful offset8 and zero-count pointer-alignment comments, copyright,
SPDX lines, module description and all unmodified upstream comments. No additional
generic helpers, macros, flags, ignored checks, instrumentation or source logic
changes are proposed.
