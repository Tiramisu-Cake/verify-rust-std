# Qualified guard / canonical Drop — session closed, compile preflight blocked

UTC start **2026-10-10T10:21:50Z**, main deadline **12:21:50Z**, absolute deadline **12:51:50Z**. No Cloud Builds began after main deadline. Owner steering during finishing paused new functionality/layout/glue and explicitly permitted local OCaml compile/type checks until absolute deadline. No automatic new session. Policy `c7ca8c467aecf10a4b53039372ee97714f854ee3`, adoption `1b9e3df3182d13e5adf7d2e5d04afcfbc1851f14`, ACK `aec832ab25ba65a5ddc643ca325f8d8ea8b2b612` retained.

Assigned project `/root/verify-rust-std-merge-origin`, branch `merge/incoming-origin-20261009`, git-dir/index `/root/verify-rust-std/.git/worktrees/verify-rust-std-merge-origin[/index]`. Tool `/root/verifast-merge-incoming-span`, branch `merge/incoming-span-lifetime-20261009`, git-dir/index `/root/verifast/.git/worktrees/verifast-merge-incoming-span[/index]`. Initial project `aafa61c4145c8721bbd095e100d292b8da1c1b81`, tool `8cb0121b03a5164495bf0d7c6c236ea9504d5ce4`; own newer history preserved. No foreign process/worktree/pin/ledger changes, Actions, runtime std edits, upstream publication or maintainer integration.

## Candidate and compile outcome

Last exact Cloud proof = infra **60c07f9d381b44c35e43f4cc97e1641b65dd2b1d**, tool **ee54a8a2406f1eb39cd277d39afe4e656f5c9300**, Build **2200d07f-3de4-4dd8-b79d-12ce46898913** FAILURE. Config SHA256 `8ad77d4693037512b4ed12eed5b9208f5daa8f644b5648f277b4ae7362a1fd38`, source-input SHA256 `ea4317b88ac0bd633650d8510a31b346d1261265fa1240c0d4098921dbcabd1d`, verified archive `ee478395656eb0c19eec1ae2ef5b2ef4ad05cf47cce76f4e212fa21a0fbe1f51`. Exporter compilation/link and decoder generation pass; console compilation stops at pointer-width getter type mismatch before target proof. All seven new Builds have **target proof NOT_RUN**, not intended negative proof outcomes.

Corrected tool **e8a77a29666fce5b9401d81deede3ec40f3b54bc** removes only redundant `Stdint.Uint8.to_int`: pinned `pointer_width_get` returns `int`. Qualification and contracts unchanged. This candidate is **NOT_FRESHLY_COMPILED / CLOUD_NOT_RUN**. Portable `guard-layout.patch` SHA256 `661abc823cc9ecb81fa1ffaabe3ed2d6b61f7416204bfa3cfcd020f48b8058d8`; translator SHA256 `858a4559bbe115a39bdd0cb9840a87f83598edd465e8da2a439740a3115136c0`; schema `bac5f307bb74f0e98efeebfe67649639666ec4a9e38c3cb8bcb60a3259fe31f9`. Exact remaining source pins in [LAYOUT-PINS.json](LAYOUT-PINS.json) and [PROFILE.json](../../merge/overnight/guard-ownership/insertion-onecell/PROFILE.json). Profile **experimental-merge-qualified-guard-onecell-v1**, **NOT_ACCEPTED / NOT_FOR_INTEGRATION**. Corrected candidate PROFILE.json SHA256 `8997ecd08a06dba03d1b82a32676b7bbcd8ccf6b729768de072833fb941f9d9c` (not a fresh profile-build receipt).

Preserved compiler failures and fixes: Rust exporter API/type mismatches corrected against pinned compiler; LLVM native search set to that compiler sysroot/lib; unsupported primitive UInt64 list schema replaced by canonical decimal Text lists; redundant out-of-scope tparams/lftparams conjunction removed; `IntAux.Uint64.to_string` corrected to `Stdint.Uint64.to_string`; concatenation constructor qualified `Ast.ReprC`; redundant Uint8 conversion now removed. No guards/contracts weakened. Entire six-file OCaml delta independently reviewed: AST, both serializers, translator, model and kernel; no further concrete static blocker identified. Review does not establish compilation.

## Local OCaml preflight

**BLOCKED_DEPENDENCIES_AND_RESOURCE_PRESSURE, compiler NOT_RUN.** At 12:24:03 UTC VPS has 1967 MiB RAM, 387 MiB available, swap 3911/3915 MiB used, disk 194 MiB free (100% used), load 9.99/17.02/20.51, active swapping. At 12:28:34: available RAM253 MiB, swap0 MiB free, disk190 MiB free, load13.00/12.11/17.37, active swapping. No compiler job started; owner's resource stop criterion applies. OCaml/Dune/opam/capnp/compatible generator not found in PATH or targeted dependency locations. `ocamlc -version`, `dune --version`: command-not-found. No installation/bootstrap or foreign process intervention. Compiler elapsed time and peak RSS **NOT_MEASURED**.

Exact discovery commands, modules reviewed and scope of the explicit owner exception are recorded in [SESSION.md](SESSION.md). Project Dune dependencies are real stdint/capnp/ppx_parser/frontend/vf_mir/vf_mir_decoder, with schema-generated modules; no stubs or stale local cmi were substituted. Prepared Cloud-only next compile stage and commands are in [COMPILE-PREFLIGHT-RECIPE.md](COMPILE-PREFLIGHT-RECIPE.md); preparation is not dispatch or compile credit. Minimum order: changed exporter → generated schema/decoder and translator → changed model/kernel compilation → minimal end-to-end source/MIR/AST proof case → scoped origin/layout/recovery regressions and mandatory retained-six/exact-combined smoke. Do not add natural Drop/glue before applicable canonical interface proof.

## Semantic sources and separate verdicts

Implemented candidate extent/alignment comes from the **same pinned compiler** `layout_of` for exact local nongeneric guard DefId/instance/source and x86_64 64-bit target, checked qualified shape; decoder/translator/model connect it to the verifier's own `sizeof`, `alignof`, field-offset and thin-pointer terms. This is an implementation proposal, **not a fresh established guard theorem**. Separation proposal uses validated actual live allocation receipts, supported positive extents and actual reference/chunk identity; retirement on StorageDead/free cleanup, not variable names or numerical address inequality. It adds no own/FBC/pointee authority. Cards and independent addressed reviews are retained.

Supported candidate domain: exact source-qualified concrete-u64 guard and supported positive live scalar/pointer storage on x86_64. Generic guards, ZST separation, unrestricted comparator/user-Drop and compiler monomorphic MIR claims remain unsupported. Caller must construct existing mutable fields/padding/FBC, source permission and CURRENT source value, destination gap/option, u64 ownership/type interpretation and len==1; these are still explicit resource obligations in unrun fixtures. Source/destination payload nonoverlap remains an explicit resource/geometry obligation. No supplied positive guard size or root/source interval separation was added. Historical count-n strong req keeps its supplied root geometry clauses; omitting them in the new len1 helper does not prove old count-n applicability.

| Obligation | Verdict |
| --- | --- |
| Historical bounded half-FBC CURRENT normal copy/recovery, full posts/return/leak | RETAINED PASS_FRAGMENT_ONLY on previous profile |
| Historical specialized strong-pre Drop body | RETAINED CONDITIONAL PASS; own=false compatibility vacuous |
| New len1 strong-pre body | NOT_RUN |
| Nonvacuous canonical Drop interface | NOT_RUN; explicit nonempty own/effect candidate only |
| Actual compiler Drop/glue application | NOT_RUN / lowering unimplemented |
| New canonical/caller normal recovery/posts/return/leak | NOT_RUN |
| Actual panic/unwind cleanup | NOT_EXERCISED |
| Changed-profile regressions and mandatory smoke | NOT_RUN; historical successes retained separately |
| Synthetic/saved classifier/parser replay | PASS_SERVICE_ONLY, no fresh proof |
| Combined profile / integration | NOT_ACCEPTED / NOT_FOR_INTEGRATION |

First blocker: obtain a **freshly compiling exact candidate**. Remaining compile errors beyond corrected pointer-width getter are unknown until real compilation. Next step in a newly authorized window/budget: execute the prepared build-first stage with pinned real dependencies and corrected e8a77a29 candidate; only after it passes run minimal exact end-to-end and canonical applicability cases. Existing natural caller draft remains inert, no new glue changes.

## Accounting

Owner merge, v2/max2 preserved. All seven terminal Builds fully accounted and archives/text chunks verified. **CLOSED 2662/3600 Cloud seconds; 938 unused closed**, no carryover. Closure observed12:31:04UTC. Own active/unresolved/reservations empty and ready request withdrawn through existing client; no unresolved ID/token remains. The previous1099 closed seconds remain separate. Full timestamps, proof/infra IDs, tokens, config/source/archive hashes in [BUDGET.json](BUDGET.json). Documentation/recipe changes after the last Cloud proof are **not a proof run**.

| Build | Proof = infra | Seconds | Status |
| --- | --- | ---: | --- |
| 2105d916-4b03-432e-abe9-ea36e994034a | dbd2b4b16df4bac15eb3eea7e3b2778055a9b2fb | 353 | FAILURE |
| 970fa776-c573-4d1e-bf7e-792d526dc4a5 | 9bc78de7848f28b11d408790f054acf1116a66b4 | 344 | FAILURE |
| 16be672d-ae39-48fe-b71c-8a5ea27cb0e6 | cc4cd43b8e0c3fcbfe5015a99021cb1f59cf582f | 360 | FAILURE |
| a645e3b6-c422-44ed-a3bf-3ce74ab30bee | 2a9a4300114de9122353f03fb641aecdbdcbb15b | 431 | FAILURE |
| e273a620-550f-44a9-987e-3e64eaa64277 | ba37caf2dc0c8de186ffd7de0968755b620aa973 | 375 | FAILURE |
| 2888a14b-6833-4200-8512-15c8e26835c9 | e7984c8f475ef5fdae4fd64b615dca7369e30261 | 404 | FAILURE |
| 2200d07f-3de4-4dd8-b79d-12ce46898913 | 60c07f9d381b44c35e43f4cc97e1641b65dd2b1d | 395 | FAILURE |

## Previous closed checkpoint

# CURRENT recovery / one-cell Drop — session closed

Observed UTC start **2026-10-10 00:34:48**; main deadline **02:34:48**; finishing deadline **03:04:48**. Account closure observed at **02:37:34**; finishing inspection/publication follows within the limit. All Builds were submitted before the main deadline. No new experiments after it and no automatic next session. This section supersedes the historical checkpoint below.

Policy `c7ca8c467aecf10a4b53039372ee97714f854ee3`, adoption `1b9e3df3182d13e5adf7d2e5d04afcfbc1851f14`, ACK `aec832ab25ba65a5ddc643ca325f8d8ea8b2b612` verified; no retransfer. Only assigned project/tool worktrees were changed. Runtime std, frozen tool semantics, final consumer contracts and foreign pins were unchanged. Compilation/extraction/proof ran only in Cloud; saved-data classifier/parser/audit replay is service evidence. No Actions or upstream publication.

## Recovery result

First derived refusal is full-FBC existential field identity abstraction: Build `6fb5bd55` at `f76536a6` cannot derive `src == held_ref` immediately after FBC/own open, before copy. An annotation-only half-FBC precise field frame preserves the existing witnesses and resources. Build `61eb1905` at exact `a98404d718dedf183eaa7431ac05060d9e45010e` proves all seven identity/quarter assertions, source-linked concrete-u64 literal-one copy, CURRENT recovery, full normal posts, return and leak (0 errors, 216 statements). Later builds repeat this result. The after-recovery false control reaches its intended assertion; duplicate physical FBC fails at its missing field. `missing_held_owner` is N/A for empty u64 own.

Fraction-only sufficient repair was falsified. Copy preserves the required quarter and the actual helper/token arguments match in this bounded domain. No ref-token lifecycle, alias or provenance semantic defect is established. No new points_to, restored authority, address-derived permissions, supplied separation or entry snapshot was introduced. This precise read-only field frame does not establish a mutable actual Drop caller. Actual panic unwind is **NOT_EXERCISED**.

## Drop and candidate gates

Latest fresh proof/infra **`739b261ffc3ca688f6ebc3306bff0766be0feaf6`**, Build **`1f2f9442-25e8-466b-ba77-ea508795e9b0`**, create `02:26:33.712410283Z` → finish `02:33:08.937667Z`, 396 charged seconds. Archive **`01bd254c68e8e94a945309c0f6797929ec3d06d3d41e163dcf6917256d8c114a`** and full text chunks integrity-verified. Exact config `d18743ca2d87a03be2240bc85a5d2e7468d172d7da4564850430cc3f27852cc7`; token `dispatch-f360877570cb426ba9d0eb47084ece06`.

Tool **`8cb0121b03a5164495bf0d7c6c236ea9504d5ce4`** is unchanged. Profile **`experimental-merge-origin-layout-concrete-u64-v1`**; source baseline `f76012fb518703b1d98e243ac4f487f16877cfcb` plus frozen checked patch chain. Full source/compiler/schema/file/binary/profile receipts are in EVIDENCE.current_session, PROFILE.json and LAYOUT-PINS.json. Actual SmallSort SHA256 `85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`; actual CopyOnDrop block SHA256 `caff1edbfa3a8d9fd29459e49c43abd0f8f987f9061c75e7bf6ecedbbba26a6a`.

The mechanically specialized source-linked Drop body passes its explicit strong precondition → full normal posts/return/leak (47 statements). Default guard own is false, so safe-prototype compatibility is vacuous; this is **conditional body proof**, not actual compiler-monomorphic callee or Drop/glue credit. The direct first-body false and canonical prototype false are intended negatives; canonical first-body false is blocked earlier and remains INCONCLUSIVE.

Two isolated derived repairs pass: typed-storage roundtrip conserves root fraction/value and derives alignment; destination limits, endpoint, option capture, empty-tail/singleton array closure and unchanged `DST_PRE` pass. `dst[..len] |-> _` is possibly-uninitialized `array_`; older initialization explanations are superseded. Remaining independent refusals: root/source interval separation at lib102, and the reached `call()` at lib100 fails its strong req `0 < sizeof(CopyOnDrop)` at lib28. Archived JSON's `canonical_prototype_before_body` label is coarse; full logs establish the specific positive-extent call-precondition refusal. No old receipt was rewritten.

Origin/resource/span and unit/scalar component gates matched in their stated domains; 14 layout controls, native C/C++ return/leak and compiler receipts retained. Mandatory **retained six-profile smoke PASS** and separate **exact combined-candidate normal/unwind smoke PASS**. Strict eight-case **outer bindings valid**, independently replayed; nested receipts alone were not substituted for outer checks. Component evidence is complete for internal review only. Combined profile **PARTIAL_DIAGNOSTIC / NOT_ACCEPTED**; integration **NOT_FOR_INTEGRATION**. Whole insert_tail, actual Drop/glue, actual panic unwind, generic/ZST/caller/comparator/user-Drop remain OPEN; unchanged generic reproducer **NOT_RUN**.

## First remaining blocker and next step

Canonical FBC/own does not expose qualified positive root extent or root-to-payload interval separation. Actual tmp/guard AST establishes live-local sequencing and `src` lineage, not allocation intervals. Next read-only audit: determine whether existing frozen live-local/reference-origin/provenance rules derive those facts for actual tmp and gap_guard. If not, retain these minimal source-linked refusals and define a separately reviewed, source-qualified caller/interface relation before implementation. No guessed guard size, positive-size premise, separation premise or assumed generic drop_in_place effect is justified.

## Account and continuity

| Build | Exact proof = infra | Charged seconds | Cloud status |
| --- | --- | ---: | --- |
| a86c1c7c-4393-4553-92df-9bafb665b733 | 4639c615f489f33c1cb0b527cba999f0dbc00345 | 89 | FAILURE |
| 6fb5bd55-4c71-4764-8bc0-0d5d1c97ac6e | f76536a6890b8be85d8aa5f502abde76d48d0829 | 398 | FAILURE |
| d642e649-94d3-41d6-91ff-52185f019c33 | 3060ce17e85feb48cc57f97efe3184a61efcf0ca | 393 | SUCCESS |
| 61eb1905-3d30-4a6e-b4f4-43dfcb50995d | a98404d718dedf183eaa7431ac05060d9e45010e | 386 | SUCCESS |
| c451ed14-505f-49c3-8e88-82664b9aafa3 | 3a3a70e7803bc275b381ba4af1133c6cae1d7662 | 396 | SUCCESS |
| ac238e6a-59b9-4573-989e-54144b71bc1b | eccfd6d5ca969a8e8ecdc2da632b9ad134f625be | 443 | SUCCESS |
| 1f2f9442-25e8-466b-ba77-ea508795e9b0 | 739b261ffc3ca688f6ebc3306bff0766be0feaf6 | 396 | SUCCESS |

Account **CLOSED: 2501/3600 Cloud seconds**, including setup failure; **1099 unused seconds closed**. Old account 2136 seconds and its retired 1464 are separate. Seven terminal builds are accounted and every archive/text index/chunk verified. Own active/unresolved/reservations empty; ready request withdrawn through existing v2 client. Coordinator schema2/max2 and peer accounts were not manually changed. Codex usage data, including subagents, is unavailable from routine session tools; Cloud seconds are not Codex usage.

Final documentation HEAD differs from fresh proof/infra and is not a proof run. Portable internal review packet is published only to the own project branch. No maintainer integration, foreign pin update, tool/upstream push or automatic continuation.

<!-- END CURRENT SESSION -->

## Previous closed session retained for continuity

# MERGE session checkpoint — closed, not accepted

The session started on 2026-10-09 at 21:53 UTC. Main deadline: 23:53 UTC. Account and evidence closed on 2026-10-10 at 00:04:48 UTC, within the finishing-only limit of 00:23 UTC. No new Builds began after the main deadline; no automatic continuation.

Policy `c7ca8c467aecf10a4b53039372ee97714f854ee3`; adoption `1b9e3df3182d13e5adf7d2e5d04afcfbc1851f14`; ACK `aec832ab25ba65a5ddc643ca325f8d8ea8b2b612`. Branch-local history was preserved. Absolute assigned paths, branches and distinct git-dir/index identities are in EVIDENCE.json.

Latest fresh proof/infra: `ba37cbfee25aa0e1e1270f95421391f02f358cfd`; Build `fa5a4fd4-3b96-4876-9e36-03b1ca46089d`; terminal FAILURE, 369 seconds. Archive `05b3be833db21c9ee7525352d5cf553acc9b89883d64f43e85c923a1907be5da` passed integrity verification. Tool `8cb0121b03a5164495bf0d7c6c236ea9504d5ce4` over `6cb7b6736c4ef7978d2f3a80737952ac7148cccb` remains NOT_FOR_INTEGRATION. Cloud source baseline `f76012fb518703b1d98e243ac4f487f16877cfcb` plus the exact frozen profile patch chain is bound to the candidate source hashes. EVIDENCE.json and PROFILE.json record full source/file/binary/compiler/schema pins, six runs and costs.

Applicable origin controls passed fresh: ordinary calls and divergers, event provenance/local binding/ordered CFG regions, full normal/unwind resource positives and targeted missing-resource/StorageDead negatives. Lost authority remains lost. The canonical-unit shared sizeof=0/align=1 correction and nonnegative Rust struct bound pass fourteen controls; C/C++ behavior is unchanged and both native smokes reach return/leak. Compiler observations agree on the qualified unit/u64/wrapper domain. Arbitrary generic storage extent remains unsupported; ZST addresses may coincide. Independent review is recorded separately.

The concrete source-linked tmp/ManuallyDrop/read/guard witness derives src/dst geometry before/after canonical FBC and executes literal-one copy plus CURRENT source/destination assertions. Its first remaining failure is unchanged with exact-quarter own: aliasing.rsspec:50, caller:92, missing `[(1/2*1/2)]points_to<u64>(held_ref, _)`. The coefficient-only repair hypothesis is insufficient. Pointer/value identity loss remains a hypothesis; no lifecycle semantic defect is established. Full recovery/normal posts/return/leak and the after-recovery false target are NOT_REACHED. Actual unwind is NOT_EXERCISED. Missing-held-owner is NOT_APPLICABLE for empty u64 own. Actual Drop/glue and full insert_tail are not proved.

Mandatory profile smoke is NOT_RUN after the retained cold matrix timed out at 126 seconds. The root combined audit is INCONCLUSIVE / NOT_ACCEPTED. Nested artifact receipts are valid, while the outer onecell artifact-binding flag remains false. Broad accepted profile and foreign pins are unchanged.

After a newly authorized session/budget, the next technical control is a derived entailment ladder, with no supplied premise: immediately after FBC/own open, assert `src == held_ref` and exact quarter permissions at both addresses; after copy, assert `recovery_src == held_ref` and exact quarter permission at held_ref before end_ref. Inspect the first failure to distinguish FBC identity, alias/provenance/coercion, copy preservation or ref-token lifecycle. This control is NOT_RUN. Separately provide adequate cold-matrix/profile-smoke time and reconcile the outer aggregate binding before any combined acceptance. Qualified guard layout and an actual Drop/glue effect bridge still require justified implementation/review. No assumed summary or readonly transfer through an arbitrary comparator is available.

Account CLOSED: 2136/3600 seconds, unused 1464 seconds closed. Six Builds are terminal and accounted; every archive is verified. Own active/unresolved/reservations are empty; ready request withdrawn. Coordinator v2/max2 and foreign accounts were not changed.

Draft status: the portable unit patch and concrete consumer/control infrastructure remain experimental; recovery still fails. No generated/injected source, downloaded logs or build output was committed. No upstream publication or integration. Final documentation HEAD differs from the fresh proof SHA; it is not a proof run.
