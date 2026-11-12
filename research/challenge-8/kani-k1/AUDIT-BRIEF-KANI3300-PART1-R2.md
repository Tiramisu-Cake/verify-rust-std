# Kani #3300 Part 1 — external audit, round 2

Snapshot: 12 November 2026. This brief combines the coordinator's recorded CI/Miri results with the A1–A3R source handoffs. No compiler, verifier, CI, or build was run to prepare it.
Research links point to verify-rust-std @ `6491a749c2`; Kani code links point to the candidate `a0a2386001`.
The first-round reference is [AUDIT-REPORT-KANI3300-RU.md](https://github.com/Tiramisu-Cake/verify-rust-std/blob/dff05db0c85ebaad823bf54edf28e9c5ddb49291/research/challenge-8/kani-k1/AUDIT-REPORT-KANI3300-RU.md) @ `dff05db0c8`. Preparation documents saying NOT_RUN predate the subsequent coordinator CI runs; they are not execution reports.

## 1. Goal and candidate

Part 1 adds memory-initialization checking for supported direct `MaybeUninit<T>` storage, flat slot arrays/slices, typed conversions, copies, and ordinary by-value calls/returns. Typed reads must still reject unwritten data; raw copies must preserve byte initialization state; typed transfers must not preserve padding that Rust does not guarantee.
This supports real SmallSort scratch verification with `-Z uninit-checks`. It does not complete Challenge 8, establish arbitrary type/length coverage, or discharge invalid-value obligations.
The previous candidate was `1cd96e354`. The new candidate is [`a0a2386001a15fecfe2facc2f6cd87f3dee13b60`](https://github.com/Tiramisu-Cake/kani/commit/a0a2386001a15fecfe2facc2f6cd87f3dee13b60), 16 commits on that baseline ([diff](https://github.com/Tiramisu-Cake/kani/compare/1cd96e354...a0a2386001a15fecfe2facc2f6cd87f3dee13b60)).
It is publicly reachable as the parent of CI-only branch `uninit-ci/a3r-repair` head `3b90da205860ebd579c4ae418c9d20ef66b5bd9a`. The candidate is not ready for publication: one existing test still fails because of raw_eq, and full regression CI has not run on this final candidate.

## 2. Response to the first audit

“Addressed” below means implemented with the stated targeted evidence, not a general correctness proof or final release acceptance.

| First-audit finding | Change / commit | Evidence and remaining limit |
|---|---|---|
| §2.1: typed MU transfers preserved initialized padding | A1: `fc37f9021`, fixtures `5fd713a20`, final `613c18831`; separate full storage extent from typed `D(T)`, repeated at rustc array stride | [43105165870](https://github.com/Tiramisu-Cake/kani/actions/runs/43105165870) passed the quick gate. Same new tests on old Part 1, [43105207965](https://github.com/Tiramisu-Cake/kani/actions/runs/43105207965), gave verification SUCCESS for four intended padding negatives: the original P0 was observed, then corrected. |
| §4.1: Pat offset and nested-enum comparison | A2 production `1f91626a3`, final `3dc0227ce`; preserve `current_offset`, compare variant masks in enum-local coordinates, shift once | Controls were added for nonzero-offset Pat, equal-layout enum and differing-padding enum. Run `43118703581` reports no remaining failure in these selectors; A2's gate was initially blocked by its raw_eq policy. |
| §2.4: unpaired arguments/returns could reach initialized fallback | A3 `e3c529a0d` through `0b1d68ac6`; common supported-instance predicate, current-call protocol, signature/count/index/size checks, mandatory return0 | A3R quick run [43118703581](https://github.com/Tiramisu-Cake/kani/actions/runs/43118703581) reports 93 passed and one failing raw_eq-related test. No full regression or general protocol proof is claimed. |
| §2.6: moved-from semantics must follow actual MIR | A3 snapshots witness state before clearing an in-place `Call(Move(place))` source; Copy, assignment/field Move and intrinsic forget are not blanket-cleared | Pinned Miri probes and repaired custom-MIR tests distinguish these cases; details below. Scope must remain tied to the actual operand/place, not source-level ownership syntax. |
| §4.1: uncovered operations | Reverse `[MaybeUninit<T>; N] → [T; N]` remains explicitly Unsupported; raw_eq was first rejected, then instrumented | This is a declared boundary for reverse conversion. raw_eq remains unresolved, not closed by the repair attempts. |

A1's new controls use a padded payload, fill its physical bytes, and compare raw copy with typed assignment/argument/return. They also check data preservation, false data remaining false, and padding/partial data in array slot 1.
References: [A1 notes](https://github.com/Tiramisu-Cake/verify-rust-std/blob/6491a749c2/research/challenge-8/kani-k1/kani3300/a1/NOTES.md), [A1 result](https://github.com/Tiramisu-Cake/verify-rust-std/blob/6491a749c2/research/challenge-8/kani-k1/kani3300/a1/RESULT-KANI3300-A1.md), [A2 notes](https://github.com/Tiramisu-Cake/verify-rust-std/blob/6491a749c2/research/challenge-8/kani-k1/kani3300/a2/NOTES.md), [A2 result](https://github.com/Tiramisu-Cake/verify-rust-std/blob/6491a749c2/research/challenge-8/kani-k1/kani3300/a2/RESULT-KANI3300-A2.md).
Primary code: [ty_layout.rs](https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs), [check_uninit/mod.rs](https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/mod.rs), [uninit_visitor.rs](https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs), [mem_init.rs](https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/library/kani_core/src/mem_init.rs) @ `a0a2386001`.

### Call protocol and the A3 repair

The protocol admits ordinary nonforeign bodyful `InstanceKind::Item` on both sides; unsupported shadow-carrying calls are rejected. Unselected-argument fallback is allowed only inside a matching current-call protocol; absence/mismatch is not silently blessed. Normal return0 is paired separately.
Stores snapshot witness membership, relative offset and value while the source is live, before any in-place source reset. Loads preserve the selected state through the typed mask. Several arguments, nested/same-size/repeated calls and ordinary-union return0 have dedicated controls.
A3 initially caused 30 quick-suite regressions: a new private-model `argument_count.max(1)` reached unsupported `integer_max`, a custom-MIR fixture ICEd, and extra uninit failures were reported.
A3R `c57314d4c` removes that helper dependency without relaxing protocol checks and replaces `UnwindContinue` with `UnwindUnreachable` for the required panic=abort fixture compilation. `a0a2386001` keeps unmodeled intrinsic shadow-value transfers fail-closed, with a specific no-effect Forget exception; pointer-effect models remain separate.
The coordinator reports 29 regressions resolved in run `43118703581`; the sole remaining failing selector is `maybe-uninit-initialized`. Existing goldens were not weakened to absorb A3R failures.
References: [A3 notes](https://github.com/Tiramisu-Cake/verify-rust-std/blob/6491a749c2/research/challenge-8/kani-k1/kani3300/a3/NOTES.md), [A3 manifest](https://github.com/Tiramisu-Cake/verify-rust-std/blob/6491a749c2/research/challenge-8/kani-k1/kani3300/a3/TEST-MANIFEST.json), [A3 result](https://github.com/Tiramisu-Cake/verify-rust-std/blob/6491a749c2/research/challenge-8/kani-k1/kani3300/a3/RESULT-KANI3300-A3.md), [A3R notes](https://github.com/Tiramisu-Cake/verify-rust-std/blob/6491a749c2/research/challenge-8/kani-k1/kani3300/a3r/NOTES.md), [A3R result](https://github.com/Tiramisu-Cake/verify-rust-std/blob/6491a749c2/research/challenge-8/kani-k1/kani3300/a3r/RESULT-KANI3300-A3R.md), [A3R review](https://github.com/Tiramisu-Cake/verify-rust-std/blob/6491a749c2/research/challenge-8/kani-k1/kani3300/a3r/REVIEW.md).

### What Miri established

Coordinator probes on nightly-2026-10-23, branch `probe-ci/b2-moved-from`, runs `43109689395`, `43109978880`, `43111757334`:
- Assignment Move, field Move, forget and a by-value call through a temporary leave the observed original source initialized.
- Custom MIR `Call(f(Move(src)))` on the same address-taken local makes a subsequent source read uninitialized; `Copy(src)` remains valid.
These observations support a narrow in-place rule. They do not justify clearing every Move, nor assuming every ordinary call uses the same lowering. Actual Kani MIR/place identity remains relevant, especially for aliases, temporaries and reinitialization.
The candidate controls are [maybe-uninit-call-move](https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/tests/expected/uninit/maybe-uninit-call-move/main.rs), [call-pairing](https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/tests/expected/uninit/maybe-uninit-call-pairing/main.rs), and [unsupported pairing](https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/tests/expected/uninit/maybe-uninit-call-pairing-unsupported/main.rs).

### Deliberately outside this Part 1

- Stage B1 is the independent unresolved-call/operation-loss repair, branch `fix/kani-uninit-unresolved-call` @ `d5f072f2b`; it is not integrated here. This stage name is distinct from the earlier “PR-B1” name for the G1 union-pointee feature.
- B3 is the separate ZST union backend candidate, `fix/zst-union-codegen` @ `6db3c4dab`.
- B4 realloc shadow effects, the G1/compound-storage expansion and T1b shared-cache work remain outside this candidate. No result from those tracks is credited to it.
Keeping a fix separate does not by itself prove independence: the auditor should assess whether Part 1 needs any of these fixes as a prerequisite or must narrow its supported domain.

## 3. Main blocker: raw_eq

raw_eq can read every byte of both pointees, including padding; treating an ordinary typed value's data mask as its complete byte-read obligation is insufficient. Standard array equality also reaches this intrinsic, so its policy affects existing MU regression tests.

| Attempt | Implementation | Coordinator result |
|---|---|---|
| A2 | Reject raw_eq as Unsupported | [43107071880](https://github.com/Tiramisu-Cake/kani/actions/runs/43107071880): three existing MU tests fail. |
| A2R `85fc5cd2c` / `b20784793` | Check both full pointee extents using byte-array CheckAs; add both references as initial targets | [43111242922](https://github.com/Tiramisu-Cake/kani/actions/runs/43111242922): two regressions restored, but `maybe-uninit-initialized` has two false failures in SpecArrayEq, with `*const [u8;4]` diagnostics. |
| A2R2 `585c93b2f` | Form `AddressOf(*reference)` before the byte-array cast, avoiding a synthetic reference-storage read | [43117585146](https://github.com/Tiramisu-Cake/kani/actions/runs/43117585146): diagnostics now name `[u8;4]`, but two false failures remain. |
| Current A3R candidate | Retains the A2R2 raw_eq behavior | [43118703581](https://github.com/Tiramisu-Cake/kani/actions/runs/43118703581): this is the remaining failing test. |

The relevant existing fixture writes a `MaybeUninit<[u8;4]>` bytewise, then executes `assert_eq!(slot.assume_init(), [1,2,3,4])`. The coordinator attributes the failures to the ordinary array temporary produced by assume_init and the promoted constant array: valid bytes exist, but no initialization-shadow setter covers their materialized objects.
The current model does not encode a general three-way initialized/uninitialized/untracked state. It follows one nondeterministically chosen object/byte witness; reads outside it return true, while a matching witness starts with value=false unless an appropriate setter/transfer updates it.
Therefore a missed initialization update for a valid temporary can cause a false failure when that object is selected. This is more precise than “all untracked reads default to uninit.” Changing the default to true or blessing an arbitrary pointee could hide genuinely unwritten bytes.
The current address fix establishes the intended pointee construction in source, not the complete provenance of the remaining failures. A diagnostic type alone does not prove an extra pointer indirection. Caller MIR, promoted-allocation identity, relevant sets/transfers and the selected witness still need correlation.
References: [A2R notes](https://github.com/Tiramisu-Cake/verify-rust-std/blob/6491a749c2/research/challenge-8/kani-k1/kani3300/a2r/NOTES.md), [A2R2 notes](https://github.com/Tiramisu-Cake/verify-rust-std/blob/6491a749c2/research/challenge-8/kani-k1/kani3300/a2r2/NOTES.md), [existing initialized fixture](https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/tests/expected/uninit/maybe-uninit-initialized/main.rs), [raw-eq controls](https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/tests/expected/uninit/raw-eq-uninit/main.rs).
The controls use 3-byte arrays and a 12-byte padded payload to retain raw_eq through the pinned compiler's InstSimplify; small scalar-sized examples can lower to different operations. Test intent must be checked against actual MIR.

### Options and planner assessment

- **(a) Restore the base behavior: no raw_eq initialization checks.** This is the practical interim compatibility option, only if explicitly accepted as an uncovered read class and reflected in support claims. It is not a soundness fix for raw_eq, and “same as base” requires matched tests; it does not establish Challenge 8's automatic UB exclusion.
- **(b) Check only precisely tracked storage, skip other operands.** This needs a proven full-range provenance predicate and sound state transfer across temporaries, promotions and aliases. The current type predicate for MU/union storage is not that predicate; an ordinary array can originate from storage. I do not endorse a type-only implementation as sound coverage.
- **(c) Blanket Unsupported.** This fails closed, but is already known to reject ordinary array equality and break the baseline suite. It is rejected as the current compatibility solution; the failure of (c) does not make (a) or (b) complete.
My preference is to ask the auditor explicitly whether the narrow Part 1 may use (a) pending a separate raw_eq model. The longer-term direction is a justified ordinary-value/promoted-constant initialization and provenance model, followed by complete byte-read checks. No global bless, test rewrite, or third speculative repair is proposed here.
The two raw_eq repair rounds have hit the stop rule; an owner/auditor decision is pending.

## 4. Open risks before full CI and publication

- Quick CI means format/build/clippy and the uninit-check suites, not the complete Kani regression matrix. A1's gate and A3R's 93/1 summary must not be treated as identical test selections or a final full-CI PASS.
- A2R2 changed shared CheckAs operand construction, not just a test. Review other reference/pointer consumers and constant-reference operands as well as raw_eq.
- Protocol correctness still needs review across shims, nested calls, repeated signatures, zero-sized values, normal returns and potentially aliased moving arguments. A fallback is safe only within its proved nondeterministic protocol.
- Confirm exact Kani MIR for in-place Call(Move), temporary lowering and reinitialization; the custom-MIR/Miri results are not a blanket source-language rule.
- Check how the separate B1 resolver defect interacts with Part 1's new Unsupported paths and previously collected entry/terminator operations; “outside scope” is not a substitute for fail-closed behavior.
- Existing PFC/MU-roundtrip resource limitations and private-state frame effects remain; the new protocol must not enlarge compatibility claims without matched legal/frame/clause evidence.
- Named expected failures and totals do not exclude every additional failure inside a negative harness. Inspect the intended reached operation/property and keep old controls intact.
- Audit the exact upstream export, dependency commits and test goldens after the raw_eq decision. Do not credit a later tree with an earlier run or promote static READY records to execution evidence.
- The coordinator reports possible fork Actions blocking since 12 November 00:17 UTC (“repository invocation blocked”). Current availability is not independently verified; no new CI is authorized until the owner checks. Local compiler/verifier execution is unavailable under this workflow.

## 5. Questions for the auditor, in priority order

1. **raw_eq release decision:** Is option (a) acceptable for this narrowly stated Part 1, with raw_eq byte reads explicitly uncovered, or is raw_eq support a publication prerequisite? Does the candidate expose new unchecked MU paths that the base rejected?
2. **Cause of the false failures:** Do the assume_init temporary and promoted constant lack the required initialization transfer, or are the check address, witness selection, analysis relevance or cross-root cached instrumentation also involved? What exact MIR/object/state evidence would distinguish them?
3. **Option (b):** What predicate can soundly prove that both complete pointee ranges have usable shadow provenance after promotion, conversion, copies and pointer erasure? Where must unsupported/unknown origins be handled instead of skipped?
4. **Initialization model:** What setters/transfers are justified for ordinary return temporaries and immutable promoted allocations, while retaining false padding/data states? How should the single-byte witness distinguish missing instrumentation from actual uninitialized memory without a blanket initialized default?
5. **raw_eq controls:** Are the retained-intrinsic array/padding tests sufficient, including left/right holes, ordinary locals, reference parameters, promoted values and ZST? What matched base/candidate case is required before accepting a rollback or restricted model?
6. **A1 closure:** Do D(T), stride repetition, constants and array-slot handling fix the padding P0 without blessing false data or changing raw-copy semantics? Do runs 43105165870/43105207965 provide the right differential controls?
7. **A2 closure:** Are Pat and enum-local offsets composed exactly once, including nested arrays and layouts with different variant padding? Is the reverse MU-array boundary explicit and actually exercised after compiler simplification?
8. **A3 protocol:** Do the current-call signature/count/index/size checks and mandatory return0 make the unselected-argument fallback valid? Are snapshot, consume and repeated/nested-call rules sufficient when arguments alias or a shim lacks a matching store?
9. **Move semantics:** Does the exact Call(Move(place)) rule match the pinned Miri/Kani execution model, including writes by the callee and reinitialization? Are the abort-strategy custom-MIR fixtures valid without masking the original ICE or unrelated failures?
10. **Intrinsic scope:** Does A3R reject unmodeled shadow-value intrinsics before skip paths while retaining correct Forget and pointer-effect models? Are any helper dependencies like integer_max still reachable unexpectedly?
11. **Dependencies outside Part 1:** Must B1 unresolved-call handling or B3 ZST codegen be integrated first? Which residual realloc/foreign-call behaviors need explicit guards or support exclusions for the proposed domain?
12. **Full-gate requirements:** Which legal PFC/frame/clause, multi-harness, layout and cross-target checks are essential after resolving raw_eq? What would justify separating a known resource limit from a remaining semantic defect?
13. **Readiness:** What minimal source/export changes and exact-run evidence are required for Part 1 ready-for-review, and which remaining topics should become separate upstream issues/patches rather than further changes to this candidate?
