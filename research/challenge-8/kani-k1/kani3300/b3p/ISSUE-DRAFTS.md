# Issue drafts for B3 (owner publishes; nothing filed yet)

CBMC repro verified with `cbmc` 6.11.0 in fork CI run https://github.com/Tiramisu-Cake/kani/actions/runs/43241563566 (`v1_deref.c` aborts with exit 134; `v3_union.c` and `v4_array.c` hit the same invariant; `v2_memcpy.c` passes).

---

## 1. model-checking/kani

**Title:** CBMC invariant failure (`bits2expr`) when copying a padded union with a zero-sized array field

With default checks, a typed copy of a union whose smaller field is a zero-sized array makes CBMC abort:

```rust
#[repr(C)]
union ArrayUnion {
    bytes: [u8; 8],
    zst_array: [(); 2],
}

#[kani::proof]
fn array_typed_copy() {
    let mut src = ArrayUnion { zst_array: [(); 2] };
    let mut dst = ArrayUnion { zst_array: [(); 2] };
    unsafe {
        std::ptr::write_bytes((&mut src as *mut ArrayUnion).cast::<u8>(), 0x5a, 8);
        std::ptr::write(&mut dst, std::ptr::read(&src));
        assert_eq!(dst.bytes, [0x5a; 8]);
    }
}
```

```
Invariant check failed
File: ../src/util/simplify_utils.cpp:345 function: bits2expr
Condition: el_size_opt.has_value() && *el_size_opt > 0
Reason: Check return value
```

Kani 0.68.0 (`main` at bf9c58e662), CBMC 6.11.0, x86_64 Linux.

`codegen_union` wraps the zero-sized field in a padded struct `{ [(); 2], padding }`, and CBMC cannot rebuild an array of zero-width elements from a bitvector. #5085 reports the same CBMC invariant for statics and constants. The root cause is in CBMC (filed as diffblue/cbmc#N), but Kani can avoid generating this shape for union fields.

*Disclosure: this issue was prepared with AI assistance.*

---

## 2. diffblue/cbmc

**Title:** `bits2expr` invariant failure on a struct containing an array of zero-sized elements

```c
#include <string.h>
struct E {};
struct W { struct E z[2]; char pad[8]; };

int main(void) {
  char buf[8];
  memset(buf, 0x5a, sizeof buf);
  struct W w = *(struct W *)buf;
  __CPROVER_assert(w.pad[0] == 0x5a, "copied");
  return 0;
}
```

`cbmc test.c` with CBMC 6.11.0 aborts (exit code 134):

```
Invariant check failed
File: ../src/util/simplify_utils.cpp:345 function: bits2expr
Condition: el_size_opt.has_value() && *el_size_opt > 0
Reason: Check return value
```

`struct E {}` is the GNU empty-struct extension, so `z` has width 0. `bits2expr` rejects array types whose element width is zero, although such an array is zero bits wide and could be rebuilt from an empty bitvector. The same happens when `struct W` is a member of a union that is copied through a pointer.

This shape comes up naturally from Rust: zero-sized types such as `()` and arrays of them are common, and Kani hits this invariant (model-checking/kani#5085, model-checking/kani#N).

*Disclosure: this issue was prepared with AI assistance.*
