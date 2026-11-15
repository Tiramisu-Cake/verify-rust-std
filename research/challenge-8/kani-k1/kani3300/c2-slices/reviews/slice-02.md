# Slice 02 IMMUTABLE — worker15 read-only review

2026-11-15. **PASS_STATIC_ONLY: no blocking findings; READY for coordinator CI preparation.**
Candidate `b0a5a4fff9122ae4dabcc9808568c0d15fbe9b12`, tree `03e33b5a3a8b3aa1fd5505467bbe869d1001b44e`,
exact parent `d82752c8bc878398e672bffaa631ca6a28430acc` (accepted NO_REGRESSION run43696666260).
Package input g0 `ff3ce29e4f6694f28b0d6fcf025e70cfeae8f378`; U/B1/F identities unchanged.
No worker14 source, test, doc or package files edited. This review is limited to stage2 delta and its inherited prerequisites.

## Ownership and extraction

All52 owner2 parts match the canonical source-map coordinates/hashes and SOURCE-PARTS exactly.
Read-only reconstruction reproduces the accepted parent and this candidate with only the three declared
adaptations: leading blank removal inside PointeeInfo, interim immutable paragraph placement, and explicit
contract-doc link/reflow. The adaptations preserve the intended text and have exact-F restoration assigned6.
29 changed paths =15 production +12 tests +2 docs. Existing tests/flags/goldens are unchanged.

Accepted qualification prerequisites `immutable_origin_type_supported`, export, `wrapper_inner`,
`maybe_uninit_storage`, `for_storage` and required imports belong2 and have present consumers; they are
not deferred storage implementation. No typed/deinit/argument-size/protocol helpers, runtime, raw_eq,
layout offsets, closure code or edge guards from3–6 entered this delta. data_bytes_for_ty is unchanged
from the parent. In compiler_interface only immutable prepare/finalize and the prerequisite quantifier/
metadata ordering move: no F7 delayed scope/cache API. Both existing pre-F7 delayed writers remain exact.
Existing B1 resolver/no-body/walk/flush and upstream fixes remain inherited, without another B1 change.

## Correctness invariants inspected

Anonymous provenance is retained even when qualification fails. AllocId remains a compiler-local key;
carrier slot offsets are not referent offsets or runtime object IDs. Constant/deref resolution, initial
anonymous targets, direct referent targeting, graph joins and closure preserve origin metadata together.

Registry descriptors, bind-on-emission/reuse, statics, preparation, finalization and seal move as one unit.
Exact allocation bytes (including None versus Some(0)), explicit masks, layout, mutability and relocations
are compared before combining qualification. Compatible aliases combine **qualification by OR**, as the
accepted F5 contract requires; masks are not OR-ed or replaced by all-true. Incompatible descriptors
cannot supply qualification; admitted conflicts fail, otherwise the first descriptor is retained. Mutable/
relocated storage remains unadmitted. Original false mask bits survive emitted reset seeding. Finalizer
checks the actual symbol/type/extent/target; labeled normal-return edges and empty masks remain handled.
Lifecycle: prepare → codegen/contracts → quantifier postpass → finalize/seal → metadata → split/export.

Main review checked map/extraction/graph/layout/docs/oracles. A bounded independent Luna HIGH read-only
review checked registry/origin/codegen integration and found no blocker. Reviewed registry/origin/emission
files match frozen F; compiler_interface differs from F only by the five absent F7 scope lines.
No runtime or Rust typechecking result is implied by that identity comparison.

## Oracles and deferred qualification

Six complete descriptor-coalescing fixtures are byte-identical to F: direct-first, nested-first,
the two volatile variants, aggregate-constant-initializer and const-fn-initializer. Their original flags,
three useful SUCCESS assertions, N0 and one-harness completion remain intact. Nine immutable units are
exact F: zero/hole masks, compatible aliases in both orders, incompatible descriptors, mutable/unqualified
refusal, labeled reset edges and empty extents. CI must actually select9/9; zero tests is failure.

The16 absent owner2 whole fixtures are honestly PENDING:15 masks/promoted/static/subrange/relocation
fixtures require raw_eq on3; immutable-masks/copy-hole requires4. The11 later-owner immutable consumers
remain assigned3/4/5 (contract-immutable on5). Their complete input/golden hashes, exact oracles,
prerequisites and source parts match the accepted ORACLE-MAP. No fixture was split or weakened to
simulate early qualification. All existing expected/uninit selectors are included; full inherited311
selectors survive unchanged, plus6 =317. Parent analysis integration remains PENDING4/5.

## Validation and acceptance boundary

[Static/source checks](../ci/slice-02/check_source.py) PASS; [CI runner checks](../ci/slice-02/check_overlay.py)
19/19 Python synthetic checks PASS; Python AST/YAML and git diff --check PASS. Clean before/after source
snapshots agree on3892 protected entries. [CI request](../ci/slice-02/CI-REQUEST.md) pins the exact source
and CI-only overlay. No compiler/runtime/tests/docs/dependency change in that overlay.

NOT_RUN: Rust parsing/fmt/build/clippy, native units/compiletest/Kani/CBMC, docs build, CI, push or dispatch.
Historical F acceptances do not qualify this intermediate head. No Gate A, structural F7 qualification,
SmallSort or formal proof credit. Coordinator must review reached assertions/negatives and native outputs;
aggregate exit0 does not close deferred obligations. Ordinary regression, false SUCCESS, extra Unsupported,
lost assertions, identity mismatch or missing/partial execution remains STOP.

## Correction review — revised head 932fb8395a (2026-11-15)

**Current verdict: PASS_STATIC_ONLY, fresh exact-head CI required.** New source
`932fb8395a58f8c86c0d702ba2cae835823b2962`, tree `2c4d5ad4b72a7d07059f1461132a58da03f81ef9`,
same accepted parent d82752c8bc. Coordinator reports run43699468860 failed E0726 on the superseded
b0a5a4fff9/83550218 overlay. That native failure invalidates the old candidate's readiness; the original
static review above missed the compile seam and remains historical. No raw CI logs were read.

Exact old→new source diff is one line only: `impl MirVisitor for InitialTargetVisitor` becomes
`impl MirVisitor for InitialTargetVisitor<'_>`. It pairs the trait impl with the existing lifetime-bearing
struct/inherent impl; matches exact F. No body, behavior, fixture, flag, golden or later-slice/F7 code changes.
Canonical source-map now assigns both impl-header replacement parts to2 and the adjacent raw_eq comment
to3:54 owner2 parts, all hashes/coverage checked. The cumulative manifest remains317 selectors +9 ActiveCalls
+9 immutable units;16 owner2 and11 later-consumer deferred obligations remain unchanged and PENDING.

[COMPILE-SEAMS](../slice-02/COMPILE-SEAMS.md) reviewed for bounded coverage: inventories cover all21
changed Rust files on2, complete current imports/impls, changed declarations, generic impl consumers
throughout the compiler and explicitly bound cross-file API calls; inherited1 interfaces are also covered.
Report paths/hashes and call contracts match the exact revised head. The old-head regression report detects
the missing explicit lifetime. No further missing prerequisite found in this bounded review. Token inventory,
arity and reference agreement are not name resolution, borrow/trait checking or compile PASS; those limits
are stated honestly. Original analysis integration PENDING4/5 is preserved.

Replacement overlay/request supersedes only the old preparation: see [current CI-REQUEST](../ci/slice-02/CI-REQUEST.md).
19/19 Python synthetic runner checks PASS. Local Rust builds and new native CI/push/dispatch remain NOT_RUN;
new run acceptance belongs to the coordinator.
