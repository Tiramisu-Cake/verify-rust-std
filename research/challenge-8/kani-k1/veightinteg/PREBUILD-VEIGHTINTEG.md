# VEIGHTINTEG — exact pre-build packet

Status: READY FOR REVIEW; no build dispatched. Await explicit coordinator GO.
k1-network is reserved for ENSURES; k1-merge is occupied by PERMTAGS G2.
The request selects k1-network; GO must confirm the slot is free before dispatch.

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

All three commits are library-only and carry `[skip ci]`; research is committed separately.
Sources are only our authorized REALCONTRACTSTWO `588c002998`, PERMTAGS `c59410d242`,
and SCRATCHGEOM `151c193b63`. No competing PR source or diffs were opened.

## Static validation and inventory

- `python3 -B research/challenge-8/kani-k1/veightinteg/check_veightinteg.py`: PASS.
- Ordinary = **219 = 204 + 15**. Cfg-on = **249 = 219 + 30 opt-in**.
- Full exact names: `ordinary-expected.txt`, `cfg-on-expected.txt`, `opt-in-expected.txt`.
  The 15 new names are in `new-ordinary.txt` and the request; no ordinary root was removed.
- All previous 212 root bodies/attributes are token-identical to v8. Existing verify source
  files except the module documentation/declarations are byte-identical.
- All existing runtime free-function signatures/bodies match upstream and v8 by tokens.
  All runtime-file tokens match REALCONTRACTSTWO, ignoring comments/whitespace.
- New module bodies match the authorized sources after identical rustfmt formatting;
  changes are cfg gates, gated imports, documentation and formatting/trailing commas.
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
| verify.rs | 76 | 74 | 2 |
| verify/assembly.rs | 181 | 171 | 10 |
| verify/comparators.rs | 23 | 23 | 0 |
| verify/merge.rs | 802 | 802 | 0 |
| verify/merge/specfix.rs | 415 | 344 | 71 |
| verify/mutations.rs | 27 | 0 | 27 |
| verify/network.rs | 1163 | 1163 | 0 |
| verify/permtags.rs | 198 | 127 | 71 |
| verify/realcontracts.rs | 336 | 213 | 123 |
| verify/scratchgeom.rs | 112 | 83 | 29 |
| verify/smoke.rs | 34 | 34 | 0 |
| verify/types.rs | 172 | 172 | 0 |
| verify/wrap.rs | 271 | 223 | 48 |
| **Verify total** | **3810** | **3429** | **381** |

v8 verify source: 3147 -> 3810 (+663). Runtime smallsort.rs: 866 -> 964 (+98),
all 98 added lines ordinary/shared (contracts, cfg(kani) use and geometry helpers).
Combined verify + full runtime file: 4774 lines = 4393 ordinary/shared + 381 opt-in.

## Proposed build and prior timing evidence

Run request `veightinteg-g1-20261105-01`; request SHA256:
`1f55dc32633f4b3078286dfabc40cd9a8a0178c1411413924f2523a36966fb9b`.
Diagnostic, standard4, inventory=true, controls=false, jobs=1, 10 minutes per harness.
15 new roots only: 150 harness-minutes + 30 overhead = 180-minute Cloud Build timeout.
Maximum reservation: **$2.4300**, within own **$3.00** cap; one primary build, no retry,
at most one compile-error repair if authorized limits and remaining budget permit it.
Main window 240 minutes + closeout 30 minutes; no build window has started.
Budget snapshot: 228 builds, used $96.8460, reserved $1.0800, project cap $118.96.
With this maximum reservation: $100.3560. Snapshot may change; recheck at dispatch.

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

## Covers requiring coordinator review

Prior source reports give **55/61 satisfied covers**, with six expected unreachable covers:

- Each stubbed N9/N13 consumer: 1/3 (return reached, callback true/false cut by swap stub).
- Each permtags N9/N13 network: 1/2 (normal return reached, order-violation panic unreachable).

All other prior covers were reached. Every new root has a reachable normal-return witness.
The task says SUCCESS and all covers. Literal 61/61 conflicts with the preserved sources.
Coordinator decision required before GO: accept the six documented unreachable covers,
or specify a source/acceptance adjustment. No acceptance criterion has been relaxed here.

## Bounded scope and owner decisions

Matched composition domains: u8, backing9/N9 or backing13/N13, the same function-item
`arbitrary_less::<u8>`, arbitrary in-range swap positions, ordinary matching PFC and consumer.
No universal callback frame/order/Drop/ZST proof is claimed. Merge cuts explicit order-violation
panic; no panic-unwinding, uninitialized-memory, value-validity or permission proof is added.
Tag transfer assumes whole-element moves and the same type-selected route, with branches on
answers/positions/lengths/type properties rather than payloads. This is a source-level transfer
assumption, not a machine-checked generic refinement theorem. Mutating comparators excluded.
The owner must decide whether to include runtime-file contracts and the 15 new ordinary roots.

## After coordinator GO

1. Confirm exact pushed SHA, k1-network slot and project/own budget. Do not change this packet.
2. Dispatch once via `research/challenge-8/kani-k1/tools/k1g.sh dispatch BRANCH`.
3. Run `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`, then end the turn.
4. On wakeup, use bounded k1g summary/rows, inventory, check-tooling, warnings and budget.
   Compare the complete cfg-off SmallSort inventory to the 219 expected names and hash.
5. Report each row status, time, failed/total checks and covers, preserving unreachable covers.
   Write RESULT-VEIGHTINTEG.md <=40 lines; commit/push research separately with [skip ci].
6. End with REVIEW REQUEST <sha> / VEIGHTINTEG ЗАВЕРШЁН. No local proof tools or raw logs.
