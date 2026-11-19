# PR9487 — retain the fix and coverage; repair the regression descriptor

Recommendation: **CHANGES_RECOMMENDED**, limited to the regression descriptor and concise explanatory text. Keep the production change and all three new unit cases. One concrete test-oracle defect is established statically. No production correctness defect was found within the reviewed expression/type paths; native validation remains pending.

Reviewed diffblue/cbmc#9487 at head `9f2d01ec2bf115879c86e22203d403ba156d22e5`, tree `00ef6af1359f247f574bbfab6e6a514442118ba9`, against connected-confirmed merge base `107a1e504cd69a2f3483717c8bcfcfa59814c557`. All four file blobs, byte counts, SHA256s, source diff and body digest match root's task commit `98784e2ade6135d3177b0ad14c9ab88777ab6aa2`. Current upstream base `57c8ad710ee2f581895478ff4645cebec2f53c49` is metadata only and absent locally. No comparison against its unobserved source or fresh CI success is claimed.

## Finding F1 — P2: EXIT=0 is consumed as a header field

`regression/cbmc/byte_extract_empty_struct_array/test.desc:4` contains `^EXIT=0$`. At head, `regression/test.pl:135–136` unconditionally consumes four header fields: level/tags, input, options, and grep_options. Consequently the required patterns start with `^SIGNAL=0$`; EXIT=0 is never matched. The `-e` loader check at lines127–129 only checks that EXIT/SIGNAL strings occur somewhere in the descriptor. It does not repair their position. `run` at lines82–114 appends the actual exit/signal and ordinarily returns success independently of a nonzero exit; only matching the result patterns rejects that exit.

For example, the synthetic output `VERIFICATION SUCCESSFUL`, `EXIT=7`, `SIGNAL=0` satisfies the current evaluated patterns. Insert a blank fourth line so all three required patterns are evaluated. STATIC-CHECK.json records a seven-case bounded Python model of these inspected parsing/matching rules: that synthetic nonzero-exit case changes from accepted to rejected, while success remains accepted and signal/invariant/warning/failed-verification cases remain rejected. The Perl driver and CBMC were not executed.

This is an incomplete exit oracle, not evidence that the current test accepts the original invariant abort: the invariant remains explicitly forbidden and the verification-success marker remains required. The fix strengthens the descriptor while retaining its meaningful success and diagnostic checks. No driver-wide change or new test framework is needed.

## Finding F2 — P3: shorten historical descriptor/PR narration

The descriptor's lines11–14 narrate the previous failure and compare implementation branches. Replace them with a current-behavior description of the aggregate and its surrounding bytes, as given in CODE-COMMENT-EDITS.md. Preserve its tag, options, required verdict, forbidden warning/invariant patterns and existing source comment about the GNU C extension.

The PR body repeats the whole29-line fixture, an invariant report, implementation details, a long platform matrix, Maven failure history and formatting history. A reviewer can find the fixture and tests in the diff. SUGGESTED-PR.md retains the concrete trigger, recursive typed reconstruction, real related Kani issue and AI disclosure, uses CBMC's actual checklist, and leaves one standard-CI placeholder for the final cleanup revision. Historical native/CI statements in the original body remain author-reported, not validation performed by this review. Its statement that there is no user-visible behavior is too broad for a crash fix; describe the lack of new API/options instead.

## All changed files

| File | Disposition | Reason |
|---|---|---|
| `src/util/simplify_utils.cpp:345` | KEEP the one-line `>0` to `>=0` edit | Known zero width is compatible with recursive reconstruction. Positive widths, known-width check, size conversion, count and type construction remain unchanged. |
| `unit/util/simplify_expr.cpp:113–217` | KEEP all three new TEST_CASEs and their oracles | Cardinality, recursive shape, tags, struct/union embedding and nonzero siblings are distinct properties. No new helpers/framework or generated test matrix was introduced. |
| `regression/cbmc/byte_extract_empty_struct_array/main.c` | KEEP | One29-line frontend-to-simplifier success regression; meaningful byte assertions on both sides of the empty-array member. GNU C source comment is useful. |
| `regression/cbmc/byte_extract_empty_struct_array/test.desc` | FIX F1 and shorten final comment | Blank line restores the intended EXIT oracle. Preserve the GNU/MSVC selection boundary and every positive/negative pattern. |

## Reconstruction and type invariants

`bits2expr` first checks known overall width and exact bit count for non-unions (`simplify_utils.cpp:202–213`). `pointer_offset_bits` multiplies array element width by constant count and sums struct component widths (`pointer_offset_size.cpp:103–156`). Both an array with zero elements and an array with nonzero count of zero-width elements therefore have zero total width, but their operand cardinalities differ.

At element width0, `std::string(bits,i*el_size,el_size)` is an empty substring at position0 for every element. The count-controlled loop still makes one recursive call and appends one result per element. `array_exprt({},array_type)` preserves the complete original array type. Empty structs reconstruct an empty typed operand list; struct-tag recursion restores the original tag type (`simplify_utils.cpp:293–330`). A nested zero-length ordinary-byte array instead reconstructs an empty array with its own array type. Recursive failure still propagates as no value. There is no new division by element width or loop bound based on bit consumption.

For positive widths, the comparison and all subsequent code have the same behavior as before. Unknown/negative widths are not newly accepted. Vectors and complex values retain their existing positive-width guards. No production special case, early return, synthetic empty placeholder or abstraction is needed. No modification of existing upstream comments/license text is recommended.

## Why retain these tests

The first unit case checks direct empty-struct recursion plus array counts0/1/2, exact array type, exact typed elements, empty round-trip and rejection of nonempty bits. A zero-element array alone cannot detect returning an empty array for every count: retain1 and2 as well. The direct struct control distinguishes failure of the recursive element case from failure of the new array allowance.

The nested case distinguishes two rows each containing three empty-struct elements from two rows each containing zero ordinary-byte elements. Both occupy zero bits; losing inner shape/type would still pass an empty-bit-string-only oracle. Keep the row/element checks and both inner types.

The tagged case checks namespace lookup and preservation of struct-tag types. Its distinct0x5a/0x12345678/0xa5 siblings and complete expected-expression equality detect offset/value corruption. The union has a deliberately too-small first member, so reconstruction must choose `w`. Keep both the struct and union checks and both endian directions. The asserted48 bits describe the explicit expression-level member widths, not a claim about padded native C struct layout.

The end-to-end C regression reaches byte-extract reconstruction through a typed constant read. Its uniform sentinel is adequate for the original abort and for preservation of the bytes on both sides; exact nonuniform sibling reconstruction is separately checked by the tagged unit case. Replacing this reported reproducer or generating more fixture directories is unnecessary. All three new unit cases and one regression directory should remain; line-count ratio to a one-line fix is not a defect.

## Discovery, platform and existing baselines

- New TEST_CASEs have `[core][util]` tags in the existing `unit/util/simplify_expr.cpp`. `unit/Makefile:208` includes that file; `unit/CMakeLists.txt:12,74,102–114` glob/build/register the unit binary with CORE labels. No registration or isolated-mode flag change is needed.
- `CORE gcc-only` is intentional for a GNU C empty-struct extension. `regression/cbmc/Makefile:6–14` and `CMakeLists.txt:1–12` exclude that tag for MSVC; it is not an instruction to compile/run with GCC during this review. Preserve the tag. The blank options line adds no weakening flags. Standard suite commands also validate goto/SSA structure.
- Existing `unit/util/simplify_expr.cpp:66`, TEST_CASE **expr2bits and bits2expr respect bit order**, checks ordinary32-bit scalar and bitfield reconstruction. Existing `unit/util/lower_byte_operators.cpp:25`, TEST_CASE **byte extract and bits**, checks conversion into16 ordinary one-bit array elements and lowering under both endiannesses. These are concrete preserved nonzero-width baselines at the pinned head/merge base, not newly executed tests.
- `regression/cbmc/empty_compound_type4` checks an empty struct in a union and intentionally contains a failing assertion. It forbids invariant/warning diagnostics, but has no array of empty structs and does not replace the new success regression. Its older descriptor also puts a pattern in the fourth field; no edit to that unrelated baseline is proposed here.

The test uses a complete empty struct, not an incomplete type or an array of void. `c_typecheck_type.cpp:577–605` distinguishes those unsupported types. The C fixture has byte-array siblings around the GNU zero-width member; it deliberately exercises supported target-specific byte reconstruction. No ISO-C portability theorem, fresh architecture/layout validation or C++-empty-class equivalence is inferred. Retain its GNU boundary instead of using an invalid-input/internal-abort golden.

## Scope and remaining validation

No unit case or assertion removal is recommended. The genuine confirmed gap is the missing EXIT oracle. Native compiler/unit/CBMC runs, final formatting checks and final standard CI remain unperformed. A later authorized cleanup should apply the local descriptor repair, preserve all tests, and validate the exact resulting revision. The original release6.11.0 abort and platform CI matrix are source-reported claims in the pinned PR body.

No source changes, C/C++ compiler, native test driver, CBMC, CI, push, PR/comment/issue or external draft writes, ledger/accounting, subagent, model or Fast changes occurred. CBMC's LICENSE and `.github/pull_request_template.md` govern the recommendation; no Kani Apache/MIT attestation is inserted. S4P2 intake and the independent W13 plan remain untouched.
