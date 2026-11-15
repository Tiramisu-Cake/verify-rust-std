# Slice02 author/static review

Source `b0a5a4fff9122ae4dabcc9808568c0d15fbe9b12`, tree `03e33b5a3a8b3aa1fd5505467bbe869d1001b44e`.
Exactly one commit on accepted slice01 `d82752c8bc878398e672bffaa631ca6a28430acc`.
Readiness means ready for worker15 review/coordinator CI; independent review and native results are pending.
Parent acceptance is run43696666260, NO_REGRESSION; its integration obligations on4/5 remain unchanged.

## Production and provenance

The 52 owner2 parts are enumerated and hashed in SOURCE-PARTS.json. All anonymous origins,
including unqualified alternatives, remain relevant to the alias graph and initial targets.
AllocId is a compiler-local provenance key, never a runtime object number or an exact alias offset.
Anonymous constant targets already denote referents and are added directly to delayed analysis targets;
ordinary stack-pointer targets continue through graph successors. Constant operand/deref arms use the
same graph resolution. Origin metadata is retained by graph join and transitive closure.

Registry, anonymous origins, graph and cumulative points-to analysis are byte-identical to frozen F.
Observation, bind on insertion/reuse, static registration, prepare, finalization and seal move together.
Registration combines qualification only for compatible exact storage descriptors under the same symbol:
allocation Option bytes, explicit mask and layout remain distinct, including Some(0) versus None.
Conflicts preserve the first descriptor and cannot create qualification. Mutable or relocated storage
is not admitted. The finalizer checks canonical symbol type/lifetime/extent/target and exact source masks.
Seeding happens at reset completion, before each original normal return with labels/control edges retained;
false mask bits are emitted as false, not dropped. Empty masks generate no seed query/index.
Existing U reset/private-state markers are sufficient; runtime/storage changes from4 are absent.

`immutable_origin_type_supported`, its export, `wrapper_inner`, `maybe_uninit_storage`, `for_storage`
and required imports belong2 under accepted post-stage0 variant C. They have current consumers in
anonymous/static qualification. Typed storage, deinit, argument-size and protocol helpers remain4.
No alternative predicate, future API or scaffold was introduced.

The compiler lifecycle is prepare -> codegen -> quantifier postpass -> finalize/seal -> metadata -> split.
The quantifier pass is preserved and moved before metadata with immutable finalization, as assigned2.
F7 scope/cache APIs are absent. Both exact pre-F7 delayed writers from accepted1 remain unchanged.
B1 resolution/no-body/one-walk/common-flush controls are inherited unchanged, as are upstream fixes.

## Extraction seams and docs

Extraction reconstructs owners1+2 from original B1/F line parts and checks the owner1 reconstruction
against the exact accepted parent before writing. Shared files are assembled by hunk ownership,
never restored wholesale for a subset. New registry/anonymous files have sole owner2 and match F.

Omitting owner4's adjacent methods leaves one empty line immediately inside `impl PointeeInfo`;
only that leading empty line is removed. This is a whitespace seam, not a feature or ownership change.
The raw_eq/layout offsets/typed-storage/deinit/protocol/closure/F7 code remains at parent behavior.

DOCS-PARTS.json pins the exact owner2 segments. The general feature document gets only the immutable
qualification/alias-limit paragraphs before the retained baseline issue link. The contract paragraph
gets a direct link to the uninitialized-memory section because its final antecedent/link belongs6;
its initial Whole/immutable line break is joined. No storage/Scope A promise or later limitations
header is imported. Head6 must restore exact F wording and placement after all segments exist.
These interim placement/link adaptations are explicit in SLICE.json and the residual patch.
No workflow, dependency pin, historical JSON suite or research/process content enters the source tree.

## Oracles and limitations

Six complete descriptor-coalescing .rs/.expected pairs are exact F, with all original flags and useful
SUCCESS assertions. Nine registry units are exact F and cover mask bits, compatible aliases in both
orders, descriptor conflicts/qualification, mutable rejection, labeled reset edges and empty masks.
No existing test, golden or directive changes; no new ignore, fixme or weakened failure pattern.

Sixteen owner2 fixtures remain absent: fifteen await head3 (raw_eq) and copy-hole awaits4 (storage).
SLICE.json records each whole fixture/golden hash, prerequisites, assertions and exact literal oracle.
Eleven later-owner consumers are also recorded: mixed-promoted on3/4, contract-immutable on5.
No fixtures are split, rewritten or replaced by easier controls. Units on2 cannot stand in for those
pending source/layout/storage/contract integration obligations. Historical full-F gates qualify F,
not this intermediate head. Closure/capture consumers and parent analysis integration stay pending.

TEST-MANIFEST.json retains every accepted1 regression selector, including full original contract suites
and upstream uninit/delayed-UB inventory, then adds the six new expected selectors. Deduplicated totals
are 317 selectors (308 expected passes, 9 pre-existing ignores), plus ActiveCalls9 and immutable9 units.
These are static expectations, not observations. Native discovery must agree; zero selected units fails.

## Validation

PASS_STATIC_ONLY: deterministic extraction and parent reproduction; 52 original part hashes; lexical
Rust delimiter balance (not parsing/typecheck); exact F production blobs and new fixture pairs;
protected runtime/protocol/visitor/workflow/pins unchanged; lifecycle and pre-F7 seams; no old test delta;
git diff --check. Alternate temporary Git indexes apply source.patch from parent to source tree and
residual-to-F.patch from source to exact F tree `9829702c1aa0ecb73c860fc0ad5451757917d6cb`.
This checks patch endpoints, not the final logical multi-slice recomposition or proof correctness.

NOT_RUN: rustfmt, Rust parsing/typecheck/build/clippy, native units/compiletest/Kani/CBMC, docs build,
CI/push, full logical-stack recomposition. Worker15 independent review PENDING. Cloud spend0.
A real ordinary regression, false SUCCESS, lost assertion or extra Unsupported is still STOP.
