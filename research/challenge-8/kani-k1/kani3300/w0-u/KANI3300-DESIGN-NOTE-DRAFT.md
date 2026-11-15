# RFC draft: initialization tracking for MaybeUninit storage and selected MIR bodies

Owner-only draft for [Kani #3300](https://github.com/model-checking/kani/issues/3300), 2026-11-16. The text below requests review; it does not report upstream acceptance or publication.

---

## Problem

Challenge 8 asks for SmallSort memory safety and checked sorting contracts. Its helpers move initialized values through partially initialized scratch storage and invoke comparators by reference. Initialization checks need to distinguish a storage byte from a typed payload byte, carry that distinction through direct calls, and analyze the body actually selected by contract/closure transformations. Treating all storage as initialized hides holes; treating initialized immutable constants as holes rejects legal reads.

This proposal extends the existing experimental `-Z uninit-checks` machinery. It is a limited contribution toward #3300, not a claim to solve that tracking issue or the challenge. Current evidence consists of fork regression qualification and bounded helper harnesses. Upstream tool integration and actual organizer CI are still required.

## Goals and non-goals

The experimental domain includes a `MaybeUninit<T>` slot, flat `[MaybeUninit<T>; N]` and `[MaybeUninit<T>]`, and `MaybeUninit<[T; N]>` where the payload layout is computable. Goals are to preserve holes and padding accurately across supported storage operations, pair shadow transfers for direct MIR-body calls, seed qualified immutable allocations, and keep delayed instrumentation local to each model/root.

This does not introduce a new alias/provenance model, grant memory access, establish absence of every UB class, prove all generic types or lengths, or support arbitrary indirect calls and recursion. Value validity, immutable-byte mutation and access permission remain distinct obligations. The tested helper profiles do not establish panic/unwind coverage or a functional sorting theorem for the module.

## Source decomposition and dependencies

The seven dependent slices start from clean upstream `0aac16ef62da9e9d5645782d458593e5d78143ba` plus our existing [#5172](https://github.com/model-checking/kani/pull/5172), exact source `6fe484b30043b3696b5f1ccc4bea0e42891ad012`. That dependency preserves checks at unresolved calls; it is already open and is not being resubmitted.

| Slice | Scope | Exact source | Immediate parent |
|---|---|---|---|
| PR-01 | Selected-body analysis, active-call cycles, ordinary entry slots | `d82752c8bc878398e672bffaa631ca6a28430acc` | #5172 |
| PR-02 | Whole immutable allocation masks | `932fb8395a58f8c86c0d702ba2cae835823b2962` | PR-01 |
| PR-03 | Nested layout offsets and full-extent raw equality | `5ca51679e3f433718807a2e44add0d5abac128e7` | PR-02 |
| PR-04 | Storage operations and paired direct-call shadow transfers | `345cedfd67df679e326474385308349d609fc43d` | PR-03 |
| PR-05 | Closure capture layout masks | `96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f` | PR-04 |
| PR-06 | Edge fixtures and documentation | `3f5242bb1539fb88196d7e503b722f0905f2b46c` | PR-05 |
| PR-07 | Delayed-body cache restoration and model isolation | `8e299aa6243bc5f06a29c51e98aafa9564478220` | PR-06 |

Review and merge order follows this chain. While the parents remain open, each stacked PR includes its unmerged ancestors in its diff against `main`. No slice is described as independently closing #3300. The final tree is `9829702c1aa0ecb73c860fc0ad5451757917d6cb`.

A separate `select_unpredictable` initialization fallback is qualified at source `14bc57fdb99960240c4944845a3d985c8af4dcf7`, parent `8e299aa6243bc5f06a29c51e98aafa9564478220`, tree `1efb6e4dfa69d346df8e23741d11839b1932403d`. It adds a special, validated route to the intrinsic's standard Rust fallback, with payload validation and paired argument/return transfers using the existing typed masks and shadow-state representation. It is an additional change, not one of the seven slices, and its successful bounded replay must not be attributed to the seven-slice head alone.

## Proposed architecture and actual behavior

### One witness, distinct masks

The runtime maintains one nondeterministically selected object/byte-offset witness and its Boolean initializedness, rather than allocating a shadow array for every program allocation. Checks outside the selected witness are neutral; preservation through copies and transfers must retain the ability to observe a hole at the selected byte. The transfer buffer is verifier-private state in the marked initialization-state object.

Two Boolean masks have different meanings. In an **initialization-state mask**, false denotes an uninitialized byte and true an initialized byte. Constant masks preserve `None` versus `Some(0)`: a hole is not an initialized zero. In a **payload-layout mask**, true selects a data byte that a typed read requires, while false excludes padding. A typed value transferred to `MaybeUninit<T>` initializes its payload bytes while leaving padding uninitialized; raw storage copies preserve source byte state across the whole storage extent. Deinitialization clears the full extent, including padding. A layout mask alone does not assert that its selected bytes are initialized.

Storage operations distinguish typed payload transfers from bytewise copies. Supported Copy operands are snapshotted before any Move deinitialization. Whole-storage resets prevent stale initializedness from surviving an overwrite. `raw_eq` checks the full compared pointee extent, including padding, rather than only typed payload bytes; unsupported layouts remain an explicit boundary.

### Direct calls and selected bodies

Caller/callee transfer is paired only for supported ordinary, non-foreign, MIR-backed item calls, excluding Kani hooks. Begin/store/load operations agree on signature, argument count, argument position and the return slot; return transfer follows the normal edge. Unsized storage is rejected before starting a partial protocol. Paths without the paired protocol retain conservative resets where supported; no missing transfer is replaced by invented initialization.

Analysis records the selected contract-registration or discarded-closure body and its provenance. It uses root-local body snapshots, resolves calls through the existing fallible resolver, visits call operands once and retains their checks. The active-call chain identifies cycles by instance and selected body. A cycle latches an error, aborts that root's analysis and discards its incomplete graph rather than treating it as a valid summary. Delayed-analysis cycles remain unsupported.

Ordinary sized scalar/reference argument **slots** are initialized before tracked reads. This does not initialize a reference's pointee or bless union/MaybeUninit storage. Closure masks use monomorphized capture offsets and layout; a sized zero-byte closure has an empty mask. These changes do not substitute a tuple layout or an all-true mask for an actual closure layout.

### Immutable origins and permissions

Compiler-produced immutable allocation origins are bound to emitted storage. Seeding requires a whole allocation at offset zero with matching extent, no relocations, a supported `Freeze` origin type and a computable exact mask. Compatible aliases may share a descriptor only when storage identity, extent, layout and mask agree; conflicting descriptors are rejected. False bits survive seeding after state reset, and empty masks require no byte query.

These are initialization metadata. They grant neither mutability nor permission to load/store through a pointer. Mutable allocations, unsupported relocation/subrange cases and conflicting origins do not become initialized through this mechanism. This proposal does not establish the challenge's immutable-byte mutation obligation by marking constants initialized.

### Delayed mutation and per-root isolation

Delayed instrumentation journals its body replacements and restores them when the model code-generation scope ends, including failed-root paths. Regular/stub transformations and selected-body provenance remain separate from the delayed journal. Both code-generation backends scope reachability/global passes and code generation in the restoration guard.

The structural controls compare selected roots compiled in fresh mixed-root runs with those roots' own isolated runs. On the final seven-slice source they completed 11 invocations and 18 exact comparisons, with intended negative/cycle exits retained. Together with six cache and two scope unit tests, this supports restoration for the tested cases. It does not prove universal isolation for every transformation, backend or workload, nor infer AST/MIR semantic equivalence from matching source coordinates.

## Alternatives and open design choices

- An all-true storage mask would erase holes and padding distinctions; a blanket all-false seed would reject supported initialized constants. Exact masks preserve both cases.
- A complete shadow memory per allocation would be a different cost/design tradeoff. The submitted source retains the existing one-witness approach; no replacement memory model is proposed here.
- General function-pointer/vtable dispatch and recursive summaries would require additional analysis and transfer rules. They are deferred; unresolved paths remain explicit boundaries rather than assumed summaries.
- A nondeterministic shadow summary constrained by contract ensures for `stub_verified`/Replace or loop havoc is a question for maintainers, not adopted behavior. It needs an argument that no hole witness is excluded and distinguishing controls before any claim.
- A whole-module proof or a generic-T theorem would exceed this evidence. Named types, geometries and direct closure bodies are qualified first; source-parametric reasoning is not converted into a mechanized universal theorem.

## Evaluation and evidence

All runs below are in our fork; CI-only overlays are distinct from the source heads above. They do not supply organizer CI integration. Counts and acceptance are reported from curated coordinator receipts; this draft does not independently award formal proof credit.

PR-01 has **no new end-to-end tests for its analysis feature on its own**. Exact-head run [43696666260](https://github.com/Tiramisu-Cake/kani/actions/runs/43696666260) on `d82752c8bc878398e672bffaa631ca6a28430acc` provides formatting/build/Clippy, 9 ActiveCalls units and 302 regression passes, with 9 existing ignores. Exact-head run [43701587141](https://github.com/Tiramisu-Cake/kani/actions/runs/43701587141) on PR-02 `932fb8395a58f8c86c0d702ba2cae835823b2962` provides 9 registry units and 308 regression passes, including six new descriptor cases, with 9 existing ignores. Both are selected ubuntu-24.04 qualification.

Deferred analysis/layout/storage integration ran on cumulative PR-04 source `345cedfd67df679e326474385308349d609fc43d`, [43710024495](https://github.com/Tiramisu-Cake/kani/actions/runs/43710024495), and closure/contract integration on PR-05 source `96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f`, [43715788377](https://github.com/Tiramisu-Cake/kani/actions/runs/43715788377). Those results do not establish standalone behavior on PR-01's head. PR-07's structural/LLBC/regression qualification is [43723531871](https://github.com/Tiramisu-Cake/kani/actions/runs/43723531871), source `8e299aa6243bc5f06a29c51e98aafa9564478220`.

Full regression run [43665002636](https://github.com/Tiramisu-Cake/kani/actions/runs/43665002636) used accepted export `ad499e41dd2db9ccd432f89721638a1f3a0bbd44`, whose tree equals the final seven-slice tree. It completed 33 ordered stages on each of ubuntu-24.04, ubuntu-24.04-arm and macos-15. The corresponding bounded closure replay [43683557088](https://github.com/Tiramisu-Cake/kani/actions/runs/43683557088) had two merge successes, but sort4 stopped at the `select_unpredictable` boundary with return unreachable. Neither run is evidence for a standalone earlier slice or a whole-module proof.

The separately qualified fallback source `14bc57fdb99960240c4944845a3d985c8af4dcf7` has this chain:

1. Quick [43740679160](https://github.com/Tiramisu-Cake/kani/actions/runs/43740679160), ubuntu-24.04: formatting/build/Clippy/LLBC exit zero; 76 compiler units; ActiveCalls9, immutable9, argument-size1, marker-category1, delayed-cache6 and delayed-scope2 units; kani50/0/3, expected402/0/6 (including 29/29 intrinsic controls), UI17, script3, JSON17, std2; 4/4 mutations and 18 structural comparisons.
2. Full three-platform regression [43744142824](https://github.com/Tiramisu-Cake/kani/actions/runs/43744142824): 33/33 ordered stages and exit zero per platform. Expected-suite counts were 773 passed/0 failed/13 ignored, exactly 29 more passes than the seven-slice tree. Curated rounded times are **41 minutes ubuntu-24.04, 40 minutes ubuntu-24.04-arm, 76 minutes macos-15**. That receipt does not report RSS.
3. Bounded six-row replay [43751703000](https://github.com/Tiramisu-Cake/kani/actions/runs/43751703000), ubuntu-24.04, six serial jobs. Tool source is the same separate fallback head; std source is `70ba5befc617627073738e26cb1466bd4fb76e41` plus test-only overlay `6075e7ce17179f45642c9ffe8fe09e3ec9395726`. Flags include `-Z uninit-checks`, object-bits12, controls cfg ON and `--no-assert-contracts`; **`-Z valid-value-checks` is OFF**. Exact harness identities, geometry and bounded outcomes follow.

All replay selectors below have prefix `slice::sort::shared::smallsort::verify::`. Geometry and target are part of each claim; changing them requires new qualification.

| Selector suffix / target | Geometry; source unwind | Failures / total (unreachable); covers |
|---|---|---|
| `helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0`; Check(bidirectional_merge) | u64 len8, MU scratch48, src[32..40], dst[0..8];34 | 0/572 (16);5/5 |
| `replay_gateb_prime::merge_profile_closure_scratch48_u8_n9`; Check(concrete closure profile) | u8 N9, scratch48, both backings;34 | 0/1030 (68);2/2 |
| `helper_contracts::sort4_safety_u64`; Check(sort4_stable) | u64 src4/dst4;16 | 0/753 (14);3/3 |
| `helper_contracts::swap_safety_u64_backing4`; Check(swap_if_less) | u64 backing4;8 | 0/585 (12);6/6 |
| `replay_uninit_controls::sort4_raw_all_initialized_u64`; Original(sort4_stable) | u64 src4/dst4;16 | 0/382 (12);2/2 |
| `replay_uninit_controls::sort4_raw_hole_negative_u64`; Original(sort4_stable) | same, source[1] unwritten;16 | Exactly1/382 intended failure;2/2 |

All legal rows reached return. The negative retained verifier exit1 and exactly the intended uninitialized u64 read, `sort4_stable::<u64, …read_less_u64>.safety_check.1`, at smallsort.rs:751:26. A refusal, layout error or unreachable return would not substitute for this control. The replay result reports neither timing nor RSS: **both costs are unknown**. Earlier measurements on another source/run cannot supply them.

## Independent sorting contracts and integration

The sorting-contract campaign starts from std `872d5a43380752786415bc00d2a12ce0e930cb37` and **clean upstream Kani `0aac16ef62da9e9d5645782d458593e5d78143ba`**, with uninit/value checks OFF. It targets primitive/default ordering, actual checked trait-method contracts and the valid threshold domain: fallback16 and general/network32. Symbolic lengths and six-implementation-body accounting are our proposed coverage strategy. That campaign and its organizer pin-bump request do not wait for completion or merging of the seven-slice initialization series.

The separate safety campaign retains its own std/test source, arbitrary-bool closure comparators and initialization-check flags. Functional evidence without extra UB checks cannot be combined with safety results simply because root names match. Any combined claim needs compatible source, target, comparator, mode, flags and newly qualified evidence. The existing [verify-rust-std #752](https://github.com/model-checking/verify-rust-std/pull/752) remains its own bounded proposal; these fork results do not migrate into its submitted tree automatically.

## Limitations

The bounded closure-comparator replay is not all T/N, not the function-pointer comparator profile and not whole SmallSort. It does not address #5104 or establish general aggregate/array value validity. Function-pointer and trait-object call dispatch, shadow transfer under `stub_verified` (Replace) and `kani::recursion`, delayed-analysis cycles, by-value nested union/MaybeUninit aggregates and intrinsics without an initialization model remain unsupported or unqualified as documented for their source. The separate fallback only addresses the tested `select_unpredictable` path.

Loop-contract havoc interactions remain **open/unqualified** unless a specific control establishes their behavior. Merely enabling `-Z loop-contracts` in a harness invocation does not qualify arbitrary havoc/shadow interactions. Initialization metadata is not an aliasing, validity or write-permission proof. Rounded regression costs and bounded successes do not establish ordinary organizer CI time/RSS fit.

## Questions for maintainers

1. Is retaining the one-witness model with these explicit masks, direct-call protocol and per-model restoration an acceptable direction and review decomposition?
2. Which additional controls would you require around selected contract bodies, immutable origins and delayed-body restoration before broader qualification?
3. What shadow summary, if any, should a future Replace/recursion or loop-havoc design provide without excluding an uninitialized witness? These are proposed review questions, not implemented extensions.
4. How should small follow-up fixes and organizer-compatible integration be staged after review, while the independent stock-upstream sorting path proceeds?

*Disclosure: this change and description were prepared with the help of AI assistants.*
