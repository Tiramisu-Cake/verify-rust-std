# PART2-POSTS8 PRE-BUILD (G1 and G2 requests prepared; nothing dispatched)

Runtime Claude Code, executor alone, no subagents. Owner k1-network, slug partposts. Prepared 2026-11-02T20:18Z;
T0 not started (starts at the actual G1 dispatch after coordinator GO). This file registers no phase and grants no dispatch.

## Identities
- Branch `experiment/kani-k1-partposts-20261102`; base `2104e7a596fabb058a99c8bcdf0e3f487d9a7753` (PART2-FAST, library
  tree `d4ec476a7a001363e58f19948c188a9c2078e370`); task commit `9f4712c29c` (TASK-PART2-POSTS8.md sha256 cd726621…39b6).
- Library commit `6fe5864e8d51e5750f77f3e762cb61de9061a7b8`: only `verify/network.rs` (+3, append) and new
  `verify/network/posts.rs` (+92). New library tree **`d646cb402b0e5fdad30a0c37d4428e6828aef8f8`**; G1 and G2 use it.
  network.rs blob 1a85a483 → 95356887 (sha256 bf31fbe3…bdd6); posts.rs blob 6e4ba051 (sha256 b08346da…eb6d);
  smallsort.rs blob d1d7f552 unchanged (sha256 78fc8fe8…ed61).
- Old combined source preservation: the first 54177 bytes of new network.rs are byte-identical to the base file (`cmp`);
  `git diff 2104e7a596 6fe5864e8d -- library` has no removed line. So `network_correctness_u64_n8`, its macro
  `network_correctness_cases` (962-976), `network_correctness_fixed` (945-960), `strict_less` (941-943), `is_sorted_by`
  (113-122), `count_matching_values` (102-112), `prefix_unchanged` (51-60) and the whole runtime are unchanged.
- Lane files (k1g.sh LANE_PATHS) at HEAD equal frozen tooling `30f77e859903df14b442ff9294d4fbbd44827f20` (`git diff --stat`
  empty). Kani `9461e07af7ec929f050aa4192f29363c9be07779`, channel nightly-2026-10-12. `check-tooling BUILD 30f77e85…`
  after each Build. Controls guard (gcb-k1.sh 52-57): no `kani_smallsort_controls` outside verify/, verify.rs, Cargo.toml.

## Semantic diff (`network.rs` end: `#[cfg(kani_smallsort_controls)] mod posts;`)
Child `network::posts` reaches parent-private helpers as `super::…` (no visibility change); no parent macro call.
All 4 roots are plain `#[kani::proof] #[kani::unwind(25)]` fns; no stub, PFC, contract, summary, assume/any_where.

| Root (`verify::network::posts::`) | Input / probe | Asserts in order (literal) | Root covers |
|---|---|---|---|
| partposts_sorted_u64_n8 | `[u64;8]=any`, `_probe:u64=any` (unused) | is_sorted_by `partposts: sortedness` | 3: moves / len 8 / end |
| partposts_count_u64_n8 | `[u64;8]=any`, `probe:u64=any` | count(pre,probe)==count(v,probe) `partposts: full-value count preserved` | 3: moves / len 8 / end |
| partposts_order_negative_u64_n8 | `[P,P,P,P,P,P,P,Q]`, P | initial sorted, initial count; swap v0/v7; count after swap; **`partposts negative: sortedness`** | 2: returned before corruption / order check reached |
| partposts_count_negative_u64_n8 | `[P;8]`, P | initial sorted, initial count; v7=Q; sortedness after overwrite; **`partposts negative: full-value count preserved`** | 2: returned before corruption / count check reached |

Common setup = old checker: `pre = v` before entry; `let mut cmp = super::strict_less::<u64>;` (inferred existing
function item, `a < b`, no fn-pointer coercion); `<u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp)`.
P=1<<40, Q=1<<41 (low 32 bits equal) only in controls. Every positive cover is after the return and its post-check;
control covers are before the final (designated) assert, none after it, none in helpers. `kani::assert` instead of the
old `assert!` only keeps the literal in the property description (same check, as in merge/specdiag.rs).
Cover mapping (fixed N8 instead of macro selector `len: any_where(8)` + `match`): old `N<2 || !prefix_unchanged(&v,&pre,0)`
= `!prefix_unchanged(&v,&pre,0)` at N8; old `len == 8` → `v.len() == 8` after return; old `true` family end → `true`.

## Equivalence / replacement logic
Same T=u64, exact initialized backing 8, offset 0, same F, same actual entry and executions. Route (smallsort.rs 88-101,
156-170, 311-349, 574-600): Freeze+Copy, size 8 ≤ 8 → small_sort_network; len 8 < 9 → presorted_len 1, actual
insertion_sort_shift_left offset 1 → raw insert_tail tails 1..7; no_merge → return. No sort9/sort13/merge.
Sorted root proves sortedness for every input; count root proves count equality for every input **and every independent
full-width probe**, i.e. full-value multiset preservation. Together they give the old combined claim (in the old root the
count assert was reached only on paths that passed sortedness; here it is checked without that premise). Each root also
carries all safety/unwinding checks of the actual entry. Omitting the other post does not change the sort: `is_sorted_by`
and `count_matching_values` only read `v`, `strict_less` is pure; no global probe/ghost state. One PASS alone does not
close the combined domain. Negative witnesses: order — entry leaves the sorted input as is, both initial posts hold, the
swap keeps count(P)=7, then `Q,P` violates order → only the designated literal fails. count — `[P;8]` stays, v7=Q keeps
order (`Q<P` false), count(P) 8→7 → only the designated literal fails. Both distinguish values only by high bits.

## Static inventory / ordering / format (`cleanup/source_inventory.py` functions imported in a scratch script, no report written)
- Ordinary 202, names identical to base (sha256 of sorted list d5d55502…42e5); cfg-on 384 → 388; opt-in 182 → 186.
  Exact delta: +4 names above (posts.rs lines 14, 28, 45, 70; origin direct; gates [kani_smallsort_controls]), −0.
  PFC 36 unchanged (no PFC in posts). `integwrapfix/pfc_order.py`: ordinary pfc sites 16 bad 0. Native inventory not run.
- rustfmt `--check --edition 2024` (TASK-DIRECT wrapper/config) on network.rs (recurses into posts.rs) and posts.rs: exit 0;
  no line > 100, no trailing whitespace/tabs, `git diff --check` clean. Tool unit tests 82 OK (python only).

## Requests (both validated by `kani_k1.py validate --require-runner gcb-e2-standard-4 --max-total-minutes 720`)
| File | request_id | sha256 | Rows |
|---|---|---|---|
| partposts/g1.request.json = RUN-REQUEST.json (G1 commit) | partposts-g1-baseline-u64n8-20261102 | 8f30cf6b82c864321515cf635d960ceae27b7fe51a742d4e1beb7753b7b106d5 | old `network::network_correctness_u64_n8` SUCCESS |
| partposts/g2.request.json (copied to RUN-REQUEST.json only in the G2 commit) | partposts-g2-split-u64n8-20261102 | 0326ea4419bb30a3c60545cc9cb9727067a0ef7119e7a01f0efd13a19918a170 | sorted, count SUCCESS; order_negative FAILED `partposts negative: sortedness`; count_negative FAILED `partposts negative: full-value count preserved` |

Both: kind measurement, agent k1-network, runner gcb-e2-standard-4 (k1-standard4, 4 vCPU/16 GiB, swap off), controls true
(rustflags `--cfg kani_smallsort_controls`), kani_jobs 1, uninit_checks false, harness_timeout_minutes 10, full names,
args `--exact --harness-timeout 10m --jobs=1 --output-format=terse`. No highmem/resource kind/solver flags/list prep.
The tool's FAILED gate needs a located failed check containing the literal; "only designated" is checked in RESULT from
the failed-check list (initial/after-corruption literals differ and do not contain the designated substrings).

## Budget / slots / window (k1g.sh budget, 2026-11-02 ~20:15Z)
- Project: 181 builds, used $82.2930, reserved by unfinished $0.0000, cap $88.96. Unfinished builds 0 → G1 makes 1 (≤2),
  k1-network none. G1 reserve (10+30)×$0.0135=$0.540 → $82.833; with G2 $0.945 → $83.778 ≤ $88.96 (no cap raise).
- Own cap $2.50: plan $1.485; one shared compile-error repeat ≤ $0.945 → full-reserve ceiling $2.430. Max 3 Builds.
- Window: T0 at G1 dispatch; G1 envelope 40 min + G2 70 min + finishing fit main 180 min; G2 after G1 terminal/accounting.
- Night limit: tonight PART2-FAST spent $0.513; current night total/limit is a coordinator check before GO.
