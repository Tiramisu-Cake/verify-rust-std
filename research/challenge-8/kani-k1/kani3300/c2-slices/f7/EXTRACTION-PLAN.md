# F7 separate extraction plan — worker15 stage0

No production extraction/commit now. Stage7 starts only on coordinator's immutable accepted cumulative head6; worker15 writes, worker14 reviews/recomposes. B1 remains parent; no SEL1, experimental runtime, JSON runners or T1b allowlist.

Exact reference delta: ad324418cdc66b18e9b71f76a412be6ccea20c7e → 3b382c812a1b8541946e6dc732cf04497ebcf995. All five relevant files are unchanged from S4 to F. F7-RESIDUAL.json pins file blobs, historical0-context patch hashes/headers and comparison summaries. These are plan anchors, not an applied patch. Worker14 source hunk IDs are linked through ../oracle-map/ORACLE-MAP.json F7 feature.

| File | Residue owned only by7 |
|---|---|
|M/transform/delayed_cache.rs|New144-line first-write journal incl6 tests|
|M/transform/mod.rs|DelayedCache/Deref imports/module, journal field/default, delayed_scope and replace_delayed_body, RAII Deref/DerefMut/Drop,2 tests|
|M/transform/check_uninit/delayed_ub/mod.rs|Remove TransformationResult import; replace ordinary delayed writer and failed-root writer with replace_delayed_body (both)|
|codegen_cprover_gotoc/compiler_interface.rs|5-line scope at codegen_items entry; immutable prepare/finalize from2 stays|
|codegen_aeneas_llbc/compiler_interface.rs|3-line scope at model-codegen entry including PubFns; backend-owned transformer still scoped|

M = kani-compiler/src/kani_middle. Before7 there is no journal/no-op API/stub. Intermediate1–6 uses actual pre-F7 ad324 writer: ordinary path updates existing cache entry via and_modify + TransformationResult(body,true); failed-root inserts TransformationResult(body.into(),true). Keep its import. Record that exact temporary adaptation in head6 metadata;7 removes it. Intermediate results are not structurally isolated and cannot inherit F7 assurance. Don't roll back immutable2, ordinary transforms or override provenance.

Review invariants:

- Begin once per model before reachability, keep active through codegen/contract/model materialization. Export workers receive owned materialized symbols; scope cannot end before MIR consumers finish.
- Journal only replace_delayed_body writes. First complete original TransformationResult, including modified flag, is moved into journal. Repeated delayed writes never replace its original.
- Previously absent failed-root entries are removed. Warm/untouched entries remain. A regular entry first created during scope stays regular after its delayed replacement is restored.
- Normal/early exit and Rust unwind restore before transformer reuse. Process abort has no subsequent reuse; Drop is not claimed on abort. Exclusive borrow prevents overlapping models; scope misuse intentionally panics.
- Preserve regular/stub transforms, generated_loop_modifies and bindings. No cache.clear/fresh-transformer refactor. Both normal and failed-root delayed writers journal; both backends scope.

Portable regression ownership:8 compiler units (6 delayed_cache +2 delayed_scope), exact names/assertions in ORACLE-MAP.json. Controls: first snapshot/modified flag, warm/untouched/new regular entries, absent failed-root removal/repeated fresh scopes, empty scope, unclosed/unscoped misuse; normal/early return and panic-unwind reuse. Require actual nonzero6+2 atop prior20 targeted units and complete Quick (../ci/QUICK-PLAN.md). S4 historical cprover+llbc feature build passed; request fresh affected LLBC build from coordinator in addition to stock Quick. An uncompiled optional backend is NOT_RUN. No local build/CI in stage0.

Existing mixed-vs-isolated research/review basis:

- S4 baseline run43621472749 on ad324 + baseline-tests tree6bed3373b8 + overlay51b1707e71:18 comparisons,6 mismatches, additions only/removals0: immutable_legal+6, immutable_hole_negative+9, unrelated_legal_after_cycle+3, in each all_A_then_B/all_B_then_A selector order.
- Candidate run43621476331 on3b382 + overlaydb76eced8f:18/18 exact. Seven roots in both full orders (14 comparisons), plus cycle→legal and legal→cycle (4). Other four roots: ordinary_ensures_legal, pfc_legal, pfc_negative, cycle_root.
- Both captures say UNBOUND_CAPTURE / NOT_CHECKED_CAPTURE, producer_order ORDER_UNCONTROLLED / order_credit NOT_ESTABLISHED. Keep these limits; selector labels don't establish actual producer order. Accepted S4 implementation/units and coordinator CI-RESULT are historical source-reported evidence, not new independent proof credit.

S5 deliberately reduced exported end-to-end inventory/order coverage:7 split root-composition expected fixtures check per-root semantics. Standalone legal/cycle success does not prove shared cache isolation. Preserve structural units and mapping/hashes; don't recreate deleted JSON runners or allow additions-only matching. Fresh end-to-end shared-inventory comparisons would need a separately accepted bounded CI-only design; this plan does not silently add one or claim it ran.

Stage7 outputs: exact F7 source commit, REVIEW.md, source/parent/tree/manifest, CI-only overlay/request and observed counts/original exits. At head6 allow only pinned F7 residue. After7 require tree9829702c1aa0ecb73c860fc0ad5451757917d6cb, empty `git diff F HEAD`, equal modes/submodules/pins. Any other residual → STOP, including docs-only. Commit SHAs may differ; final tree may not. Recomposition and all new runtime results NOT_RUN.
