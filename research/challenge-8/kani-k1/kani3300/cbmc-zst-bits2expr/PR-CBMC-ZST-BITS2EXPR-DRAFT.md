# Fix reconstruction of arrays with zero-width elements

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

Baseline source: `37a17adc07f29e1127f100debf1d8eea00532a24` (develop). The final paired invocation is pending:

- CBMC version: PENDING final baseline invocation.
- Exact command and working directory: PENDING the same invocation.
- Verbatim `Invariant check failed` block, including File/Condition/Reason: PENDING the same invocation.

The struct branch already accepts zero-width components. With a zero element width, the existing array loop takes empty slices and recursively builds one operand per element, retaining both the element count and the original array type. This change accepts width zero in that branch and adds one regression plus three unit cases alongside the existing bit-order case.

Kani encounters the same invariant for Rust input: [model-checking/kani#5085](https://github.com/model-checking/kani/issues/5085).

## Testing

Paired baseline/fix regression runs in the five standard profiles are pending. The four focused unit cases in Make and CMake builds and final formatting checks are pending.

- [ ] Each commit message has a non-empty body, explaining why the change was made.
- [ ] Methods or procedures I have added are documented, following the guidelines provided in CODING_STANDARD.md.
- [ ] The feature or user visible behaviour I have added or modified has been documented in the User Guide in doc/cprover-manual/
- [ ] Regression or unit tests are included, or existing tests cover the modified code (in this case I have detailed which ones those are in the commit message).
- [ ] My commit message includes data points confirming performance improvements (if claimed).
- [ ] My PR is restricted to a single feature or bugfix.
- [ ] White-space or formatting changes outside the feature-related changed lines are in commits of their own.

Checklist applicability: no new production methods; no new User Guide feature or interface; no performance improvement is claimed. These three items are n/a; the template wording above is retained verbatim. Source diff and test inclusion are prepared; completion of CI remains pending.

*Disclosure: this change and description were prepared with the help of AI assistants.*
