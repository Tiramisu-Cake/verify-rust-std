<!--
CBMC-SLIM draft, NOT READY TO PUBLISH. Supersedes the 13-directory proposal.
Direct PR to diffblue/cbmc develop; no separate issue and no PR inside the fork.
Planned base: 37a17adc07f29e1127f100debf1d8eea00532a24; new clean source SHA: TBD.
The consolidated regression and moved unit cases are NOT_RUN on this base.
Before publication replace receipt placeholders using ONE final baseline invocation:
same main.c bytes, exact version/commit, actual command, verbatim invariant block.
Do not combine an old6.11/r2 version or output with a new command.
Replace the two Testing sentences with verified results after the requested CI.
Checklist wording is verbatim from the pinned PR template; n/a notes are separate.
-->

**Title:** Allow bits2expr to reconstruct arrays of zero-width elements

`bits2expr` fails an invariant when reconstructing an array whose element type has zero width inside a larger aggregate. For example, a typed read of constant bytes into this GNU C aggregate reaches the array conversion:

```c
#include <string.h>

struct empty {};
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

Reproduction: `<exact CBMC version and develop commit from final baseline receipt>`; command: `<actual command for the same input and invocation>`.

```text
Invariant check failed
File: <verbatim path and line from that invocation> function: bits2expr
Condition: <verbatim array element-width condition from that invocation>
Reason: <verbatim reason from that invocation>
```

The struct branch already accepts zero-width components, and byte-operator lowering already admits zero-width members and zero-length arrays. With a zero element width, the existing array loop takes empty slices and still reconstructs one typed operand per element, so the change only needs to accept a known width of zero. Unknown and negative widths remain rejected.

Kani encounters the same invariant for Rust input: [model-checking/kani#5085](https://github.com/model-checking/kani/issues/5085).

### Testing

Testing of the consolidated regression and relocated unit cases on this candidate is pending. Paired results for the five standard regression profiles and focused unit results from Make and CMake builds will be added after execution.

### Checklist

- [ ] Each commit message has a non-empty body, explaining why the change was made.
- [ ] Methods or procedures I have added are documented, following the guidelines provided in CODING_STANDARD.md.

  n/a — no production methods or procedures are added.

- [ ] The feature or user visible behaviour I have added or modified has been documented in the User Guide in doc/cprover-manual/

  n/a — this internal conversion fix introduces no CLI or language construct.

- [ ] Regression or unit tests are included, or existing tests cover the modified code (in this case I have detailed which ones those are in the commit message).
- [ ] My commit message includes data points confirming performance improvements (if claimed).

  n/a — no performance improvement is claimed.

- [ ] My PR is restricted to a single feature or bugfix.
- [ ] White-space or formatting changes outside the feature-related changed lines are in commits of their own.

*Disclosure: this change and description were prepared with the help of AI assistants.*
