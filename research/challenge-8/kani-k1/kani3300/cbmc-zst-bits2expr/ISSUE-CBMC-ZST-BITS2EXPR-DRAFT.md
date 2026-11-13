<!-- Draft only. Owner publishes after review/duplicate check. No issue has been opened. -->

**Title:** bits2expr aborts on arrays of zero-width elements inside a nonempty struct

**CBMC version:** `cbmc-6.11.0`; also reproduced on develop `107a1e504cd69a2f3483717c8bcfcfa59814c557` with the same tests in fork CI.

**Operating system:** Linux x86_64; the paired develop run used Ubuntu 24.04 and GCC 13.

**Exact command line resulting in the issue:**

```sh
cbmc --gcc --c11 --64 --little-endian --validate-goto-model --validate-ssa-equation repro.c
```

`repro.c` uses GNU C empty structs:

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

**What behaviour did you expect:**

Successful verification: the zero-width field consumes no bits, and the eight payload bytes remain `0x5a` after the typed copy.

**What happened instead:**

CBMC aborts in `src/util/simplify_utils.cpp:345`, function `bits2expr`, at the array element-width invariant. The CBMC 6.11.0 reproduction exited with code 134. Develop's corresponding condition still requires `el_size_opt.has_value() && *el_size_opt > bitst{0}`.

The struct conversion already permits zero-width components, but recursing into the array rejects its zero-width element type. A `memcpy` version of the same copy verifies. Union copies, nested arrays and zero-width fields next to an integer reach the same invariant in our focused cases.

In [paired fork CI](https://github.com/Tiramisu-Cake/cbmc/actions/runs/43334186094), develop plus the new tests hit the invariant in 12 of 13 focused cases; the `memcpy` control passed. Allowing a known zero element width lets the existing recursion reconstruct each typed element from an empty slice without consuming neighboring payload bits. All 13 fixed-case oracles then passed, including an intentionally failing payload assertion.

The shape also occurs in Rust-generated input; see model-checking/kani#5085. The C reproducer isolates the CBMC conversion failure; no actual Kani/Rust replay is claimed here.

*Disclosure: this change and description were prepared with the help of AI assistants.*
