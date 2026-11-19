# Concrete suggested edits — recommendation only

Apply no production C++ or unit-test changes. Retain all existing upstream comments, copyright/license material and the useful GNU C extension comment in the regression fixture.

## Required descriptor repair and comment cleanup

Replace `regression/cbmc/byte_extract_empty_struct_array/test.desc` with these exact contents. There are two empty lines after `main.c`: the options field and the grep-options field. This is a proposal contained only in this review packet.

```text
CORE gcc-only
main.c


^EXIT=0$
^SIGNAL=0$
^VERIFICATION SUCCESSFUL$
--
^warning: ignoring
Invariant check failed
--
Reconstructing a constant aggregate with an array of GNU C empty structs
preserves the bytes on both sides of its zero-width member.
```

The comment edit is optional P3 prose cleanup; the added blank header field is the P2 oracle repair. Preserve the exact required/forbidden patterns. No `.out` file, internal-abort expectation, broad ignore, driver change or new regression folder is needed.

## Code and test edit list

| Location | Recommendation |
|---|---|
| `src/util/simplify_utils.cpp:345` | Keep `CHECK_RETURN(el_size_opt.has_value() && *el_size_opt >= bitst{0});`. |
| Existing array recursion at lines349–362 | Keep count-controlled reconstruction and exact array/element types. |
| `unit/util/simplify_expr.cpp:113–217` | Keep all three TEST_CASEs, loops and assertions; no helper extraction or test merging. |
| `regression/cbmc/byte_extract_empty_struct_array/main.c` | Keep the exact reported reproducer and both surrounding-byte oracles. |
| Original PR narrative | Use SUGGESTED-PR.md after owner review; preserve the real issue/disclosure and supply one actual final-revision standard CI link when available. |

No broader correctness repair or implementation is requested by this review. Native formatting and test execution remain a later authorized step.
