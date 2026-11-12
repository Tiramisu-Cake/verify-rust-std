# M2 — coordinator-only CI handoff, NOT_RUN

Source base `5abdcf982da6aff65662e198af27a9c776830a89`, tree `960a71c70b3f890b4f5cd2b53a83f6a0f8e00951`.
Candidate `5f7f2b7364135a0a8b7cfd86c43b4491a8911bac`, tree `b2bbb7366a9fbac33398fb01be7300f83a1d27bd`.
Local clone `/root/kani-fix-3300-m2`, branch `experiment/kani-3300-m2-qualification`; Kani NOT pushed.
M1 production unchanged `254ae69662b3206cd4432dae0cd44c534b1b13fb`; test delta is exactly eight added files,
four sources/six harness selectors under tests/expected/uninit/transfer-qualification/. Exact SHA256 in TEST-MANIFEST.json.
No workflow, runner, source model, contract ABI, dependency or check-setting change. Worker Cloud $0; no dispatch/wait.

## Ordered request using existing authorized Quick process

1. Existing static/preflight/fmt/build/clippy, keeping original exits. All new files request --edition2021 and -D warnings.
   No local compiler was run. Setup/compile failure is not a harness result; later stages stay NOT_RUN.
2. First targeted new selectors below, then paired legacy legal/frame/requires/false/typed/Move controls in QUALIFICATION-MAP.json.
   Use ordinary --emit=mir/property inspection in the existing process when binding is incomplete; no new runner or adapter.
3. Run unchanged D0 legal pair, call-pairing all6, argument-return, argument-buffer, four Item-return plain/seeded,
   typed-transfer-data all6 and all typed-*-padding/partial-data, contract-frame/clause and call-move all13.
4. Then existing complete Uninit Quick. Preserve all existing checks/controls, including raw-eq-uninit, reset/overwrite,
   immutable-masks and promoted-only controls. Existing unit immutable_allocations step remains; no source-repair omission.
   C1-T2 mixed fixtures belong to owner15 and are not imported into this base or changed here. Keep their runs/results separate.
5. Goldens are semantic expectations, identical under the same model/test delta; do not replace a legal SUCCESS with
   a baseline false FAIL or use an earlier Unsupported as a desired negative. M2 is pure qualification, not a new model fix.
   If a pre-M1 differential run is desired, coordinator must compose the SAME test delta on its authorized baseline;
   this worker neither prepared a replacement baseline tree nor requested extra infrastructure/dispatch authority.

| File selector under transfer-qualification/ | Harness | Required outcome and binding |
| --- | --- | --- |
| legal-pair.rs | legal_ordinary_transfer | SUCCESS of original target body, true-selected scalar7 read, written array destination, both immutable-equality operand checks and useful assertions |
| legal-pair.rs | legal_pfc_transfer | Same initialized behavior plus ensures and legal modifies(out) frame SUCCESS; private shadow writes must not cause frame failure |
| postcondition-hole.rs | postcondition_reads_returned_hole | Reached uninit u8 FAILURE in ensures assume_init_read; select false arg2 -> return0 chain; no early Unsupported/frame/validity failure |
| out-pointer.rs | out_pointer_fully_written | full=true; offsets0,2,1 written, normal return, legal assume_init and all11/22/33 assertions SUCCESS |
| out-pointer.rs | out_pointer_preserves_middle_hole | full=false; offsets0,2 checks/assertions SUCCESS; intended offset1 u8 read FAILURE, no blanket pointee blessing |
| normal-abort.rs | normal_return_or_abort | Only expected panic FAILURE on true branch; false normal return0/read7/assertion SUCCESS; no executed normal update/return0 load on true abnormal path |

## Exact inspection queries and acceptance

For each selector retain exact full source/test/tree/toolchain/target/solver/bounds/flags identities and original stage exits.
Actual property IDs/classes/locations/status/reachability start UNKNOWN. Return a complete relevant property inventory;
for negatives list *all* failures, successful companion checks and any unreached/unsupported operation.
Compile success, expected substring or overall FAILURE alone never accepts a row.

- Legal pair: bind consumed MIR select signature, true branch a=7 versus b=false, original shadow indices1,2/count2,
  StoreArgument snapshots -> any Move clearing -> entry LoadArgument -> selected source-following branch -> return0/count0.
  Numeric signature equals actual monomorphic function Ty::to_index at each paired boundary, never a guessed stable ID.
  Join array byte writes -> assume_init normal destination setter -> native equality/raw_eq specialization -> both CheckAs operands.
  For immutable RHS record actual origin/Some×3 mask before zero fill, symbol/cache-hit mapping, emitted layout, live object,
  offset/extent and matched post-reset seed. Literal syntax or legal PASS does not prove the immutable path.
- PFC legal/old frame/old requires/new ensures: bind actual target/root/closures and private assigns symbol;
  require reset completion -> seed -> first effect and clause-depth reset -> init_contracts -> first dispatch.
  Frame violation must be the user outside write; requires negative must be its clause read; ensures negative must be its own
  first read at postcondition-hole.rs:14. No earlier typed invalid value or opaque contract error qualifies.
- Out-pointer: bind live MU<[u8;3]> object, caller base/offset, callee writes and bool branch to exact three-byte range;
  returning pointer/unit does not initialize unwritten bytes. On partial path prove intended final read sees false byte1,
  with both endpoint read checks and value assertions reached SUCCESS. Outside-object neighbor remains unprobed.
- Normal/abnormal: inspect return_or_abort true panic CFG and reached panic property; prove absence of execution of
  callee Return/return0 store and caller normal-target load/set on that path. On false path require initialized7 normal return
  and its read/assertion SUCCESS. panic=abort is required; real unwind NOT_COVERED, no custom simulation.
- Legacy protocol: exact indices1/3/5 vs gaps2/4, counts3 (not5/6), nested/repeated calls, Item plain/seeded actual kind;
  zero return/count0 and distinct function signatures. Bind false source-following alternatives, not optimistic destination state.
- Legacy typed/raw/Move: actual Padded layout assertions/stride/masks, raw extent8/16 vs typed D(T), false data7/15,
  snapshots before any Move reset; no claim existing normal custom MIR covers unwind.
- Registry/reset closure: bind every actual ordinary/PFC/generated reset body after producer/contract/quantifier closure,
  all original false/buffer resets before seed, no intervening user effect, no per-reference reseed. Source presence alone is insufficient.

Missing/partial binding => UNKNOWN. Any new failure, lost required check, lowering mismatch or unpaired transfer => STOP acceptance.
New runtime/compile/property outcomes are NOT_RUN. M3 requires later coordinator acceptance, not this READY.
Report only via authorized evidence interface; no raw/full-log/archive fallback. Do not rewrite historical M1 observations.
