# W14 S2 r3 contract delta — APPROVE

Reviewed exact g0 `ba7286f5f77277aed531eaaab601e94396dec909`,
`kani3300/ch8-s2/batch-r3/`, under issued task
`task91cd41b3fdbffe36ed5d14806c390bf0b0c16bbb` (owner15:48).
No blocking findings. Approval covers the source-supported repair candidate and
its exact static integration. Compilation and causal repair remain unverified.
Original13 owns any source/composition repair; this review edits only its own
new directory. Historical packages and verdicts remain immutable.

| Pin | Exact value |
| --- | --- |
| Source | `478dbf10d3fccd1119f4de7ac596c96d6dbe8ade` |
| Source tree | `b5b25f4e59308df7b15340cae343f50ae9fd8a81` |
| Source sole parent | `97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a` |
| Source derivation baseline | `efb1aba7fc6445cba6cd75154713b598c9e2579d` |
| Control | `dc1ad0f9ce364f9a7efb2c3cc32db6ed51b6db4b` |
| Control tree | `1c199ee22001213c164ac0bb9c9b56c2e5f827df` |
| Control required sole parent | `9e14e033f9ee31522b571c127609dcdff76d230b` |
| Control derivation baseline | `2ce62b5bb31abd44824dc8e358f77e63d539ed98` |
| Request SHA256 | `f6a0d1c354237c1f0ffde252cef84ec2e30b739ae1e5ef41a54ec7cfa3fb761e` |
| Workflow SHA256 | `93521eefcbd83c50218d8484b2f8bbc044ff9acd2dd2b003749fe0e316c0ea6c` |
| Stock tool | `0aac16ef62da9e9d5645782d458593e5d78143ba` |
| Stock tool tree | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

## Source and contract semantics

The derivation delta against efb touches only smallsort.rs. Its 12 original
safety preconditions become paired complementary cfg attributes in five
functions: swap_if_less (5), insert_tail (1), insertion_sort_shift_left (1),
sort4_stable (1), bidirectional_merge (4). Under the complete S2 conjunction,
each original predicate uses crate::kani::requires; outside it, each keeps its
original safety::requires path and predicate. Eight feature projections retain
ordered premise/frame/post tokens and complete function signatures/body tokens;
the seven non-S2 projections retain the entire effective attribute sequence.
Exact normalization and the one-file Git delta also preserve unrelated source.

Swap retains both checked offset/nonwrapping predicates, the same-allocation
predicate and both read/write access predicates. The write set remains exactly
the two element pointers, followed by the identical enabled-domain semantic
ensures with old(capture). No predicate, frame location, comparator restriction,
old capture, generic bound, runtime body or algorithm has been weakened. Insert
and merge retain their additional S2 sorting premises after modifies; source
attribute order remains the original order. Sort8's already direct stack is
unchanged. No new assumed stub or trusted premise is introduced by this delta.

The regenerated map covers 23 active modules, 321 lexical function declarations
and 19 active contract stacks in all 11 identical effective cfg row contexts.
The 19 comprise five repaired functions, sort8, six trait impl methods, three
forwarding contracts and four merge profile contracts. Unselected providers and
model helpers are included. Independent token accounting attributes all 91
literal contract paths, including inactive complementary arms, to the enumerated
declarations; declared attributes and cfg availability also match source. This
does not enumerate compiler-generated harnesses or establish MIR identities.

## Stock macro trace and static gate

The source hashes and line anchors in MACRO-TRACE.json match exact stock0aac
and the source wrappers. safety::requires selects its host implementation and
prepends kani_core::requires to the attributed ItemFn; its runtime placeholder
returns the item. The stock sysroot contract handler parses ImplItemFn and uses
kanitool::checked_with to distinguish untouched from expanded functions. It
does not classify a group by safety/kani/crate::kani spelling. Aliases and
intervening attributes are explicitly supported by the stock documentation.

Bootstrap emits remaining attributes before the five internal markers, enabling
later outside-in expansions to reuse one generated group. Initial names derive
from the function identifier; subsequent clauses find marked closures in match
arms. Requires handlers prepend preconditions; ensures handlers insert old()
remembers after recognized preconditions. The repair retains the source clause
sequence and its stock processing rules. The expected recursion name for swap
is __kani_recursion_check_swap_if_less.

The retained r2 diagnostic comes from the later compiler transform's find_closure,
which searches MIR var_debug_info for the exact name and closure type, including
when mark_unused handles Original mode. This differs from the macro's own
missing-marked-closure panic. Direct paths remove the safety wrapper stage in
S2, but source inspection cannot prove macro resolution, actual expansion,
closure survival or why MIR lookup failed. R2 compileFAILED/0roots is the
coordinator-supplied historical observation; no raw evidence was fetched here.
R1's cause remains UNKNOWN.

The new gate requires exact normalization of a SHA-pinned r2 fixture and checks
cfg semantics and all active stacks. It is deliberately a finite source gate,
not a general Rust parser or macro-expansion verifier. s2_policy invokes it
through the existing runner check-source before tool build. Using the frozen
baseline for the inherited runtime projection is sound within this gate because
actual source must first equal the complete normalization. No existing gate is
removed. The workflow adds its tests while retaining existing tests and caps.

Seven new gate tests pass once on final dc1, covering the old mixed pattern,
wrong predicates/cfg/frame/post/body, unselected provider wrappers, missing
modules, source integration and comment/string handling. Three independent
mutations additionally reorder swap's actual frame/post or delete either
attribute; all are rejected, even with the source hash resealed. These establish
static rejection behavior, not an observed compiler diagnosis.

## Exact inheritance and integration

Frozen approval `a2d6428b35930282b03f91eeadba72eaf3cbef9b` and package
`5a9e715ad9e303fbd10600ee379313301c87e9b3` remain the inheritance baseline.
All source outside smallsort.rs is unchanged from efb, including both general32
ordinary diagnostic_sort8 replacements, removed-registration state, model,
witnesses, providers, 11 roots, 20 covers and six negative oracles. The model's
domain, initialized outputs, frame and full-value relation therefore inherit
the frozen review. Both general consumers remain DIAGNOSTIC_ASSUMED. No model
execution, callee proof or new qualification is established here.

Runner.py changes only STD_SHA and STD_TREE. Collector, packer, binding/CFG
checks and existing tests, including B01/B02 regression code, match2ce byte for
byte. B01/B02 remain closed within the frozen bounded review scope; producer
universality is not claimed. Policy changes only integrate the new gate and its
source-map requirement; fixtures, payload hashes, request bindings and workflow
test inclusion match those changes. Rows, source bindings, variants, execution
groups, flags, budgets and qualification inventories are exactly inherited.
ENVELOPE/MEASUREMENTS/ROOT-BINDINGS/COMPILED-ITEMS maps are byte-identical;
model/assumption maps rebind only source_sha. The inherited ENVELOPE accounting
reference is historical; current request/task reference is item1 29/29,
item2 9/14, total38/43. Neither reference authorizes a charge.

All 45 committed package files and 44 manifest hashes match the reviewed g0.
Each of six full/derivation/parent patches matches exact Git diff bytes and
replays to its declared source/control tree. Required parents are distinct from
derivation baselines. Real shallow Git metadata checks preserve stock0aac at
control depth7 and base99e at source depth5; tool depth2 remains valid. Final
source/control/tool cleanliness, request/workflow/payload/fixture hashes,
source preflight, cfg/stack maps, Python AST and whitespace checks pass.

Unchanged limits are 600s/root, compile900, root-sum6600, group7500,
internal8100, step7560, setup1800, job180min, serial1, group RSS12GiB with
2GiB headroom, checkout7/5/2. Per-root total wall time and R8 attribution remain
UNKNOWN within the inherited envelope.

## Test provenance and handoff

The author's 33 targeted tests ran on precursor
`67ebcf4a2285976b85d986e741adde8e443b706a`, request
`64ea54d7ad935ada202d19e292529f1f3ae21dc2a2269ee6a76db74e0f077b9a`.
Their transcript and exact provenance are retained as author evidence. The
only finaldc1 change from67eb is CI-REQUEST.json's ci_changed_paths: the existing
control gate requires the stock-relative inventory rather than parent-relative
paths. Functional code, source, fixtures, tests and workflow are identical.
The exact final preflight was independently re-executed successfully here;
the seven final gate tests and three extra mutations are separate W14 evidence.
The precursor33 suite was not rerun or relabeled as finaldc1 execution.

APPROVE permits coordinator/root preparation of an exact r3 GO-request. It
does not issue GO. Retry, publication, dispatch and accounting still require
separate owner/coordinator authority. No compiler, macro executable, verifier,
full runner, CI, push, PR, cancellation, ledger, reservation or budget action
was performed. No author paths, old findings or historical evidence were edited.
No subagents or model/tier/Fast changes. Compilation, actual expansion/MIR
lookup, runtime/model execution and qualification remain NOT_RUN; causal repair
UNVERIFIED; formal proof credit NONE; closed proof obligations zero.
