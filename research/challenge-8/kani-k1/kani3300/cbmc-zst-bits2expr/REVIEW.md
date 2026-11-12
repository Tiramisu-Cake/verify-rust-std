# Source review — CBMC ZST-BITS2EXPR

Candidate reviewed: `c0850c029faed04f8666de7f89045b5f04d246e1` (`Allow bits2expr to reconstruct arrays of zero-width elements`), parent `107a1e504cd69a2f3483717c8bcfcfa59814c557`.

## Findings

- **Low — negative constant array count reaches an invariant for zero-width elements.** In `src/util/simplify_utils.cpp:339-347`, the constant array count is cast to `size_t` before validation. With an invalid negative count and an element type of width zero, `pointer_offset_bits(array_type, ns)` computes `0 * negative == 0`, so the top-level width check at lines 203-212 accepts an empty bit string; the new `>= 0` element-width guard also accepts it, then `numeric_cast_v<size_t>` on the negative count fails its invariant (`src/util/arith_tools.h:98-111`). This input is outside valid C array declarations, so it does not undermine the valid-source fix, but the public utility's failure mode is a process invariant rather than its usual optional failure. Consider checking that the constant count converts to a nonnegative integer before casting, or explicitly document this invalid-type precondition. No regression input currently covers this edge.

## Review notes

The one-line change is limited to the array element-width guard and is consistent with the existing struct recursion: after the existing top-level type-width equality check, zero-width array elements slice `[i*0, 0)` from the empty bit string, recurse on their declared element type, and append one typed operand per constant count. Count zero naturally reserves/appends no operands. Nested zero-width arrays terminate as their count decreases the type recursion depth; no division by element width is introduced. Unsupported element types still return `nullopt` through the recursive call. Struct/union/tag handling and scalar endian mapping are unchanged. `expr2bits` already concatenates recursive operand strings, so empty elements round-trip without changing that path.

The new unit cases inspect array type and operand count, empty struct element type, nested zero-length/nonzero-length inner arrays, empty-bit round trips, a tagged type, a union arm, nonzero siblings, and both endian flags. The C cases use `gcc-only` (matching existing `Empty_struct*` descriptors), explicit `--gcc --64 --little-endian`, typed reads from fully initialized storage, and preserve nonzero payload assertions; the interior-`int` case provides aligned union storage and target layout assertions. The negative companion expects the named nonzero-field assertion failure. `zst-bits2expr-memcpy` is a distinct positive control. Test execution and compiler validation were not performed.

A zero-width element array with very large constant count still creates O(N) operands while consuming zero bits; this is an accepted bounded-scope risk, not addressed by this patch. Add the risk to the type audit/CI handoff and keep runtime sizes bounded in tests.

## NOT_RUN

No compilation, formatter, unit test, regression test, CBMC run, or runtime oracle was executed, per task restrictions. Findings are static source review only; no claim of compiled or verified behavior.

## Main-agent disposition

No source change for the Low invalid-count edge: the same checked size_t conversion
already precedes the old guard and fails on the same malformed type at the base.
The existing constant-count/convertibility precondition is now explicit in
TYPE-AUDIT.md; invalid negative count is not optional-failure supported input.
The reviewed source SHA is unchanged. No critical or valid-source blocker remains
from this static review. Formatting/compiler/runtime validation remains NOT_RUN.
