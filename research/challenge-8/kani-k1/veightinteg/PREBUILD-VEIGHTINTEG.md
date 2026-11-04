# VEIGHTINTEG — exact pre-build packet

Status: UPDATED FOR REVIEW; no VEIGHTINTEG build dispatched.
Coordinator conditionally authorized one build after coverage-only corrections and a free slot.
Request owner: k1-merge, after PERMTAGS G2 `8c10dc52-3e39-4b07-800f-0c1d3aad4888` finishes.
k1-network is occupied by ENSURES `6d95823e`; use it if coordinator reports it free earlier.
Slot watch uses separate K1_CACHE `/tmp/veightinteg-k1g-slotwatch`; end turn after watch.

## Identity and library commits

- Worktree: `/root/verify-rust-std-kani-veightinteg`.
- Branch: `experiment/kani-k1-veightinteg-20261105`; task commit `6088054699`.
- v8 library base: `56efe5c477ded5bc06a975f6a843822d09100894` (204 ordinary, 8 controls).
- Task branch base: `5378a0ba00`; upstream library comparison: `233f96f66a`.
- Tooling base: `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; lane files unchanged.
- Kani pin: `cd355b0bccd32300713bc2ce4f765dafa1510607`; nightly `2026-10-22`.

| Library commit | Content |
| --- | --- |
| `fa6a1d3142dd7463ffe35ab51e24a54c7ad470e6` | Real-helper contracts and matched PFC/consumers |
| `f351bbc1c61fe7397006d713db7e0e7de9c3bfb5` | Identity tags N9/N13 and type routes |
| `aa2a7347511350ae4a855352595d4bdd12d5ff48` | Stable u64 N2 minimal scratch |

The original three commits are library-only and carry `[skip ci]`; research is separate.
Coverage-only follow-up: `4b4803b126638b7ece733076ceb7361b653c98b9` (also library-only).
Runtime functions/contracts and all assertions, assumptions, data and domains are unchanged.
Sources are only our authorized REALCONTRACTSTWO `588c002998`, PERMTAGS `c59410d242`,
and SCRATCHGEOM `151c193b63`. No competing PR source or diffs were opened.

## Static validation and inventory

- `python3 -B research/challenge-8/kani-k1/veightinteg/check_veightinteg.py`: PASS.
- Ordinary = **219 = 204 + 15**. Cfg-on = **253 = 219 + 34 opt-in**.
- Full exact names: `ordinary-expected.txt`, `cfg-on-expected.txt`, `opt-in-expected.txt`.
  The 15 new names are in `new-ordinary.txt` and the request; no ordinary root was removed.
- All previous 212 root bodies/attributes are token-identical to v8. Existing verify source
  files except the module documentation/declarations are byte-identical.
- All existing runtime free-function signatures/bodies match upstream and v8 by tokens.
  All runtime-file tokens match REALCONTRACTSTWO, ignoring comments/whitespace.
- New module bodies match authorized sources after cover-hook expansion and identical rustfmt.
  The four ordinary roots differ only in cover omission; all other prior roots are unchanged.
  Four new opt-in roots preserve the original cover-bearing versions exactly after cfg/name
  normalization. Ordinary consumer comparator function-item type and matching PFC are retained.
- Both cfg configurations have no source-reported orphan item/import/macro arm.
- Library diff vs upstream: only smallsort.rs, smallsort/verify* and Cargo.toml check-cfg.
  Existing workflow/research history is inherited; no workflow or tooling was modified.
- rustfmt --check (edition/style 2024, existing codefix config): PASS.
  Wrapper: `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`.
- `git diff --check`: PASS. All verify lines and added runtime lines are <=100 characters.
  Runtime has three inherited longer lines (108/419/422); these bodies were left unchanged.
- Existing request validator: 15 exact SUCCESS roots accepted, controls=false, inventory=true.
- Static expansion is not compiler inventory or proof. GCB inventory must match all 219 names.
  Cfg-on is checked statically only; this build deliberately compiles/verifies with cfg off.

## Source lines

The split counts explicit controls-cfg item spans as opt-in; remaining source, shared helpers,
comments and blank lines are ordinary/shared. This is a physical-line count, not proof size.

| Source | Total | Ordinary/shared | Opt-in only |
| --- | ---: | ---: | ---: |
| verify.rs | 81 | 79 | 2 |
| verify/assembly.rs | 181 | 171 | 10 |
| verify/comparators.rs | 23 | 23 | 0 |
| verify/merge.rs | 802 | 802 | 0 |
| verify/merge/specfix.rs | 415 | 344 | 71 |
| verify/mutations.rs | 27 | 0 | 27 |
| verify/network.rs | 1163 | 1163 | 0 |
| verify/permtags.rs | 229 | 134 | 95 |
| verify/realcontracts.rs | 362 | 225 | 137 |
| verify/scratchgeom.rs | 112 | 83 | 29 |
| verify/smoke.rs | 34 | 34 | 0 |
| verify/types.rs | 172 | 172 | 0 |
| verify/wrap.rs | 271 | 223 | 48 |
| **Verify total** | **3872** | **3453** | **419** |

v8 verify source: 3147 -> 3872 (+725). Runtime smallsort.rs: 866 -> 964 (+98),
all 98 added runtime lines ordinary/shared. Coverage follow-up leaves runtime byte-identical.
Combined verify + runtime: 4836 lines = 4417 ordinary/shared + 419 opt-in.

## Proposed build and prior timing evidence

Run request `veightinteg-g1-20261105-02`; request SHA256:
`67856fbccfcd68a923830ff8fcac6393a245a6a23b1628b4df64c4a31239df81`.
Diagnostic, standard4, inventory=true, controls=false, jobs=1, 10 minutes per harness.
15 new roots only: 150 harness-minutes + 30 overhead = 180-minute Cloud Build timeout.
Maximum reservation: **$2.4300**, within own **$3.00** cap; one primary build, no retry,
at most one compile-error repair if authorized limits and remaining budget permit it.
Main window 240 minutes + closeout 30 minutes; no build window has started.
Budget snapshot: 229 builds, used $96.8460, reserved $2.0250, project cap $118.96.
With this maximum reservation: $101.3010. Snapshot may change; recheck at dispatch.

All 15 roots require SUCCESS and **55/55 covers, zero unreachable covers** after correction.
`expected-covers.json` records exact per-root cover totals; request purpose requires all covers.
The existing request schema supports SUCCESS/FAILED only, so cover acceptance is a separate
mandatory report check. A green runner gate alone does not establish cover acceptance.
Times below are source-reported GCB SUCCESS results, not new integrated proof evidence.
Exact prior report labels and cover counts are retained in `check-report.json`.

| Root (verify::) | Prior seconds | Covers |
| --- | ---: | ---: |
| permtags::network_u8_n13 | 23.773 | 1/2 |
| permtags::network_u8_n9 | 13.415 | 1/2 |
| permtags::tag_types_preserve_source_routes | 0.064 | 1/1 |
| realcontracts::insert_tail_safety_u64_tail1_to4_backing5 | 34.020428 | 7/7 |
| realcontracts::merge_safety_u64_len2 | 27.213285 | 4/4 |
| realcontracts::merge_safety_u64_len4 | 42.305798 | 4/4 |
| realcontracts::sort4_safety_u64 | 36.28767 | 3/3 |
| realcontracts::swap_safety_bytes17_backing4 | 31.84324 | 6/6 |
| realcontracts::swap_safety_u64_backing4 | 19.362135 | 6/6 |
| realcontracts::swap_safety_u8_backing13 | 17.583559 | 6/6 |
| realcontracts::swap_safety_u8_backing4 | 19.355654 | 6/6 |
| realcontracts::swap_safety_u8_backing9 | 17.355093 | 6/6 |
| realcontracts::unstable_network_safety_u8_n13_stubbed | 13.978799 | 1/3 |
| realcontracts::unstable_network_safety_u8_n9_stubbed | 11.660206 | 1/3 |
| scratchgeom::stable_u64_min_scratch_n2 | 3.8116105 | 2/2 |

CI estimate: **312.0294775 seconds (~5 min 12 s)**, sum of prior times for 15 new roots.
This excludes compilation, inventory and other setup; integrated times remain unmeasured.

## Coverage-only correction requested by coordinator

The six unreachable cover instances removed from ordinary are:

| Ordinary roots | Omitted covers | Reason |
| --- | --- | --- |
| realcontracts N9/N13 stubbed | `realcontracts comparator true` (2 instances) | callback cut |
| realcontracts N9/N13 stubbed | `realcontracts comparator false` (2 instances) | callback cut |
| permtags network N9/N13 | `permtags: order violation panic is reachable` (2) | panic unreachable |

Return covers are retained in all four roots. Reachable callback covers remain in every PFC.
For realcontracts, the two cover calls are factored into `comparison_covers(answer)`; ordinary
stubbed consumers replace this coverage-only hook with an empty function. The comparator is
still `arbitrary_less::<u8>` with identical reads, symbolic bool, function-item type and domain.
PFCs and original opt-in consumer copies use the hook with covers. No functional stub was added.
For permtags, the ordinary panic cutoff is an exact copy minus its cover; assume(false) and
unreachable!() are unchanged. The original cutoff and macro remain compiled only with cfg-on.

Original variants remain under cfg(kani_smallsort_controls):

- `realcontracts::unstable_network_safety_u8_n9_stubbed_with_callback_covers`
- `realcontracts::unstable_network_safety_u8_n13_stubbed_with_callback_covers`
- `permtags::network_u8_n9_with_panic_cover`
- `permtags::network_u8_n13_with_panic_cover`

Original reports remain **55/61**; no historical result is rewritten. Corrected ordinary expects
**55/55**, which must be confirmed by the authorized integrated build. The source static check
compares every other root, expands the cover hook, compares the empty hook and panic cutoff,
and checks exact original opt-in variants. It does not claim a new compiler/proof result.
The removal list and reasons are also in verify.rs module documentation.

## Bounded scope and owner decisions

Matched composition domains: u8, backing9/N9 or backing13/N13, the same function-item
`arbitrary_less::<u8>`, arbitrary in-range swap positions, ordinary matching PFC and consumer.
No universal callback frame/order/Drop/ZST proof is claimed. Merge cuts explicit order-violation
panic; no panic-unwinding, uninitialized-memory, value-validity or permission proof is added.
Tag transfer assumes whole-element moves and the same type-selected route, with branches on
answers/positions/lengths/type properties rather than payloads. This is a source-level transfer
assumption, not a machine-checked generic refinement theorem. Mutating comparators excluded.
The owner must decide whether to include runtime-file contracts and the 15 new ordinary roots.

## Authorized slot wait and dispatch

1. Publish the updated exact packet with PRE-BUILD REVIEW <sha>.
2. Run k1g.sh watch on PERMTAGS G2 with separate K1_CACHE; end the turn.
3. On wakeup, confirm terminal slot status, exact pushed SHA and project/own budget.
   Dispatch once on k1-merge. If k1-network is reported free earlier, change only request agent,
   regenerate request validation/hash and publish the exact owner-adjusted packet before dispatch.
4. Record our build identity; run k1g.sh watch BUILD and end the turn without status polling.
5. On wakeup, use bounded k1g summary/rows, inventory, check-tooling, warnings and budget.
   Compare the complete cfg-off SmallSort inventory to all 219 expected names.
6. Require all 15 SUCCESS, each exact expected cover total reached, zero unreachable covers;
   record row time, failed/total checks and covers. A green runner gate alone is insufficient.
7. Write RESULT-VEIGHTINTEG.md <=40 lines; commit/push research separately with [skip ci].
   End with REVIEW REQUEST <sha> / VEIGHTINTEG ЗАВЕРШЁН. No local proof tools or raw logs.
