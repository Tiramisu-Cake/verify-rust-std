# HANDOFF — independent PR 5159 cleanup review

**Verdict: APPROVE.** No required changes. One review stage complete; stop
with this HANDOFF. Approval covers the cleanup and local PR draft on static
evidence; native tests and CI remain **NOT_RUN**.

Reviewed candidate `282d007d06a2fc45ca6e6dc719a305f333b63a7c`, branch
`cleanup/pr5159-20261119`, in `/root/kani-pr5159-cleanup-w13`.
Its sole parent is the supplied PR head
`78f745bb696c85095a9582f959d4854ec494c4f5`; candidate tree is
`7a7103421211001791f2b01a5d06f3f5846e0b42`. The candidate worktree is clean.
Inspected the actual diff and emitting/matching source before consulting
the author's FINDINGS and original recommendation; did not adopt their
static checker or results as independent evidence.

## Byte preservation and scope

The complete diff is exactly five files: two `.expected` files each gain a
header and completion line, and three `.rs` files each replace only the
file-level comment at line 5. Independently compared each source byte after
restoring that one comment; everything else, including licenses, directives,
imports, types, attributes, assertions, internal comments and whitespace,
matches the parent. All eight proof functions are byte-identical:

| Source at candidate | Preserved harnesses (function start lines) |
| --- | --- |
| `tests/kani/Intrinsics/Volatile/load_zst.rs` | `read_volatile_unit_reference`:15; `read_volatile_dangling_unit`:20; `read_volatile_overaligned_zst`:26; `read_volatile_null_zsts`:32; `intrinsic_volatile_load_zsts`:39; `read_volatile_aggregate_zsts`:47 |
| `tests/expected/intrinsics/volatile_load/zst_unaligned.rs` | `misaligned_zst`:12 |
| `tests/expected/intrinsics/volatile_load/zst_uninhabited.rs` | `uninhabited_zst`:11 |

The entire compiler file
`kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs` is byte-identical,
SHA256 `09a6e3f017471549fc5c7a45471a321157339409c42a29471f0bd3f8f035bed7`.
Both original four-line reason bodies are byte-identical. Six positive
harnesses retain their success-mode source; the two negative cases retain
their separate sources and same-stem expected files. No harness or compiler
repair is needed for this cleanup.

## Every expected line traced to current source

All Kani file:line references below are relative to the candidate root and
refer to the pinned candidate, not an unpinned upstream version.

| Expected file line | Exact expectation and emitting code |
| --- | --- |
| Both :1 | `Checking harness misaligned_zst...` / `Checking harness uninhabited_zst...`. `kani-driver/src/harness_runner.rs:273` formats `Checking harness {}...`; :280 emits it, through :204–210 to stdout. Manual metadata uses `readable_name` at `kani-compiler/src/kani_middle/metadata.rs:25`, sets `is_automatically_generated: false` at :46, and `kani_middle/mod.rs:36–37` strips the local crate prefix. Both functions are at crate root, giving exactly the names above. Three literal periods, one space after each word; optional thread prefixes (:276–277) still allow substring matching. |
| Both :2 | `FAILURE` followed by a backslash in the expected file. `kani-driver/src/cbmc_output_parser.rs:395` renders failure as `FAILURE`; `cbmc_property_renderer.rs:335` emits `\t - Status: {status}\n`. The backslash is matcher syntax, not printed text; it requires the next expected line on the immediately following output line. |
| `zst_unaligned.expected`:3 | `` `src` must be properly aligned ``. `kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs:1925–1929` supplies exactly this message to a SafetyCheck. `codegen/assert.rs:139–143` passes it to the assertion; `cprover_bindings/src/goto_program/stmt.rs:188–200` preserves it as the property message/location. `kani-driver/src/cbmc_property_renderer.rs:336` prints `\t - Description: "{description}"\n`, immediately after Status (:338–340). Backticks, spaces and spelling match; surrounding label and quotes are allowed by substring matching. |
| `zst_uninhabited.expected`:3 | `volatile load of an uninhabited type has undefined behavior`. Both `intrinsic.rs:98–101` (no MIR return target) and :1935–1938 (returning path) provide exactly this SafetyCheck message. `codegen/assert.rs:214–231` implements the fatal-error wrapper as assert-assume-false, not a compiler abort. The same assertion-message and Description rendering path above applies. `cbmc_property_renderer.rs:642–658` leaves descriptions without matching rewrite alternatives intact. This review establishes both source routes, not which route the native harness exercises. |
| Both :4 | `Failed Checks: ` followed by the respective exact reason above. `kani-driver/src/cbmc_property_renderer.rs:406–408` processes failed properties; :482 emits this line without trace information, and :499 emits the identical first line when source information is available. Capitalization, colon and single separating space match in both branches. |
| Both :5 | `VERIFICATION:- FAILED`. `kani-driver/src/cbmc_property_renderer.rs:415–418` chooses `FAILED` for a non-success result; :432 emits `\nVERIFICATION:- {verification_result}{should_panic_info}\n`. These ordinary proof harnesses have no should-panic suffix. The colon immediately precedes the hyphen, with one space before `FAILED`. |
| Both :6 | `Complete - 0 successfully verified harnesses, 1 failures, 1 total.`. `kani-driver/src/harness_runner.rs:309–317` partitions manual results and counts success/failure/total; :337–340 prints exactly this template for a nonzero total. Each source contains exactly one manual harness, so a completed intended failure gives 0/1/1. Preserve plural `failures` even for 1, spaces around the hyphen, both commas and the final period. `kani-driver/src/main.rs:223–226` prints the summary before `conclude`; `harness_runner.rs:380–386` then exits 1 for failure. |

The negative sources specify only edition 2021, without quiet, autoharness,
output-format or filtering directives. `tools/compiletest/src/runtest.rs:349–370`
invokes each source separately. Default output is Regular
(`kani-driver/src/args/mod.rs:531–533`); `call_cbmc.rs:589–601` consequently
enables individual property rendering. Thus these are the exact strings
the current source emits for the intended completed failures. No runtime
transcript was collected or claimed.

## Oracle strength and static checks

`tools/compiletest/src/runtest.rs:488–499` selects each same-stem expected file.
At :530–535 it concatenates stdout/stderr and splits on newline. At :564–586
it collects backslash-linked consecutive lines; at :591–597 it searches any
window whose output lines contain the trimmed expected strings. Independent
blocks are not ordered, and output labels, quotation marks, indentation and
extra lines are allowed. Internal spelling, punctuation and spaces still
matter. This explains why bare `FAILURE` followed by a bare reason correctly
matches the consecutive Status/Description lines rather than requiring bare
lines in the actual output.

[review_static.py](review_static.py) is an independently written Python/Git
audit. [STATIC-CHECK.json](STATIC-CHECK.json) records PASS, the pinned tree,
compiler/proof hashes and preserved old-oracle hashes. It derives headers,
completion template and reasons from the emitting source, then exercises a
bounded port of the actual matcher with synthetic regular-format output.
Per negative file it accepts the ordinary and thread-prefixed variants and
rejects 13 variants: wrong reason at both or either diagnostic site, a reason
attached only to SUCCESS, broken Status/Description adjacency, wrong verdict,
wrong/missing harness, altered header punctuation, missing completion, wrong
counts, altered internal summary spacing and altered completion punctuation.
Four header/completion counterexamples still pass the old oracle and fail
the candidate oracle, demonstrating the additions' benefit. Wrong-reason
substitution already failed the old oracle; the cleanup preserves that
specificity while adding harness identity and completion requirements.

Limit: the matcher accepts complete intended output followed by an extra
synthetic error tail. It does not enforce an exact process exit code or a
unique failure reason, nor prove crash-freedom. Expected mode checks process
success only when `require_success` is enabled (:497–499;
`tools/compiletest/src/common.rs:156–158`). This existing limitation does not
invalidate the strengthening. Native outcome/MIR-route/proof credit remains
unestablished. `git diff --check` also passes.

## Comment and PR-draft review

The three comment replacements lose no needed information. The positive
header retains #5072 and describes the accepted pointer cases; the detailed
no-memory-access rationale remains in `intrinsic.rs:1933`, with the original
alignment/value checks and test bodies intact. The alignment header states
the requirement tested by align(8) Z at address 1. The uninhabited header
states the safety-diagnostic requirement; the empty enum and exact expected
reason retain its explanation. No implementation TODO or in-harness
explanation was removed.

`../pr5159-cleanup/PR-BODY.md` is accurate and concise as written. It explains
the original failure, typed inhabited-ZST construction after alignment,
uninhabited handling including the no-target source route, eight harnesses,
and the stronger negative oracles. It makes no claim that both MIR routes
were observed. The pending native/CI sentence correctly limits validation;
historical platform/CI bookkeeping is gone. `Resolves #5072` remains. The
license and AI disclosure lines are each byte-for-byte identical to the
pinned original body and occur exactly once. Draft SHA256:
`b5f43b9da9f92c6cb05f324adfb98b043ea680a0548da009f74dd7b412068a4c`.
No draft edits are requested.

No cargo, rustc, Kani, CBMC, native test, CI, push, PR mutation, raw evidence
retrieval, coordinator/ledger change or subagent was used. Only this review
package is written and committed, with `[skip ci]` as
`Tiramisu-Cake <igkharin@gmail.com>`; its containing SHA is reported separately.
Any native validation or publication requires a separately authorized stage.
**HANDOFF; no further stage started.**
