Title: Fix reconstruction of arrays with zero-width elements

`bits2expr` rejects an array whose element type has zero width when reconstructing a constant inside a larger aggregate. A typed read of constant bytes into this GNU C struct exercises the array branch through byte-extract simplification:

```c
#include <string.h>

// GNU C: an empty struct, and any array of it, has size zero.
struct empty
{
};

struct with_empty_structs
{
  unsigned char a[4];
  struct empty z[2];
  unsigned char b[4];
};

int main(void)
{
  unsigned char buf[8];
  memset(buf, 0x5a, sizeof(buf));

  struct with_empty_structs s = *(struct with_empty_structs *)buf;

  for(unsigned i = 0; i < 4; ++i)
  {
    __CPROVER_assert(s.a[i] == 0x5a, "bytes before the empty structs");
    __CPROVER_assert(s.b[i] == 0x5a, "bytes after the empty structs");
  }

  return 0;
}
```

With CBMC 6.11.0 (release build, x86_64 Linux), `cbmc main.c` aborts with exit code 134:

```text
--- begin invariant violation report ---
Invariant check failed
File: ../src/util/simplify_utils.cpp:345 function: bits2expr
Condition: el_size_opt.has_value() && *el_size_opt > 0
Reason: Check return value
```

The struct branch already accepts zero-width components. With a zero element width, the existing array loop takes empty slices and recursively builds one operand per element, retaining both the element count and the original array type. This change accepts width zero in that branch and adds one regression plus three unit cases alongside the existing bit-order case.

Kani encounters the same invariant for Rust input: [model-checking/kani#5085](https://github.com/model-checking/kani/issues/5085).

## Testing

The new regression test aborts with the invariant above on CBMC 6.11.0 and passes with this change. In my fork the standard workflows passed on Linux (Make and CMake, Z3, 32-bit, ARM), Windows, Intel macOS and BSD; the THOROUGH job could not resolve a Maven plugin for the JBMC models library, and a clang-format issue in the new unit tests has since been fixed.

- [x] Each commit message has a non-empty body, explaining why the change was made.
- [x] Methods or procedures I have added are documented, following the guidelines provided in CODING_STANDARD.md.
- [x] The feature or user visible behaviour I have added or modified has been documented in the User Guide in doc/cprover-manual/
- [x] Regression or unit tests are included, or existing tests cover the modified code (in this case I have detailed which ones those are in the commit message).
- [x] My commit message includes data points confirming performance improvements (if claimed).
- [x] My PR is restricted to a single feature or bugfix.
- [x] White-space or formatting changes outside the feature-related changed lines are in commits of their own.

No new methods, user-visible behaviour or performance claims are introduced, so the documentation and performance items do not apply.

*Disclosure: this change and description were prepared with the help of AI assistants.*
