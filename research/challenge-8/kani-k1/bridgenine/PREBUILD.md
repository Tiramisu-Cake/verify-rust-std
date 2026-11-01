# BRIDGENINE B2 — PRE-BUILD REVIEW

State: **WAITING_FOR_COORDINATOR_GO**. No build submitted; all four rows NOT_RUN.
Worktree `/root/verify-rust-std-kani-bridgenine`, branch `experiment/kani-k1-bridgenine-20261101`.
Task base `2d1d17ca773d97f899006a4c5f84d120e63d4af3`, over B1 result `b7761aa50a`.
Library commit `77cb4c97733d24c1f03f11dc803a2a7676bfc4d5`, library tree
`b903aba7c37e6956dc7b2643b4da79695d54fe4c`.
Kani `9461e07af7ec929f050aa4192f29363c9be07779`, nightly-2026-10-12, cap $88.96.
The published research HEAD handed to the coordinator binds this packet and the exact request.

## Patch and A2 gate

Only `verify/bridge.rs` changes in library; its existing inner controls cfg gates all new code.
Three new proof harnesses share `bridgenine_stable_caller` at bridge.rs:163. It calls the actual
`<u8 as StableSmallSortTypeImpl>::small_sort`; no helper substituted for that API, no panic-cut.
The common local is explicitly `let mut is_less: fn(&u8, &u8) -> bool = LtU8::CMP` (:165).
A/B each set `LtU8::set_probe(kani::any())` once before their arbitrary `[u8;9]` input (:185/:195).
No probe reset occurs in the caller, comparator, adapter or merge body. One pure model oracle
checks key sortedness (`x >> 1`) and full-u8 count for the same probe (:175–179), without F calls.
The pre-count is a scalar snapshot before sorting. Sort4 and insertion run their real bodies.
There is no caller assume on sortedness, geometry, result, input values, or probe equality.

A has no substitutions. B and the negative use the unchanged B1 chain:
`bidirectional_merge<T,F>` -> `adapter<T: FreezeMarker + MergeBridge<F>,F>` -> sole closed
u8/fn-pointer impl -> `merge_profile::<LtU8>(v,dst,*is_less)` verified replacement.
The adapter cover at :37 precedes forwarding. It passes the actual function value unchanged;
the profile checks canonical identity and sorted halves at specfix.rs:317–318.
Only merge is abstracted: no Sort4ReadU64/other profile, new blanket impl or transmute.
Source A2 compatibility is established; dynamic premise discharge/substitution awaits G1.

## Actual caller <-> existing independent leaf

Source anchors: smallsort.rs:49–61 (Freeze Stable entry), :220–292 (general with scratch),
merge.rs:1058–1094 (leaf fixture/PFC macro), :1112 (selected N9 instantiation).
`DOMAINS-v4.md` was read with `git show experiment/kani-k1-domains-20261101:...`;
M03 is the matching stable domain. M02 exact-array and M04 general backing are distinct.
The audit P0-B and addendum A1/A2 were treated as data, not proof of this new caller.

| Field | Actual Stable N9 caller | Selected leaf stable=true branch (M03) |
|---|---|---|
| Target/T/F | merge_profile / u8 / fn(&u8,&u8)->bool via B1 adapter | same target/T/F |
| F/model/probe | LtU8::CMP; key x>>1, full u8; independent shared LtU8 probe | same |
| Source backing | caller-owned `[MaybeUninit<u8>;48]`, initially all uninit | same backing type/init |
| Source span | scratch+0, N9; prefix9 initialized, tail39 uninit | same span/init |
| Half geometry | split4+5; left[0..4), right[4..9) | same |
| Sorted halves | real sort4 writes [0..4), [4..8); insertion extends right to [4..9) | profile requires |
| Destination | original initialized `[u8;9]`, v+0, distinct allocation | arbitrary initialized `[u8;9]`, +0, distinct allocation |
| Frame | merge summary writes only destination9; source/probe untouched | PFC enforces destination9-only modifies |
| Properties | final model sortedness and original-input full-u8 count | sortedness and source-to-destination full-u8 count |

The real caller's initialized destination values can correlate with scratch source; the leaf
allows independent arbitrary values, including all such correlations. Scratch initialization
arises from real writes in B. Leaf input prefix9 is arbitrary under the sorted-halves premise,
covering the runs produced by real helpers; no extra caller assume grants that premise.
Caller pre-count -> scratch source count must follow from real sort4/insertion; merge summary
provides source count -> destination count. G1 must establish the final original-input oracle.
The leaf's symbolic stable bool also checks M04 and both backing covers; its full VT/RSS is
charged to B. No new leaf or transfer from exact N3/N9 is claimed. Leaf has no raw->adapter
stub, no verified self replacement, and executes merge_profile -> actual raw merge.

## Exact G1 rows and acceptance

Full prefix is `slice::sort::shared::smallsort::verify::`.

| # | Suffix | Expected | Covers by construction |
|---|---|---|---|
| A | bridge::bridgenine_direct_u8_n9 | SUCCESS | Stable entry, return/oracle (2/2) |
| B | bridge::bridgenine_caller_u8_n9 | SUCCESS | same two plus adapter-entered (3/3) |
| leaf | merge::merge_scratch48_contract_u8_n9 | SUCCESS | general and stable backing (2/2) |
| control | bridge::bridgenine_payload_flip_u8_n9 | FAILED count only | same as B, all before assertions (3/3) |

Control witness: p arbitrary, probe=p, input=[p;9]. After actual Stable returns, caller flips
`v[0] ^= 1` at bridge.rs:171, outside the callee. All keys remain p>>1, hence sortedness must pass.
Count is 9 before and 8 after. The sole expected failure is literal
`bridgenine output preserves full-value probe count`, kani::assert at bridge.rs:176–179.
Request `expect_check` is that exact literal. Confirm actual source location and assertion class;
compile/unsupported/timeout/unwind/requires/assigns/sortedness failures do not count as this control.
If Kani reports the invocation line, it is bridge.rs:176 (expression :177, message :178).
All SUCCESS rows require every cover satisfied; control covers also precede the failure.
Request gate matching alone does not replace checking all failed properties and locations.

## Static validation and measurement plan

`check_bridgenine.py` / `static-check-prebuild.json`: 17/17 checks pass; ordinary exact200 equals
base and frozen `integwrapfix/ordinary-expected.txt`. Names SHA-256
`1ea7bb6585d8cff99db84a6fcd99e61a5928537817b34c92c5c4579cd610b621`.
Cfg-on forecast388 ->391, exact delta the three new names; native inventory is NOT_RUN.
Existing B1 code behavior is unchanged. Production code, profiles, leaf and tooling are byte-identical.
Request validates; `g1.args.txt`, `g1.runner.txt`, `g1.rustflags.txt` record exact selection.
Changed Rust file passes mandated rustfmt wrapper/config, edition2024; Rust lines <=100 columns.
`git diff --check` passes. No local cargo/rustc/Kani/CBMC/proof run.

After G1, record each row status, verification time, checks/unreachable, covers, failure locations
and per-harness sampled CBMC RSS with attribution. Compare VT(B)+VT(leaf) against VT(A), and
max(RSS(B),RSS(leaf)) against RSS(A). Compiler RSS and whole-build wall/cost are separate.
Missing attribution is UNKNOWN, not a guessed per-row peak. The old v4 function-item run is not A.
No acceleration claim if B+leaf is slower; no W1 completion, N16 feasibility or macOS conclusion.
Compilation, all premises/covers, full-value control sensitivity and costs remain NOT_RUN.
Uninit checks stay off; matched storage geometry does not establish an initialization detector.

## Request, budget and stop boundary

`RUN-REQUEST.json` equals `bridgenine/g1.request.json`, request_id `bridgenine-g1-20261101`.
Measurement, controls=true, jobs1, uninit=false, timeout10 min per harness, k1-standard4 only.
4x10 +30 =70 min full envelope, reserve **$0.9450**. Task <=2 builds / total <=$1.50.
Own submitted UUIDs: none; own fact_spent=$0, reserved=$0. G1 reservation is prospective only.
Budget snapshot: project used $73.4775, other unfinished reserved $1.3500, cap $88.96
(`budget-prebuild.txt`); including G1 would total $75.7725. Refresh after GO before dispatch.
G2 only on compile error or actual leaf mismatch needing a distinct leaf, with separate GO and
own fact_spent plus new full reserve <=$1.50. No G2 authorization is inferred from a G1 GO.

**Stop here. Wait for coordinator GO on the published review SHA.** After GO, refresh budget,
dispatch the reviewed branch through k1g.sh, save UUID/request/source identity, invoke
`k1g.sh watch UUID` with CODEX_THREAD_ID and end the turn. On wakeup use bounded K-1
summary/peaks/check-tooling/log-grep/log-lines; no raw/full logs or archives. Evidence Brief and
Select/Merge are outside this K-1 task. Tooling baseline is
`30f77e859903df14b442ff9294d4fbbd44827f20` for post-build check-tooling.
