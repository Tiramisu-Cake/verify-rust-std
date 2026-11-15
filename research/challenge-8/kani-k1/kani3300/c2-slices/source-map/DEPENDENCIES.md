# Source dependencies — stage0 / worker14

The fixed production order is **U → existing B1 → 1 → 2 → 3 → 4 → 5 → 6 → 7**.
B1 is a pending upstream dependency, not a merged upstream base and not a new duplicate slice.
Source SHA/tree/commit timestamps: `INPUTS.json`; upstream/fork observation timestamps: `UPSTREAM-SNAPSHOT.json`.
`DEPENDENCIES.json` gives the exact source-hunk parts for each owner; `SEAMS.md` explains shared symbols and adaptations.

| Head | Required source prerequisites | What must stay together | Qualification still required |
|---|---|---|---|
| B1 | U | Existing resolution/one-walk/common flush/no-body guards. U→B1 is immutable history, not a rewrite. | Existing submitted PR checks are not C2-head qualification. |
| 1 ANALYSIS | B1; U checked_body/tail-call/atomic fixes | Registration selected bodies + provenance + Result/error/cycle traversal + ordinary entry seeding. Resolver tcx signature with all consumers. | Full baseline/B1 uninit/delayed-UB + full FunctionContracts/function-contract + ActiveCalls9 no-regression. Integration on4/5 is PENDING. Captured-closure regression risk remains open until reached observations. Final MU fixtures do not automatically run here. |
| 2 IMMUTABLE | 1; U reset/private-state markers; **borrowed minimal layout qualification helpers** | Anonymous origins/graph/targets, descriptors+F5, emission bind/static/prepare/finalize+seal. Helper/export/recognition/for_storage belongs2, not4. | Immutable aliases9 and admitted/hole/disallowed origins at this head. raw_eq remains unsupported until3; closure layout remains baseline until5. |
| 3 LAYOUT-RAW | 2 | Pat/enum offsets, complete-byte raw_eq on both operands, both relevance seeds, shared reference CheckAs reborrow. | Padding/extent and promoted-RHS controls. Never bring closure5 or protocol4 as neighboring context. |
| 4 STORAGE | 3; recognition/raw storage qualification helper from2 | Operation enum/builders/tcx plumbing + runtime masks/snapshots/pairing + caller/callee/return0 + Move/deinit + F6 + exact Hook exclusion. All const mask/SetStorage and unsized guards here. Projected raw/address behavior moves here for MU correctness. | Paired legal/false/Copy/Move/reset/F6/hook controls and argument_size/marker units. Captured strong contract tests may additionally need5. |
| 5 CLOSURE | 4; offset fixes3; imported internal context2 | Sized zero-byte closure + monomorphized upvar offsets, no broad admission. | Ordinary/PFC captures, eight strong oracles, seven modes/seven roots where applicable; exact test allocation worker15. |
| 6 E1 | 5; mask/setter/deinit/guards/projected-raw already4 | No production residual: V420–424 belongs4 under accepted variant C. Edge qualification/docs can remain6 even when their production prerequisite moved earlier. | All E1/composition controls and complete final pre-F7 source residual. No unsafe gap left for this head to repair. |
| 7 F7 | 6, then worker15 sole writer | Journal/API/RAII + two backend scopes + both delayed write sites/import atomically. Preserve immutable lifecycle2. | Delayed-cache6/scope2 and cumulative Quick. Final exact F tree required after7; no inherited intermediate Gate A credit. |

The important directed edges, excluding cumulative ordering, are:

- B1 resolution+flush → 1 selected-body/cycle handling → 2 target traversal → 3 raw_eq → 4 typed storage.
- U reset/private-state marker → 2 immutable finalize; extended runtime4 is **not** a prerequisite of2.
- 2 qualification helper → wrapper recognition → raw-storage layout → existing U data_bytes_for_ty.
- 3 Pat/enum offsets → 4 typed masks → 5 closure capture masks.
- 4 constant_init_mask + SetStorage + for_deinit → 4 ordinary-union constant assignment; E1 tests6.
- 4 projected raw/address guards → 4 storage assignments/loads; moving these to6 would leave an unsafe intermediate.
- 1 delayed failed-root/normal writes use exact pre-F7 cache forms until7. Final F7 API is not introduced early.
- 2 immutable prepare/finalize and7 model scope share one compiler_interface function but own disjoint hunks.

The two earlier-ownership refinements are explicit in `SEAMS.md` and require the coordinator's stage0 map review
before implementation. They preserve the accepted PR order; they do not create extra features or authorize changing F.
If the coordinator retains every storage helper in4, there is a literal unresolved2→4 dependency through
`immutable_origin_type_supported`; stage2 must STOP rather than stub/copy/rewrite that predicate.

If1 reaches a new ordinary contract/layout regression before5, STOP with its exact fixture/hunk and minimal
closure prerequisite proposal; no test removal/ignore/golden update, no silent PR reorder. This static map does not
claim that regression occurred or that an intermediate is green. Tests/oracles/docs must be joined from worker15
before the coordinator accepts combined stage0; worker14 does not accept that parallel map.

Before7, permitted residuals are **only** owner7 F-hunk parts in `DEPENDENCIES.json` plus the three exact pre-F7
import/writer adaptations in `PRE-F7.json`. After7 every source part is consumed once; the **entire** tree,
including worker15's tests/docs paths, must match F `9829702c1aa0ecb73c860fc0ad5451757917d6cb`.
No slice head, patch application, recompose tree or CI overlay was created by this stage0 research.

## Accepted dependency decision for stage1

TASK @`4fef62ad67`, variant C supersedes stage0 review-pending language above.
Recognition/for_storage helpers stay2; all projected-raw guards and exact V420–424 part move to4; E1 has no required production residual.
Head1 is `NO_REGRESSION`, integration `PENDING` on heads `[4,5]`: no new non-MU fixtures, no golden weakening, no early closure/storage prerequisites.
Head4 closes owner1 DAG/cycles/root-order and ordinary payload/padding; head5 closes ordinary positive/capture-free and all mapped contract/strong/mode/root obligations.
Nested Pat/enum/raw-eq-uninit integration of owner3 waits4; generated-modifies-no-shadow waits5.
Stage0 findings are static dependency observations, not failed runtime runs. Canonical updated parts are in JSON; stage0 pins remain available at bf455494e4.

Slice02 correction (coordinator run43699468860): InitialTargetVisitor's trait impl
lifetime at F77 and deleted baseline impl at B1:68 move3→2 with the generic struct/
inherent impl/constructor/caller. F76 raw_eq comment remains3. Canonical map and
generator split B1--F:14:006 by line; no other feature ownership changes.
