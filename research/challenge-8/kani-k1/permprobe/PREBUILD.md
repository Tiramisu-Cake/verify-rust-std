# PERMPROBE PRE-BUILD (G1 request prepared; nothing dispatched)

Runtime Claude Code, executor alone, no subagents. Owner k1-merge, slug permprobe. Prepared 2026-11-03T10:00Z;
T0 not started (starts at the actual G1 dispatch after coordinator GO). This file registers no phase and grants no dispatch.

## Identities
- Branch `experiment/kani-k1-permprobe-20261103`; base `4d0121052b630a05ce4c282849510899237ed262` (terminal PART2-POSTS8,
  library tree `d646cb402b0e5fdad30a0c37d4428e6828aef8f8`); task commit `9c9f7af42d` (TASK-PERMPROBE.md sha256 9b9e2a80…4cb7).
- Library commit `7151b012eb03c67b3f4ea9ae07154740a1f548ca`: only `verify/network/posts.rs` (+3, append) and new
  `verify/network/posts/perm.rs` (+131). New library tree **`6af2d315e125e7dcc4dc5df92a0180b6e941a1be`**.
  posts.rs blob 6e4ba051 → c7a83009 (sha256 ffda00b6…a522); perm.rs blob dadf765b (sha256 a65c6c38…8ccb0);
  network.rs blob 95356887 unchanged (sha256 bf31fbe3…bdd6); smallsort.rs blob d1d7f552 unchanged (sha256 78fc8fe8…ed61).
- Old roots preservation: the first 3811 bytes of new posts.rs (= whole base file) are byte-identical (`cmp`); the library
  diff vs base has 0 removed lines. So all 4 POSTS8 roots, parent network.rs (`network_correctness_u64_n8`, `strict_less`,
  `is_sorted_by`, `count_matching_values`, `prefix_unchanged`) and the whole runtime are unchanged.
- Lane files (k1g.sh LANE_PATHS) at HEAD equal frozen tooling `30f77e859903df14b442ff9294d4fbbd44827f20` (`git diff --stat`
  empty). Kani `9461e07af7ec929f050aa4192f29363c9be07779`, channel nightly-2026-10-12. `check-tooling BUILD 30f77e85…` after
  the Build. Kissat: the pinned setup installs Kissat 4.0.1 (`check_kissat_version.sh` / `install_deps.sh` in run-kani.sh and
  gcb-k1.sh; used on GCB in C3B screen 45a0dd0c). Not installed or changed by this task; if absent on the image it is a
  blocker reported as such (row not substituted).

## Semantic diff (`posts.rs` end: `#[cfg(kani_smallsort_controls)] mod perm;`)
Child `network::posts::perm` reaches parent-private helpers as `super::super::…` (no visibility change); no macro.
All 5 roots are plain `#[kani::proof] #[kani::unwind(25)]` fns (+ `#[kani::solver(kissat)]` on one); no stub, PFC, contract,
summary, payload assume, width cut. The only `any_where` is the index `j < 8` (a position, not a payload constraint).
Common setup = `partposts_count_u64_n8`: `[u64;8]=kani::any()` (full 64 bits, offset 0), `pre = v` before the entry,
inferred `let mut cmp = super::super::strict_less::<u64>;`, `<u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp)`
(route unchanged from POSTS8: network → presorted 1 → insertion offset 1 → no_merge). Counts use the parent typed
`count_matching_values` (u64 eq, usize count, no masks/casts). Helpers (no covers): `quadratic_counts_preserved(pre, v)`
= ∀i<pre.len(): count(pre,pre[i]) == count(v,pre[i]); `index_probe_entry_u64_n8()` = setup, `j=any_where(<8)`,
`probe=pre[j]` **before** the entry, entry, assert, returns (v, pre). Roots 1 and 3 have byte-identical bodies (same helper,
same cover literals); the only difference is `#[kani::solver(kissat)]`.

| Root (`verify::network::posts::perm::`) | Line | Input / probe | Asserts in order (literal) | Root covers (after return + post-check) |
|---|---:|---|---|---|
| perm_index_u64_n8 | 48 | any `[u64;8]`, probe=pre[j], j<8 | `permprobe: index count preserved` | 2: `permprobe index: sort moves elements` (!prefix_unchanged) / `permprobe index: check reached` |
| perm_quadratic_u64_n8 | 59 | any `[u64;8]`, no j | `permprobe: quadratic counts preserved` | 2: `permprobe quadratic: sort moves elements` / `… check reached` |
| perm_index_kissat_u64_n8 | 75 | = root 1 | = root 1 | = root 1 |
| perm_index_negative_u64_n8 | 86 | `[P;8]`, probe=pre[j], j<8 | `permprobe index control: initial count`; v7=Q; `… sortedness after overwrite`; **`permprobe negative: index count`** | 2: returned before corruption / check reached (before final assert) |
| perm_quadratic_negative_u64_n8 | 114 | `[P;8]` | `permprobe quadratic control: initial counts`; v7=Q; `… sortedness after overwrite`; **`permprobe negative: quadratic count`** | 2: returned before corruption / check reached (before final assert) |

P=1<<40, Q=1<<41 (low 32 bits equal) only in controls. Controls: `[P;8]` stays after the entry; initial oracle passes;
v7=Q keeps order (`Q<P` false) and count(P) 8→7, so only the designated literal fails (for every j). No designated literal
is a substring of any other literal. No cover after a failing assert, none in helpers. Unexpected failure (UB, unwinding,
coverage, other literal) is not counted as intended-negative.

## Metatheorem (both oracles ≡ old "∀ u64 probe count preserved" on this domain)
**Index-probe.** Let S be the set of distinct values of pre. A universal `j<8` checks count_post(x) = count_pre(x) for all
x ∈ S. Σ_{x∈S} count_pre(x) = 8 = len(post), so Σ_{x∈S} count_post(x) = 8 and post has no room for values outside S;
for y ∉ S count_post(y) = 0 = count_pre(y). Hence post is a multiset permutation of pre; duplicates allowed.
Conversely a permutation satisfies every probe. **O(N²).** The same, unrolled over all i<8 (no j).
**Result.** Both are equivalent to the old claim on this domain. "2⁶⁴ → N" describes only the probe choice; inputs stay
full 64-bit; speed-up is not known in advance. The old count root is not rerun (TIMEOUT 600 on the same pin/profile).

## Static inventory / format (`cleanup/source_inventory.py` functions imported in a scratch script; no report written)
- Ordinary 202 → 202, names identical (sha256 of sorted list d5d55502…42e5); cfg-on 388 → 393; opt-in 186 → 191.
  Exact delta +5 (perm.rs lines 48, 59, 75, 86, 114; origin direct; gates [kani_smallsort_controls]), −0.
  PFC 36 unchanged (no proof_for_contract in perm.rs; smallsort total site count 18 = base). `integwrapfix/pfc_order.py`:
  ordinary pfc sites 16 bad 0. Native inventory not run.
- rustfmt (TASK-DIRECT wrapper, `--edition 2024`, fmtcfg/rustfmt.toml) applied to perm.rs, then `--check` on network.rs,
  posts.rs, perm.rs: exit 0; no line > 100, no trailing whitespace, `git diff --check` clean.

## Request (validated by `kani_k1.py validate --require-runner gcb-e2-standard-4 --max-total-minutes 720`: 5 accepted)
`permprobe/g1.request.json` = RUN-REQUEST.json, request_id **permprobe-g1-oracles-u64n8-20261103**, sha256
**07ad4c6d7cfc43e42a1bc89958ad6ae2f04c19a07abe319b93b365b9ebf3f32e**. Rows: 3 positives SUCCESS; index_negative FAILED
`permprobe negative: index count`; quadratic_negative FAILED `permprobe negative: quadratic count`.
kind measurement, agent k1-merge, runner gcb-e2-standard-4 (k1-standard4, 4 vCPU/16 GiB, swap off), controls true
(rustflags `--cfg kani_smallsort_controls`), kani_jobs 1, uninit_checks false, harness_timeout_minutes 10, full names,
args `--exact --harness-timeout 10m --jobs=1 --output-format=terse`. No highmem/new request fields/solver CLI flag
(kissat only via the root attribute).

## Budget / slots / window (k1g.sh budget, 2026-11-03 ~10:00Z)
- Project: 184 builds, used $82.7925, reserved by unfinished $0.9450 (1 unfinished; expected SAFETYNET, k1-network —
  coordinator to confirm), cap $88.96. + G1 reserve (5×10+30)×$0.0135 = $1.080 → $84.8175 ≤ $88.96.
- Slots: G1 makes 2 unfinished in project (≤ 2), k1-merge 1 (≤ 1).
- Own cap $1.10: one Build $1.080; no retry/G2. A single compile-error repair only with new review/GO if own spent +
  reserve ≤ $1.10.
- Window: T0 at dispatch; main 120 min ⊇ envelope 80 min + finishing; closeout 30 min.
