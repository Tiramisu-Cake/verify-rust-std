# PR5183 named retention and minimal edits

Pinned source19a42e1a21ae6f079cf68637782b4f16c345816b; T = tests/script-based-pre/autoharness_uninit_reset/. Native outcomes are source intentions. Keep both automatic targets and both independent invocations. No test removal, merge, helper framework or additional native run is proposed.

## Every changed file

| File | Recommendation |
| --- | --- |
| `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs` | KEEP byte-exact. KaniIntrinsic import, automatic intrinsic branch and current wrapper/DefId comment are justified. Preserve manual-harness fallback, setup insertion helper and unrelated upstream imports/content. |
| T `config.yml` | KEEP EXACT. Script run.sh and expected expected are necessary exec-suite registration. |
| T `main.rs` | KEEP EXACT. One repr(C) layout and two ordinary functions supply the genuine bad/good automatic-entry discrimination. No manual #[kani::proof] attributes. |
| T `run.sh` | KEEP EXACT, executable. Exactly two filtered regular-output commands, strict first exit1, second exit0 through set -e. No merged invocation, unconditional success fallback or generic command wrapper. |
| T `expected` | KEEP its six current lines; add two exact generated-target banners as shown below. This is a nonblocking named-oracle improvement, not a change to intended outcomes. |

## Every Rust helper/automatic target

| Symbol | Preserved obligation |
| --- | --- |
| `Bytes` | KEEP repr(C), a:u8 and b:u32. On standard CI targets offset1 is padding; both functions use this exact layout and offset. No second layout or duplicate struct is needed. |
| `uninit_read` | KEEP its local Bytes, raw const pointer and byte read at offset1. Generated automatic entry must expose the uninitialized read: exit1 plus semantic FAILURE/FAILED and 0/1/1 function summary. A missing setup must remain distinguishable. |
| `initialized_read` | KEEP its local mutable Bytes, raw mut pointer, in-place byte7 write at offset1 and subsequent same-pointer read. No intervening struct move/assignment. Generated entry must allow this initialized-byte read: exit0 plus SUCCESSFUL and 1/0/1 function summary. |

## Every relevant compiler/helper change

| Symbol / operation | Recommendation |
| --- | --- |
| `is_harness` new KaniFunction::try_from(instance) / AutomaticHarness branch | KEEP EXACT. Recognition uses the wrapper's retained intrinsic definition/marker, not the verified function's source attributes or its name. |
| `is_harness` existing proof/proof_for_contract fallback | KEEP EXACT. Manual paths retain their existing behavior. |
| `UninitPass::transform` | KEEP EXACT. Existing setup insertion precedes instrumentation and sets changed=true. |
| `inject_memory_init_setup` | KEEP EXACT. Select block0 first statement/terminator and insert initialization model call Before it. No new setup API or extra reset location is needed. |
| Existing `AutomaticHarnessPass`/Kani marker/model plumbing | KEEP all imported upstream content. AutomaticHarnessPass runs first, generated body retains intrinsic identity, and the initialization model nondeterministically selects tracked object/offset with value=false. |

## Complete invocation/oracle matrix

| Current probe | KEEP oracle |
| --- | --- |
| First `kani autoharness ... --include-pattern uninit_read ... main.rs` | Capture code in status, require exactly1. Demand named uninit_read banner, adjacent uninitialized-pointer FAILURE/description, FAILED and exactly0success/1failure/1function. Missing/multiple selection or a bare compiler error cannot replace the semantic result. |
| Second `kani autoharness ... --include-pattern initialized_read ... main.rs` | Plain final command under set -e requires code0. Demand named initialized_read banner, SUCCESSFUL and exactly1success/0failure/1function. Do not substitute an unrelated successful function. |

Current regexes are disjoint for the two exact function names; both targets have no arguments and no contract attributes. Regular output preserves visible verdicts and named banners. The driver prints automatic “functions” summaries; do not change them to manual “harnesses” totals. These are two separate Kani processes, not a same-process stale-state/reset test. Retain both commands and functions; sharing one source/layout is already minimal. Source-only zero-argument coverage does not establish native behavior of generated argument constructors or every automatic wrapper mode.

## Exact proposed expected file

Add the first and sixth lines below; retain all six existing lines byte-for-byte and in their current relative order:

```text
Autoharness: Checking function uninit_read against all possible inputs...
 - Status: FAILURE\
 - Description: "Undefined Behavior: Reading from an uninitialized pointer
VERIFICATION:- FAILED
Complete - 0 successfully verified functions, 1 failures, 1 total.
Autoharness: Checking function initialized_read against all possible inputs...
VERIFICATION:- SUCCESSFUL
Complete - 1 successfully verified functions, 0 failures, 1 total.
```

The matcher treats backslash-linked lines as adjacent substring requirements; other lines are separate file-wide requirements. The names strengthen the current filter/status/one-function-summary binding; they do not replace it or provide a native span proof. Avoid a JSON parser, new Python driver, captured-output framework or count-only reduction for this tiny fixture. Actual rendered output remains to be checked under separately authorized native validation.

No code/comment cleanup is needed: the wrapper identity comment and the two padding explanations describe non-obvious current behavior. PR prose changes are supplied separately in PROPOSED-PR.md: two substance paragraphs, one pending new full-standard-CI reference, retained #5162 historical CI context and exact license/disclosure. No implementation or publication is authorized by this edit table.
