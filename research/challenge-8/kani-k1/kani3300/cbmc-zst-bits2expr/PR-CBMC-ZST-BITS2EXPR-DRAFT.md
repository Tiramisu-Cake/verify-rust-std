<!--
Draft only; no PR opened. Target: diffblue/cbmc develop.
Clean source: cd41a5c74b0c42edf4f08834b3e2808dd3344cab, parent107a1e504cd69a2f3483717c8bcfcfa59814c557.
Do not use CI-only33235a4ef1/91062c7dba as the PR head. Source has no workflow changes.
Before publication, owner checks current develop/mergeability and fills an actual issue reference if one is filed.
Testing below describes run43334186094. Z3 util follow-up is pending; do not mark it passed in advance.
-->

**Title:** Allow bits2expr to reconstruct arrays of zero-width elements

`bits2expr` aborts when a typed copy of a nonempty struct reaches an array of GNU C empty structs. Struct conversion accepts zero-width components, but array conversion requires a strictly positive element width.

Accept a known nonnegative array element width. The existing loop reconstructs zero-width elements from empty slices, preserving their types and count without consuming bits belonging to neighboring fields. Unknown and negative widths remain rejected.

The regression tests cover typed copies, unions, interior and first/middle/last zero-width fields, nested arrays, zero-length arrays, payload preservation and a `memcpy` control. Utility tests check exact types/counts, tagged elements, nonzero siblings and round trips in both byte orders.

### Testing

- [Fork CI](https://github.com/Tiramisu-Cake/cbmc/actions/runs/43334186094), Ubuntu 24.04 / GCC 13, source `cd41a5c74b`: all 13 focused regression oracles, 13 neighboring regression directories and all three focused utility cases passed. The focused set includes one intended assertion failure.
- With identical tests on develop `107a1e504c`, 12 focused cases hit the array invariant; the `memcpy` control passed. The separate literal C reproducer and Kani-like C fixture also changed from invariant failure to successful verification.
- The remaining utility selection passed 205/212 cases. Seven Z3-dependent subprocess tests did not pass on a runner without Z3; a rerun with Z3 is pending. Full regression, other platforms and actual Kani replay have not been run.

### Checklist

- [x] The commit body explains why the change is needed.
- [x] Documentation of added production procedures: not applicable; none added.
- [x] User Guide update: not proposed for this internal conversion bug fix; no new CLI or language construct is introduced.
- [x] Regression and unit tests are included in the bug-fix commit.
- [x] Performance data: not applicable; no performance improvement is claimed.
- [x] This PR contains one bug fix.
- [x] No unrelated whitespace or formatting changes are included.

*Disclosure: this change and description were prepared with the help of AI assistants.*
