<!--
Upstream PR draft; no publication performed by this edit.
Final source: 9f2d01ec2bf115879c86e22203d403ba156d22e5, parent107a1e504cd69a2f3483717c8bcfcfa59814c557.
Standard fork CI ran on e364ad679d83db20c863912c2920b5864669d648 (closed fork PR#1).
The final source differs only by formatting two TEST_CASE headers; no new full-matrix run is claimed.
CI result categories are coordinator-reported; GitHub job metadata confirms their conclusions.
Remaining publication blocker: exact reproduction transcript. Curated r2 records do not retain a matched
version/argv/verbatim invariant block for this final main.c. The old6.11 block concerns a different input.
Replace the PENDING fields together from ONE baseline invocation; do not reconstruct text from source.
-->

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

Reproduction transcript (awaiting one matched baseline record):

- CBMC version and unpatched commit: PENDING.
- Exact command and working directory for the input above: PENDING.

```text
Invariant check failed
File: PENDING — verbatim from the same baseline invocation
Condition: PENDING — verbatim from the same baseline invocation
Reason: PENDING — verbatim from the same baseline invocation
```

The struct branch already accepts zero-width components. With a zero element width, the existing array loop takes empty slices and recursively builds one operand per element, retaining both the element count and the original array type. This change accepts width zero in that branch and adds one regression plus three unit cases alongside the existing bit-order case.

Kani encounters the same invariant for Rust input: [model-checking/kani#5085](https://github.com/model-checking/kani/issues/5085).

## Testing

Fork CI on `e364ad67` passed the standard Linux Make/CMake, Z3, 32-bit, ARM, Windows, Intel macOS and BSD jobs, plus the auxiliary API, analysis, profiling and performance checks. THOROUGH was blocked by Maven/JBMC plugin resolution, Codecov lacked its secret and macOS 26 was cancelled; the clang-format failure was corrected in `9f2d01ec`, which only reformats two `TEST_CASE` headers.

- [x] Each commit message has a non-empty body, explaining why the change was made.
- [x] Methods or procedures I have added are documented, following the guidelines provided in CODING_STANDARD.md.
- [x] The feature or user visible behaviour I have added or modified has been documented in the User Guide in doc/cprover-manual/
- [x] Regression or unit tests are included, or existing tests cover the modified code (in this case I have detailed which ones those are in the commit message).
- [x] My commit message includes data points confirming performance improvements (if claimed).
- [x] My PR is restricted to a single feature or bugfix.
- [x] White-space or formatting changes outside the feature-related changed lines are in commits of their own.

Checklist applicability: documentation of new production methods, a new User Guide feature or interface, and performance data are n/a; none is introduced or claimed.

*Disclosure: this change and description were prepared with the help of AI assistants.*
