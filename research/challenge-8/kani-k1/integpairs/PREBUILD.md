# INTEGPAIRS — PRE-BUILD G1 (network u8 N9 + u64 N9 pairs, same Build)

Runtime Claude Code, no subagents; owner **k1-merge**, slug integpairs. Task `TASK-INTEGPAIRS.md` (2571ffee39).
**Dispatch only after coordinator GO and after terminal/accounting of WRAPMORE G2 (same owner slot).**

## Identities and tree

| Item | Value |
|---|---|
| Branch / base | `experiment/kani-k1-integpairs-20261103` from `415044485b599f6337387650f0dfdefea8d5fb42` (= INV2 terminal `6ff24c756c` + cherry-pick of cap commit `e8e238db9d`) |
| Library commit / tree | `2756f0e2a6ae0956fdb427574eda39b5b9a76e64` / `a45388ac593c809405558ea0c27599f487b17e4e`; `HEAD:library` = `6ff24c756c:library` = a45388ac… (unchanged; `git diff 6ff24c756c HEAD` touches only TASK-INTEGPAIRS.md, k1g.sh cap, and this stage's research files) |
| Inventory | cfg-on 438 confirmed by INV2 Build `02b46b34-d19c-47c1-9f96-52f84d72467b` (parttreeinv2/g1.inventory-check.json); expected file `parttwotree/cfg-on-expected.txt` sha256 `da9bcae2…b578f1b` |
| Request | `RUN-REQUEST.json` = `integpairs/g1.request.json`, request_id `integpairs-g1-n9-u8-u64-pairs-20261103`, sha256 `b1c5ace07562274a69a78a6dc30c1557ff894f309038d595ef44b7be1e30fb2c` |
| Profile | measurement, gcb-e2-standard-4 (k1-standard4), controls:true, kani_jobs:1, uninit_checks:false, harness_timeout_minutes:10; Kani `9461e07af7ec929f050aa4192f29363c9be07779` (tool_config/kani-version.toml) |
| Lane args (validator) | 8 × `--harness <full>` + `--exact --harness-timeout 10m --jobs=1 --output-format=terse`; `kani_k1.py validate --require-runner gcb-e2-standard-4` accepted 8 |

## Tooling vs e8e238db9d87323fa4da011a1a8b37fb76ec91c0

`git diff e8e238db9d HEAD -- <k1g.sh LANE_PATHS>` is **empty** (lane files byte-equal). e8e238db9d itself differs from frozen
`30f77e85` in lane paths only by k1g.sh `CAP_USD` 88.96→93.96 and its comment. Bound blobs at HEAD: cloudbuild.yaml
`b25a2647`, kani_k1.py `8c3cfd6b`, gcb-k1.sh `5b02f39d`, kani.yml `8673ecfa`, run-kani.sh `55227b29`, kani-version.toml
`e121de6e`. Post-run: `k1g.sh check-tooling BUILD e8e238db9d…` must PASS.

## Name check (8 rows)

`integpairs/check_integpairs.py g1` (stdlib, `python3 -I -B`, output `g1.static-check.json`): ok, problems [].
Each full name occurs exactly once in cfg-on-expected (also as substring: no `--exact` prefix ambiguity) and in the INV2
pages; each is a proof-matrix.tsv row with the same expect; request harness list/expects/literals equal the matrix in
order; profile fields as above. Error paths checked: INV2 request → exit 1 (3 problems); G1 request with a wrong
expect_check → ok=false.

## Rows, literals, covers (proof-matrix.tsv; source of the integrated tree)

| # | Row (`…verify::network::`) | Role | Expect | Literal / reported line | Covers | Unwind | Historical ref (not credit) |
|---|---|---|---|---|---|---|---|
| 1 | `netcomp::netcomp_leaf_u8_n9` | leaf, PFC `swap_net9` | SUCCESS | – | 7/7 | 25 (:49) | NETCOMP G1 b3e257d1 |
| 2 | `netcomp::netcomp_composed_u8_n9` | consumer | SUCCESS | – | 6/6 | 25 (:204) | NETCOMP2 44af7732 B9 |
| 3 | `netcomp::netcomp_wrong_cmp_u8_n9` | control | FAILED | `netcomp canonical comparator required` @netcomp.rs:122 | 2/2 | 25 (:217) | NETCOMP G1 b3e257d1 |
| 4 | `netcomp::netcomp_count_negative_u8_n9` | control | FAILED | `netcomp N9 negative: full-value count preserved` @netcomp.rs:242 (literal :244) | 3/3 | 25 (:231) | NETCOMP2 44af7732 |
| 5 | `u64nine::u64nine_leaf_u64_n9` | leaf, PFC `swap_u64_net9` | SUCCESS | – | 7/7 | 25 (:50) | U64-N9 62bb5025 |
| 6 | `u64nine::u64nine_composed_u64_n9` | consumer | SUCCESS | – | 7/7 | 25 (:172) | U64-N9 62bb5025 |
| 7 | `u64nine::u64nine_wrong_cmp_u64_n9` | control | FAILED | `u64nine canonical comparator required` @u64nine.rs:123 | 2/2 | 25 (:208) | U64-N9 62bb5025 |
| 8 | `u64nine::u64nine_count_negative_u64_n9` | control | FAILED | `u64nine N9 negative: full-value count preserved` @u64nine.rs:235 (literal :237) | 3/3 | 25 (:222) | U64-N9 62bb5025 |

Sources of expectations/literals: matrix rows; RESULT-NETCOMP2 (`58d464ce1c`), NETCOMP G1 request (`0944189023`),
NETCOMP2 request (`bd5d2bf059`), RESULT-U64-N9 (`9ab925b157`). Note: `netcomp canonical comparator required` occurs
twice in netcomp.rs (N9 adapter :122, N13 adapter :354); in row 3 only `adapter9` is stubbed in, so the post-run
check requires the located failed check at **:122**. Lane gate only matches the substring; the stage gate additionally
requires failed = 1/total, located at the matrix line, and covers = matrix.

## Pair domains (source `verify/network/netcomp.rs`, `verify/network/u64nine.rs`)

| Field | netcomp u8 N9 leaf (#1) | netcomp u8 N9 consumer (#2) | u64nine N9 leaf (#5) | u64nine N9 consumer (#6) |
|---|---|---|---|---|
| T | u8 | u8 | u64 | u64 |
| F category | fn-pointer `U8Cmp = fn(&u8,&u8)->bool` (:12) | same; `&mut U8Cmp` to actual entry | fn-pointer `U64Cmp` (:13) | same; `&mut U64Cmp` |
| CMP value | `StrictU8::CMP` = reified `strict_less::<u8>` (network.rs identity_profile!, `a < b`) | same (:176) | `StrictU64::CMP` = `strict_less::<u64>` | same (:177) |
| canonical test | `cmp as *const () == StrictU8::CMP as *const ()` (specfix.rs:133) as `requires` | adapter guard :121–122 before summary | same with StrictU64 (`requires`) | guard u64nine.rs:122–123 |
| Probe domain / transfer | `probe: u8 = any()`; passed by value as 5th arg of `swap_net9` | `probe: u8 = any()`; `register9` stores it in CONTEXT9 before entry; adapter passes `ctx.probe` by value | `probe: u64 = any()` by value | `probe: u64 = any()` via `register`/CONTEXT_U64_NINE; cover high-bit probe >255 |
| Backing / offset | local `[u8;9] = any()`, `v.as_mut_ptr()`, offset 0; `region9` requires exact 9-elem readable/writable same allocation | same exact `[u8;9]`, offset 0; adapter asserts `v == ctx.base` | `[u64;9] = any()`, offset 0, `region9_u64` | same, `v == ctx.base` |
| Pair | any distinct `a,b < 9` | the 25 fixed pairs of `sort9_optimal`; adapter asserts distinct in range | any distinct `a,b < 9` | 25 fixed pairs |
| Prefix / scratch / init | full init, no scratch, no prefix split | full init; N9 < 18 → `no_merge`, unused uninit `stack_array`, no merge/scratch; insertion with presorted 9 = empty suffix | as u8 leaf | as u8 consumer |
| Frame | `modifies(v+a, v+b)`; root asserts other 7 unchanged + pair transfer/order/count | summary frame only; context frame base/probe/initial_count, hits == 25, per-exchange count invariant | as u8 leaf | as u8 consumer |
| Binding chain | PFC of `swap_net9` (:36–46): real body → real `swap_if_less` | `run9` → `<u8 as UnstableSmallSortTypeImpl>::small_sort` (smallsort.rs:90) → Freeze+Copy impl (:142) → `small_sort_network` (:311, `size_of ≤ 8`, 1×32 ≤ 4096) → `sort9_optimal` (:420, 25 raw `swap_if_less`) → `#[kani::stub(swap_if_less, adapter9)]` → `<u8 as SwapBridge9<U8Cmp>>::exchange` (:116, sole impl) → `swap_net9` replaced by `#[kani::stub_verified]` contract | PFC of `swap_u64_net9` (:37–47) | `run9` → `<u64 as UnstableSmallSortTypeImpl>::small_sort` → same route (8×32 ≤ 4096) → stub `adapter_u64nine` → `SwapBridgeU64Nine<U64Cmp>::exchange` (:117) → `stub_verified(swap_u64_net9)` |

Controls share the consumer route: wrong-cmp passes `always_true_u8/u64` (fails the adapter guard before the summary);
count controls use concrete inputs (`[0;9]`/probe 0, `v[8]=1`; `[1<<40;9]`, `v[8]=1<<41`) after the composed run.
Leaf and consumer of each pair share T, F, CMP, exact backing9/offset 0, and probe type; the consumer's hits are only the
pairs of sort9, all inside the leaf's quantified `a≠b<9` domain.

## Budget / slots

`integpairs/budget-prebuild.txt`: builds 195, used **$86.2350**, reserved $0.0000, cap $93.96. G1 reserve
(8×10+30)×$0.0135 = **$1.485** ≤ own cap $3.00 (G1+G2 = $2.970). Project after G1 reserve $87.720 + any WRAPMORE G2
reserve ≤ $93.96 — re-run `k1g.sh budget` immediately before dispatch; dispatch refuses over cap itself. Slots: ≤ 1
unfinished on k1-merge (WRAPMORE G2 must be terminal/accounted first), ≤ 2 project. No retry; compile-error repair only
under the task's rule. G2 PRE-BUILD after G1 terminal/accounting.

## Post-run plan (bounded only)

`k1g.sh wait` (background) → `status`, `check-tooling … e8e238db9d…`, `summary`, `peaks` pages, bounded `log-grep`
for `Checking harness` timestamps; no raw logs/archives/Cloud Logging.
