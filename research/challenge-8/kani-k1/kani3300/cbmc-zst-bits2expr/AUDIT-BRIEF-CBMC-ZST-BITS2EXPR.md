# External audit brief: CBMC zero-width array reconstruction

2026-11-13. Review before a proposed PR to `diffblue/cbmc`, targeting `develop`.
This is correctness verification, not security work.

## 1. Purpose and exact review target

We request an independent assessment of a small CBMC conversion fix and whether its tests and publication texts are sufficient. The auditor needs no prior Kani context. No CBMC issue or PR has been published in the supplied coordination state; publication remains the owner's decision.

- Clean candidate: [cd41a5c74b0c42edf4f08834b3e2808dd3344cab][fix], one commit on [develop 107a1e504cd69a2f3483717c8bcfcfa59814c557][base]. Candidate tree: `92c03401d6c2a6da069670260244bc021bbdba99`.
- Production delta: one comparison in [`src/util/simplify_utils.cpp`][converter], from `*el_size_opt > bitst{0}` to `*el_size_opt >= bitst{0}` in the array branch of `bits2expr`.
- The same commit adds 13 regression directories and three Catch test cases in [`unit/util/zst_bits2expr.cpp`][unit]. Overall: 28 files, 629 insertions and one deletion; most lines are tests.
- CI-only commits delete inherited workflows and add the owner's bounded workflow/scripts. They are **not** the proposed PR source. In particular, do not submit `91062c7dba` or `b794c3c99d` as the PR head.

This brief checks source and recorded summaries. It does not claim new execution or independent rereading of raw CI artifacts. The [coordinator's CI record][results] and [readiness assessment][readiness] preserve evidence qualifications and later corrections.

## 2. Origin: a Kani backend failure reduced to C

Kani translates Rust into CBMC's GOTO representation and uses CBMC for verification. While addressing its union code generation, our B3 work found that copying an aggregate containing an array of zero-sized elements can abort CBMC rather than produce a verification result.

The [Kani workaround 6e9e782024][kani-b3] handles a padded union arm whose Rust layout is zero-sized: it uses an empty-struct representation for that arm, based on Rust layout rather than recursive backend `sizeof`. This avoids particular inputs; it does not repair general CBMC reconstruction. A nonzero-width arm with an internal ZST array, such as `Tail { u8, [(); 2] }`, remains outside that workaround.

[Kani issue #5085][kani-5085] reports the same invariant for a `static`/`const` containing `[[u8; 0]; 2]` alongside a nonzero byte. That is related input and a future integration target, not evidence that our CBMC commit already fixes the actual Rust/Kani reproducer.

An independent C reduction uses the GNU C empty-struct extension:

```c
#include <string.h>
struct E {};
struct W { struct E z[2]; char pad[8]; };

int main(void) {
  char buf[8];
  memset(buf, 0x5a, sizeof buf);
  struct W w = *(struct W *)buf;
  __CPROVER_assert(w.pad[0] == 0x5a, "copied");
  return 0;
}
```

Command used by the proposed issue text:

```sh
cbmc --gcc --c11 --64 --little-endian --validate-goto-model --validate-ssa-equation repro.c
```

On CBMC 6.11.0 the historical [fork Kani CI run 43241563566][c-repro-run] reproduced exit 134 at `src/util/simplify_utils.cpp:345`, `bits2expr`, condition `el_size_opt.has_value() && *el_size_opt > 0`. Union-copy and an empty-array-plus-integer case reached the same invariant; a `memcpy` control passed. The [original C reduction record][origin] predates this CBMC patch. The same positive-width restriction is present on the pinned develop base; paired develop/fix evidence is below.

These tests concern CBMC's GNU C model, not an ISO C guarantee for empty structs. Please assess the reproducer's typing/alignment and the strength of the controls as part of review.

## 3. Root cause and why the proposed change may be sufficient

`bits2expr(bits, type, little_endian, ns)` reconstructs a typed expression from a memory-order bit string. See the [complete converter][converter], [width computation][widths] and [source map][source-map].

1. Entry validation requires a known whole-type width. Non-unions require exactly that many input bits. Unions retain their existing rule permitting a shorter slice than the whole union width. These checks are unchanged.
2. A struct is reconstructed component by component. Its component-width check already accepts known zero width. An empty struct can be rebuilt as a typed empty struct expression from an empty bit string. Its offset increment is zero, preserving the start of the next nonzero field.
3. Array width is element width multiplied by constant element count. The array branch still requires a constant count convertible to `size_t`, reserves that many operands, and loops over the finite count. Previously its positive-width check rejected a valid zero-width element before recursion could reconstruct it.
4. With width zero, `i * el_size` and `el_size` are both zero. Each recursive call receives the empty slice, and each successful result is appended with its type intact. Progress comes from the finite count and descent through the type, not from consumption of bits. Nested arrays retain both levels' counts; there is no division by element width or width-controlled loop here.
5. `expr2bits` already concatenates aggregate operand strings, including empty strings. No change to that direction or to byte-operator lowering is proposed. Unit round trips check this composition and preservation of neighboring payloads.

The change retains `has_value()` and the nonnegative check before casting the width. Unknown/negative element widths are still rejected, and positive-width inputs follow the old code. Unsupported recursive element conversions can still return no expression. The candidate does **not** declare every possible zero-bit type valid.

Tags follow namespace definitions and restore the requested tag. Union conversion still selects the first reconstructible member under its existing width rules; the new unit case checks a too-small first arm followed by a wrapper with zero-width members. Vector and complex branches keep their positive-width guards. This is an array-only admission change, not a general relaxation of aggregate invariants.

### Other callers and unproved edges

The converter is shared infrastructure, not Kani-specific. Direct production callers include:

- Constant [`byte_extract` and `byte_update` simplification][byte-callers]. This explains why a typed aggregate copy can reach reconstruction. An empty outer result may use a separate simplification path; the reproducer's whole wrapper is nonempty.
- [`union` member simplification][union-caller].
- Constant [`extractbits` and `bitreverse` simplification][int-callers].

Recursive callers include enums/tags, union members, struct members, arrays, vectors and complex parts. We found no direct call in `lower_byte_operators.cpp`; that does not establish coverage of every indirect lowering path.

Source reasoning supports the local change; broad safety is the audit question. Missing/negative widths are not newly exercised by dedicated tests. Very large constant counts of zero-width elements can require many expression operands despite zero aggregate bit width; no resource-policy change is included. Malformed or cyclic by-value types are not newly supported. No claim is made about arbitrary zero-width vector/scalar forms, all padding conventions, or every language frontend.

## 4. Added tests and their exact meaning

All new regression cases are [under `regression/cbmc/zst-bits2expr-*`][regressions], with a `main.c` and `test.desc` in each directory. Their descriptors select `CORE gcc-only` and `--gcc --64 --little-endian`; they do not themselves specify C11 or model/SSA validation flags. The separate reproducer command above must not be confused with these descriptor flags.

| Directory suffix | Intended coverage |
|---|---|
| `deref` | Typed dereference after filling bytes; checks all eight payload bytes |
| `union` | Typed union copy with a nonzero wrapper containing the zero-width array |
| `interior` | Nonzero prefix/suffix and a zero-width field at an interior offset |
| `count-0`, `count-1`, `count-2` | Array operand counts zero, one and two |
| `position-first`, `position-middle`, `position-last` | Zero-width field position among nonzero fields |
| `nested` | Nested arrays of empty elements |
| `zero-length-inner` | Nonempty outer array of zero-length arrays of nonzero bytes |
| `memcpy` | Existing-behavior control that avoids the failing typed-copy path |
| `negative` | Deliberately wrong payload assertion: verification must fail for that assertion |

Thus **13/13 oracles met** does not mean 13 successful verification verdicts: the negative case must produce its intended failure. Its name does not denote a negative-width test.

The three [focused utility cases][unit] exercise both byte orders:

1. Empty structs and arrays with counts 0/1/2: exact types, operand counts, empty round trip, and rejection of surplus input bits.
2. Nested arrays over empty structs and over a zero-length byte array: exact nested shapes and round trip.
3. Tagged empty elements, nonzero siblings, a union reconstruction, exact payload values and bit round trips.

The [historical test manifest][test-manifest] records the original planned inventory, not final execution status; use the later CI record for outcomes. The source-only [type audit][type-audit] is not a substitute for the subsequent CI compilation.

## 5. Recorded fork CI evidence

### Paired run r2: 43334186094

[Run 43334186094][r2], Ubuntu 24.04, GCC 13, CMake Release, MiniSat2. CI-only head [`91062c7dba9da7541c0e607a3735482e38d28d36`][r2-ci] includes source candidate `cd41a5c74b` plus workflow scaffolding. Baseline is develop `107a1e504c` with the same new test bytes and without the one-line production fix.

| Selection | Baseline + tests | Candidate |
|---|---|---|
| Build | Built | Built |
| 13 focused regression directories | 12 hit the array invariant; `memcpy` passed | 13/13 specified oracles met, including intended negative |
| 13 neighboring directories, 14 descriptors | Not run | All specified oracles met |
| Three focused utility cases | Not run | 3/3 passed |
| Other selected util cases | Not run | 205/212 passed; seven Z3 subprocess failures |
| Separate literal C and Kani-like C fixtures | Array invariant | Verified, according to the coordinator's later result |

Neighbors: `Array_Initialization1/2`, `Array_Propagation1`, `Array_Access1`, `Empty_struct1/2/3`, `Struct_Bytewise1`, `byte_extract1` (two descriptors), `empty_compound_type2/3/4`, `union-unequal-element-size1`. Existing descriptors include expected-failure oracles; this is not a claim that every neighbor program verifies.

The initial CI record still says the separate fixture summary needs checking. The [later readiness record][readiness] explicitly incorporates the coordinator's confirmation; we preserve that provenance rather than silently treating the stale line as independent evidence. A Kani-like C fixture is **not an actual Kani replay**.

Earlier attempts failed in scaffolding: one test-delta identity/format check failed; r1 run 43330853783 later died with SIGXFSZ during `ar` because a build file-size limit was applied. For r2, the coordinator removed that limit from build steps and allowed an empty formatter diff to mean clean. These repairs are outside the PR source; they do not represent changes to the production fix or a successful full regression suite.

### Z3 follow-up: 43341504085

[Run 43341504085][z3-run], CI-only [`b794c3c99dd2855bf99a466a59e779ee8d17d560`][z3-ci], kept the same clean candidate source and installed Ubuntu Z3 4.8.12; preflight passed. Selection `[util]~[zst-bits2expr]`: **210/212 passed**. The seven earlier Z3 failures disappeared. Two subprocess error-handling cases remained:

- `Creating a sub process with a binary that doesn't exist`, `unit/util/piped_process.cpp:72`: expected error text not found.
- `Scenario: run() error reporting`, `unit/util/run.cpp:45`: expected `result != 0`, observed 0.

These cases do not call `bits2expr`. However, baseline util was not run: **pre-existing failure status on develop is not established**, and environment/harness attribution remains an inference. We do not claim a complete util PASS. The PR Testing section currently reports focused results only; the full partial-util record remains available to the auditor.

## 6. Checks not performed and publication boundaries

- No full `regression/cbmc` or full CTest regression matrix; no macOS or other-platform run.
- No actual Kani replay of B3, its nonzero-arm/internal-ZST limitation, or #5085 using the patched CBMC. Do not claim those issues resolved or remove the Kani workaround on this evidence alone.
- No paired baseline utility run, and no dedicated negative/unknown-width utility tests.
- No CI on a rebased/current develop tree. The [later preparation record][prready-inputs] observed develop `37a17adc07f29e1127f100debf1d8eea00532a24`, two commits ahead of the tested base, with no overlapping source paths; that was source-only mergeability evidence, not a new CI result or a claim about today's latest develop.
- No runtime/performance improvement claim. Large zero-width counts and unrelated callers have not been stress-tested.

The owner will decide whether any additional checks are prerequisites for publication or can be left to normal upstream PR CI. This brief authorizes neither new CI nor issue/PR publication.

## 7. Repository policy and proposed texts

Pinned upstream guidance: [AGENTS.md][agents], [CODING_STANDARD.md][coding], [PR template][pr-template], [issue template][issue-template]. AGENTS is an assistant development guide; it contains no prohibition on AI assistance. Its build/test examples do not override our project rule that compilation and verification happen only in owner-run fork CI.

The proposed PR targets `develop`, contains one bug fix, and places regression/unit tests in the same commit as the fix. Its commit message has a nonempty explanatory body. No new production procedure or CLI is introduced. The draft explains why no User Guide change or performance data is proposed; whether that satisfies the template is an audit question. Changed lines are subject to clang-format; the pinned coding standard/CI uses **18.1.8**, rather than any arbitrary version 18. CI-only workflow deletion must not enter the submitted source delta.

Review the exact proposed [issue text][issue-draft] and [PR text][pr-draft]. The issue follows the repository's version/OS/command/expected/actual structure. The PR separates problem, cause, change and targeted testing. Both include the owner's disclosure line:

*Disclosure: this change and description were prepared with the help of AI assistants.*

No issue number has been invented. If a separate issue is opened, its real reference can be added before the PR. A fresh duplicate/base check belongs to the publication decision, not to the historical evidence claims here.

## 8. Questions for the independent auditor, in priority order

1. Is `>= bitst{0}` the correct minimal semantic boundary for **arrays**? Does the finite recursive reconstruction preserve count, type and neighboring payload bits for every admitted zero-width element, without weakening necessary invariants?
2. Are entry-width validation, the retained unknown/negative checks, and the unchanged vector/complex restrictions sufficient? Is there a valid zero-width type that reaches a recursive branch unable to reconstruct it, or a newly exposed invariant failure requiring a narrower condition?
3. Review other callers: can union member selection, byte extraction/update, extractbits or bitreverse now return a wrong expression rather than merely avoiding an abort? Are `expr2bits` round trips enough, or should any caller have a direct regression?
4. Is the C reproducer sound under CBMC's GNU C model, including effective type/alignment, and do the IR utility tests independently establish the intended semantics? Are constant folding or vacuous checks hiding any regression's useful path?
5. Are the 13 regression directories and three utility cases sufficient? Which missing edge, if any, is necessary before publication: tagged arrays, negative/unknown width, nested layouts, zero-count arrays, union arm order, or very large zero-width counts? Should test duplication be reduced?
6. Is the intended-negative oracle specific enough to rule out accidental success or an unrelated failure? Does each baseline invariant failure and fixed oracle support the claimed differential result?
7. What additional execution, if any, is a prerequisite for a CBMC PR: full `regression/cbmc`/CTest, paired util baseline, macOS, or selected wider callers? Please distinguish required checks from useful upstream CI coverage.
8. Do the two remaining subprocess failures require a paired baseline run before submission, or is explicit disclosure with focused-only Testing appropriate? We have not established their pre-existing status.
9. Is actual Kani replay needed before the CBMC PR, or only before claiming B3/#5085 fixed and retiring a Kani workaround? Which minimal integration cases would give useful additional confidence?
10. Is the one-commit scope appropriate, and do the commit body, formatting, documentation treatment and PR checklist comply with repository policy? Should any test-only material or narrative be shortened?
11. Are the issue/PR drafts factually precise and appropriately scoped, especially GNU C support, the two CI selections, expected failure, and unperformed checks? Please identify concrete unsupported claims rather than assume full-suite success.
12. Should we file a standalone CBMC issue with the minimal reproducer first, or submit only the PR with that reproducer and Kani #5085 as background? Are duplicate checking or maintainer questions needed before either action?

[fix]: https://github.com/Tiramisu-Cake/cbmc/commit/cd41a5c74b0c42edf4f08834b3e2808dd3344cab
[base]: https://github.com/diffblue/cbmc/commit/107a1e504cd69a2f3483717c8bcfcfa59814c557
[converter]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_utils.cpp#L196-L409
[widths]: https://github.com/diffblue/cbmc/blob/107a1e504cd69a2f3483717c8bcfcfa59814c557/src/util/pointer_offset_size.cpp#L104-L218
[unit]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/unit/util/zst_bits2expr.cpp
[regressions]: https://github.com/Tiramisu-Cake/cbmc/tree/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/regression/cbmc
[byte-callers]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_expr.cpp#L1888-L2246
[union-caller]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_expr_struct.cpp#L188-L216
[int-callers]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_expr_int.cpp#L1207-L2127
[kani-b3]: https://github.com/Tiramisu-Cake/kani/commit/6e9e782024a19f93bf3b89ede89960bf2d9419cc
[kani-5085]: https://github.com/model-checking/kani/issues/5085
[c-repro-run]: https://github.com/Tiramisu-Cake/kani/actions/runs/43241563566
[origin]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d377f342f49b2e39498745198df73f4d1999a593/research/challenge-8/kani-k1/kani3300/b3p/ISSUE-DRAFTS.md
[r2]: https://github.com/Tiramisu-Cake/cbmc/actions/runs/43334186094
[r2-ci]: https://github.com/Tiramisu-Cake/cbmc/commit/91062c7dba9da7541c0e607a3735482e38d28d36
[z3-run]: https://github.com/Tiramisu-Cake/cbmc/actions/runs/43341504085
[z3-ci]: https://github.com/Tiramisu-Cake/cbmc/commit/b794c3c99dd2855bf99a466a59e779ee8d17d560
[results]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/fe46f9f7db4790cf4702ce1ca40ef4422e68f32e/research/challenge-8/kani-k1/kani3300/cbmc-zst-bits2expr/CI-RESULT-R2.md
[readiness]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/fe46f9f7db4790cf4702ce1ca40ef4422e68f32e/research/challenge-8/kani-k1/kani3300/cbmc-zst-bits2expr/PR-READINESS.md
[source-map]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/fe46f9f7db4790cf4702ce1ca40ef4422e68f32e/research/challenge-8/kani-k1/kani3300/cbmc-zst-bits2expr/SOURCE-MAP.md
[test-manifest]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/fe46f9f7db4790cf4702ce1ca40ef4422e68f32e/research/challenge-8/kani-k1/kani3300/cbmc-zst-bits2expr/TEST-MANIFEST.json
[type-audit]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/fe46f9f7db4790cf4702ce1ca40ef4422e68f32e/research/challenge-8/kani-k1/kani3300/cbmc-zst-bits2expr/TYPE-AUDIT.md
[prready-inputs]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/fe46f9f7db4790cf4702ce1ca40ef4422e68f32e/research/challenge-8/kani-k1/kani3300/cbmc-zst-bits2expr/prready/INPUTS.json
[agents]: https://github.com/diffblue/cbmc/blob/107a1e504cd69a2f3483717c8bcfcfa59814c557/AGENTS.md
[coding]: https://github.com/diffblue/cbmc/blob/107a1e504cd69a2f3483717c8bcfcfa59814c557/CODING_STANDARD.md
[pr-template]: https://github.com/diffblue/cbmc/blob/107a1e504cd69a2f3483717c8bcfcfa59814c557/.github/pull_request_template.md
[issue-template]: https://github.com/diffblue/cbmc/blob/107a1e504cd69a2f3483717c8bcfcfa59814c557/.github/issue_template.md
[issue-draft]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/fe46f9f7db4790cf4702ce1ca40ef4422e68f32e/research/challenge-8/kani-k1/kani3300/cbmc-zst-bits2expr/ISSUE-CBMC-ZST-BITS2EXPR-DRAFT.md
[pr-draft]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/fe46f9f7db4790cf4702ce1ca40ef4422e68f32e/research/challenge-8/kani-k1/kani3300/cbmc-zst-bits2expr/PR-CBMC-ZST-BITS2EXPR-DRAFT.md
