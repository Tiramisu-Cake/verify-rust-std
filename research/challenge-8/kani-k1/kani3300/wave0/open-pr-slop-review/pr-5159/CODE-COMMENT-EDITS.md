# Proposed code/comment edits

Keep the implementation structure. The new returning/non-returning ZST guards belong to different dispatch paths. The alignment check, typed Expr::init_unit construction, non-ZST dereference and two SafetyCheck diagnostics stay. No helper, trait, parameterized test or abstraction is needed to share these few lines.

| Exact changed location | Proposed edit | Reason |
|---|---|---|
| intrinsic.rs:91, new non-returning volatile_load comment | `// Diagnose uninhabited ZST loads on the non-returning intrinsic path.` | Describes current dispatch without diff-oriented “even when” framing. Keep the return-type ZST/uninhabited guard and SafetyCheck class. |
| intrinsic.rs:1933, new ZST comment | `// ZST loads require alignment and an inhabited result.` | Captures both required conditions directly. Keep the alignment check before result construction and both branches of the inhabited check. |
| load_zst.rs:5, regression comment | `// Volatile loads of inhabited ZSTs accept aligned reference, dangling and null pointers (#5072).` | Describes the actual coverage and preserves the real issue link. Keep the exact unit-reference reproducer and every typed equality assertion. |
| load_zst.rs:40, direct-intrinsic comment | Delete only `// Exercise lowering directly as well as through the public API.` | The function name and calls already identify direct intrinsic coverage. Keep the function and both assertions. |
| zst_unaligned.rs:5, test comment | `// An over-aligned ZST requires an aligned source address.` | Explains why address1 is a meaningful negative without a contrast clause. |
| zst_uninhabited.rs:5, test comment | `// Loading an uninhabited ZST requires a safety diagnostic.` | Describes the current expected behavior instead of saying “Preserve the diagnostic”. Keep the exact message in the expected file. |

Retain the corrected non-ZST “valid for reads” documentation. Retain the initialized-value TODO and its #920 link: this PR handles inhabited zero-sized construction, not general non-ZST initialization. Preserve all unmodified upstream comments, copyright/license lines, unaligned-load/store code and other intrinsic models. Do not replace the common operand conversion/alignment path with an early ZST return, add a non-null check, or merge the non-returning case into code that expects a result Place.
