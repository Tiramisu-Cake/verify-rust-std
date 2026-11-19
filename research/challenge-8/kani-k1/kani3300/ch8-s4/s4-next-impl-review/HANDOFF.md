# HANDOFF — independent EXACT-PACKAGE REVIEW

**Verdict: APPROVE — the exact offline implementation package identified below.**
No blocking finding or required candidate change. All six constraints of plan
review `762a2a678eb624d1ddd18f0764a365e7787392c0` are satisfied within the
source/static review boundary. This approval establishes neither compilation,
native acceptance, cost fit, qualification, provider admission nor independent
proof credit. Final Validate remains **PREPARED_NOT_RUN**, execution count0;
its exact-byte execution and measured margin remain separate gates. Publication,
coordinator GO and native execution are separate stages. One stage complete;
**STOP with HANDOFF**.

Reviewed actual Git objects and clean candidate worktrees:

- Package `f485968493d3512f3e719825ef4490866808d120`, directory
  `research/challenge-8/kani-k1/kani3300/ch8-s4/s4-next-impl/`.
- Std `7b31b060b90ce286e94547993f6a698c549bc5fa`, tree
  `fccf3284bd678626c8f8cea72bbe6ec72964dbd9`; complete diff against its sole
  parent `8faf8e62af8f82b5c46af020086f8df591b6757e`.
- Control `65a9ea656a4b5f1e66f7b31eceffb5eefeba7541`, tree
  `09938d27a127351f5c51b6c9f451602d797a1c0f`; complete diff against its sole
  parent `3d3fb715271e3b195c6e0eee3557d5b0a6aad00d`.
- Stock tool unchanged `0aac16ef62da9e9d5645782d458593e5d78143ba`, tree
  `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`.
- Plan `c0de8471801ac22b38e3290c7a6b75742135af6b`; independent plan APPROVE
  `762a2a678eb624d1ddd18f0764a365e7787392c0`; network-r2 admission reference
  `8896f60ae9e0ea1c706c6b8693d00e2500190676`.
- Request SHA256
  `693e12689bfee859560d5042a36fd8b80051e9fca4082fd1a612642d7e389e30`;
  workflow SHA256
  `fc21d9f44a403b6294daaca2b25fdfcebe38d3dd7e89a927af0d289a86c177a0`.

## Findings against the approved contract

1. **Four unchanged negatives first — satisfied.** The complete first four
   request rows and their source bindings equal the control parent's objects,
   in order: checker_order_corrupt, checker_count_corrupt, sort13_weak,
   s4p_cell_count_corrupt. Their source files are byte-identical to the std
   parent. The new immutable r2 request/workflow fixtures equal the actual
   parent Git blobs. Exact intended FAILURE roles remain mandatory; Cell also
   requires S4_NEG_CELL_ACTIVE SUCCESS. An intended negative failure does not
   excuse any unsupported, U, safety, unwind or binding rejection.

2. **Actual target, domain and boundary paths — satisfied.** The complete std
   delta is the112-line `sorting_s4_full_lengths_next.rs` plus four registration
   lines under the existing cfg conjunction. N8/N9/N13/N17 use respectively
   literal `[1..9]`, `[1..10]`, `[1..14]`, `[1..18]` in snapshot, actual call
   and post. The import resolves to the unchanged production
   `small_sort_network`; each root calls it once with the original typed,
   stateless `KeyLess<u8>`. Each allocates independent arbitrary `[u8;34]`,
   copies the full pre-state and fixes base1. The only assume chooses an
   arbitrary outside canary; no byte mask, order/distinctness premise, padding,
   alternate callee or summary occurs. Every row is Original/null, production;
   variants, replacement unions and enabled summary edges are empty.

   In the unchanged helper, `no_merge = len < 18`: N8 inserts tails1..7;
   N9 calls actual sort9 and its zero-body shift entry; N13 calls actual sort13
   and its zero-body shift entry. N17 sorts the13-element prefix and inserts
   tails13..16, reaching span17. **N17 does not reach merge.** N18+ and all
   other finite lengths/types remain outside this package; no coverage
   interpolation or generic theorem follows.

3. **Full oracle, frame, roles and covers — satisfied.** Production/model/
   contract/old-harness tree entries are unchanged. Direct model inspection
   confirms full-u8 projection, owned pre-snapshot, equal lengths, adjacent
   sortedness and multiplicity queries for every input value. Equal total
   lengths make those count queries sufficient to exclude novel output values.
   The active guard requires the existing u8 sorting, span and pair models.
   Every root checks all34 frame indices plus an independently arbitrary
   canary over the complete outside set, including both allocation ends.

   The request binds all16 positive SUCCESS sites and24 covers to their new
   exact file/hash/line/source text. Per root, ACTIVE_CONCRETE_MODEL,
   SORTED_FULL_VALUE_COUNT, FULL_OUTSIDE_FRAME and ARBITRARY_OUTSIDE_CANARY
   require SUCCESS. Exact-length, UNSORTED, DUPLICATE, NONCONSTANT,
   MAX_DESCENDING and USEFUL_RETURN covers require SATISFIED. These are
   separate witnesses, with no input restrictions or claimed native branch
   trace. Fresh producer IDs remain UNKNOWN until the same native invocation.

4. **Unwind, flags and costs — satisfied, sufficiency/fit UNKNOWN.** Negative
   bounds remain34/34/34/36; every positive remains36. Request flags, budgets
   and the complete resource snapshot equal the reviewed parent and sealed
   plan. The unchanged argv builder supplies the row bound as default unwind,
   without explicit unwind/unwindset overrides; the unchanged stock resolver
   prioritizes CLI override, harness annotation, then default. No disabling of
   safety, overflow, undefined-function, assertion-reach or unwinding checks
   is introduced. Existing no-assert-contracts and experimental check settings
   retain their prior assurance limits.

   Source frame depth34, snapshot/count inner depths8/9/13/17 and maximum
   source sift depths7/0/0/16 do not establish lowered-loop sufficiency.
   Whole-child600 including compile<=180, slot720, local6GiB, outer12GiB,
   reserve2GiB and campaign6900 remain exact. The6180 envelope and720 reserve
   are arithmetic only. Native600-second fit, generated inventory/covers,
   resolved native argv, strict peak-memory assurance and speedup remain
   UNKNOWN. No historical timing or source-loop count is substituted for them.

5. **Edit scope and strict acceptance — satisfied.** Control changes add18
   profile/map/fixture/test files and modify only request, workflow, runner,
   check_package and collect. Removing the new dispatch reproduces all three
   shared Python files byte-for-byte from the parent. Every other old control
   tree entry, including all tests and protected runtime, is unchanged.
   The new campaign is an exact namespace transformation of network-r2;
   `expected_observation` and `validate_roles` ASTs are identical. New map
   traversal includes both r2 and the new module; the ordinary gate forbids
   replacements in both. Workflow changes are profile dispatch and ancestry
   depths source7/control9; old fixtures/profile depths and tool2 are retained.
   Required historical ancestors are within those depths.

   Complete rich/export inventories, precise role/location matching,
   safety/unwind SUCCESS, all feasible covers SATISFIED, ZERO_U/REJECT_ALL,
   unsupported-construct rejection, source/stage/target binding, protected
   snapshots and original exits/exceptions remain required. No old producer
   ID, merge-unreachable site, missing-location exclusion or strict0 rejection
   is converted into success. Initialization, ownership, Drop, panic, caller,
   provider, MIR and independent B1/B2 obligations remain open.

6. **Pins, manifest and prepared gates — satisfied.** Independently checked
   the package's59-file payload against its Git-bound manifest and exact
   package commit, every length/hash,173 control payload hashes, five source
   hash tables and15 dependency records including their Git blob identities.
   Actual HEAD/tree/sole-parent/clean state, request/workflow bytes and changed
   path inventories match. Independently replayed all four parent/stock
   patches through temporary Git indexes to the exact pinned candidate trees.
   The prepared final Validate still selects all366 old tests plus23 new,
   total389, with1080-second deadline and margin>=1.5 (elapsed<=720s).
   Its execution count stays0; elapsed and margin stay unmeasured.

## Independent checks and limits

- [STATIC-CHECKS.json](STATIC-CHECKS.json): Git/manifest/dependency/hash,
  preservation, ancestry, acceptance AST and exact patch replay checks PASS.
  The package's own read-only `check_packet.py` also returned
  PACKET_HASH_PIN_PASS. Historical stock source patch replay reports two
  inherited blank-line whitespace warnings; exact resulting trees match.
- [PLAN-SOURCE-CHECKS.json](PLAN-SOURCE-CHECKS.json): direct plan-to-actual
  literal call/snapshot/post, role/cover inventory, full domain/frame/canary,
  row-bound argv construction and exact resource-snapshot checks PASS.
- [PREFLIGHT.json](PREFLIGHT.json): existing
  `runner.verify_source(prebuild=True)` PASS, uncached,41.219s. All four
  maps were recomputed and equal the sealed JSON, with64 cfg projections,
  32 legacy contexts and8 ACTIVE contexts. Workflow gate PASS. This is
  static Python parsing/hash verification, without compilation.
- [TARGETED-TESTS.json](TARGETED-TESTS.json) and
  [OLD-TARGETED-TESTS.json](OLD-TARGETED-TESTS.json):23 new tests PASS
  (8.478s unittest time) and30 retained tests PASS (12.187s wrapper time),
  zero failures/errors. Retained tests comprise8 S4P2 routing tests and
  all22 r2 regressions under immutable old fixtures. Adverse cases cover
  call/snapshot/post lengths, restricted values, frame/canary, guard, callee,
  unwind, request identity, role/status/location/U/unsupported rejection,
  timeout, signal, partial/missing/null/wrong-type/NOT_RUN output and
  source-stage-target mismatch, preserving original exits/exceptions and
  protected snapshots.
- [MUTATION-CHECKS.json](MUTATION-CHECKS.json): in-memory mutants accepting
  wrong source/domain designs, accepting failed assertion/non-SAT cover roles,
  and losing runner cfg each cause the relevant new regression to fail.
  Candidate files were unchanged. This establishes test sensitivity, without
  executing the Rust implementation or proving its lowering.
- [DISCOVERY.json](DISCOVERY.json): all389 prepared tests are discoverable;
  full final Validate was **not run**. Targeted/preflight timings cannot
  satisfy its future exact-byte deadline/margin gate.

Only this review directory is added. No cargo/rustc/rustfmt/Kani/CBMC/native
tool, CI, push, coordinator/phase/ledger/accounting operation or raw verification
evidence access occurred. No subagents were used; the requested review was
performed in the main thread and the available spawn models do not include
Luna High. New qualified cases0; independently closed proof obligations0;
independent proof credit **NONE**. The approval adds no acceptance waiver or
execution authorization. Stop here.
