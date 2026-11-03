# PERMSOLVER PRE-BUILD (G1 request prepared; nothing dispatched)

Runtime Claude Code, executor alone, no subagents. Owner k1-merge, slug permsolver. Prepared 2026-11-03T10:55Z;
T0 not started (starts at the actual G1 dispatch after coordinator GO, and only after COVERCOST 623c19b0 — same owner —
is terminal and accounted). This file registers no phase and grants no dispatch.

## Identities
- Branch `experiment/kani-k1-permsolver-20261103`; base `a7271841047ef010fbbb2719ce01d7018b2d1cc7` (terminal PERMPROBE,
  library tree `6af2d315e125e7dcc4dc5df92a0180b6e941a1be`); task commit `ba1b899a4c` (TASK-PERMSOLVER.md sha256
  b21aab06…5c4c).
- Library commit `33898a9768fac072803c1fb6c685cb64959bfcba`: only `verify/network/posts/perm.rs` (+3, append
  `#[cfg(kani_smallsort_controls)] mod solver;`) and new `verify/network/posts/perm/solver.rs` (+109). Library diff vs base:
  2 files, +112 −0. New library tree **`df160e9b7c5606a5b5528a2d08c0ac6237f9b699`**.
  perm.rs blob dadf765b → 6221903c (sha256 cbd0fe1e…76f1de); first 4793 bytes (= whole base perm.rs) byte-identical (`cmp`).
  solver.rs blob 47406fa2 (sha256 c92a00b8…b81d8, 4046 B). Unchanged: posts.rs c7a83009 (ffda00b6…a522), network.rs
  95356887 (bf31fbe3…bdd6), smallsort.rs d1d7f552 (78fc8fe8…ed61). So all POSTS8/PERMPROBE roots, `quadratic_counts_preserved`,
  parent helpers (`strict_less`, `count_matching_values`, `is_sorted_by`, `prefix_unchanged`) and the runtime are unchanged.
- Lane files (k1g.sh LANE_PATHS) at HEAD equal frozen tooling `30f77e859903df14b442ff9294d4fbbd44827f20` (`git diff --stat`
  empty). Kani `9461e07af7ec929f050aa4192f29363c9be07779`, nightly-2026-10-12. `check-tooling BUILD 30f77e85…` after the Build.
  Kissat: same pin/image/setup on which PERMPROBE `perm_index_kissat_u64_n8` ran kissat (Build 87487311, kissat PID seen in
  peaks); nothing installed or changed here. If absent on the image it is a blocker (row not substituted).

## Source scope / visibility
Child `network::posts::perm::solver` reaches `perm::quadratic_counts_preserved` as `super::…` and the parent network helpers as
`super::super::super::…`: private items of ancestors are visible to descendants, so **no visibility change**. No macro, stub,
PFC, contract, summary, payload assume, `any_where`, width cut. All 4 roots are `#[kani::proof] #[kani::unwind(25)]
#[kani::solver(kissat)]`. The POSTS8 body is not extracted into a helper (it is the `#[kani::proof]` fn itself), so
`perm_arbitrary_kissat_u64_n8` is a copy; the quadratic root calls the existing helper directly.

## Byte-diff of new bodies vs originals (`permsolver/body-diff.txt`, sha256 0903960a…8c25; `permsolver/body_diff.py`)
Whitespace-normalized (rustfmt rewraps longer paths), paths mapped back to the original module
(`super::super::super::` → `super::` vs posts.rs; → `super::super::` and `super::quadratic_counts_preserved` → bare vs perm.rs):
- `perm_arbitrary_kissat_u64_n8` vs `posts::partposts_count_u64_n8`: + `#[kani::solver(kissat)]`, fn name, and −1 line
  `kani::cover(v.len() == 8, "partposts count: sort returns normally at length 8")`. Setup, probe, entry, assert and its literal
  `partposts: full-value count preserved`, the two kept covers and their literals are identical. **Flag:** the dropped cover
  follows the task's explicit list "те же covers: sort moves, check reached" and gate 2/2 (same cover count as the PERMPROBE
  kissat row); it is trivially true after return. If the coordinator wants the byte-identical body, restoring that one line is the
  only change (gate would then be 3/3).
- `perm_quadratic_kissat_u64_n8` vs `perm::perm_quadratic_u64_n8`: + `#[kani::solver(kissat)]` and fn name only.
- `perm_arbitrary_kissat_negative_u64_n8` vs `posts::partposts_count_negative_u64_n8`: + solver, name, literals renamed
  `partposts count control: …` → `permsolver arbitrary control: …`, `count check reached` → `check reached`, designated
  `partposts negative: full-value count preserved` → `permsolver negative: arbitrary count`. Statements identical.
- `perm_quadratic_kissat_negative_u64_n8` vs `perm::perm_quadratic_negative_u64_n8`: + solver, name, literals
  `permprobe …` → `permsolver …`. Statements identical.

## Metatheorem (see PERMPROBE/PREBUILD.md, RESULT-PERMPROBE.md)
Arbitrary probe: `∀ probe: u64. count(pre, probe) = count(post, probe)` is the definition of multiset equality.
O(N²): `∀ i<8. count(pre, pre[i]) = count(post, pre[i])`; the multiplicities of the distinct values S of pre sum to 8 = len(post),
so post has no room for y ∉ S and count(post, y) = 0 = count(pre, y): equivalent to the arbitrary probe on this domain (and to
PERMPROBE's index probe). The solver attribute changes only the SAT backend of the same CBMC goal, not the claim. Inputs stay
full 64-bit; no speed-up is assumed.

## Annotations / covers / literals (prefix `verify::network::posts::perm::solver::`)
| Root | Line | Input / probe | Asserts in order (literal) | Covers |
|---|---:|---|---|---|
| perm_arbitrary_kissat_u64_n8 | 17 | any `[u64;8]`, probe any u64 | `partposts: full-value count preserved` | 2: `partposts count: sort moves elements` (!prefix_unchanged) / `partposts count: check reached the end` |
| perm_quadratic_kissat_u64_n8 | 38 | any `[u64;8]` | `permprobe: quadratic counts preserved` | 2: `permprobe quadratic: sort moves elements` / `… check reached` |
| perm_arbitrary_kissat_negative_u64_n8 | 57 | `[P;8]`, probe P | `… initial sortedness`, `… initial count`; v7=Q; `… sortedness after overwrite`; **`permsolver negative: arbitrary count`** | 2: `permsolver arbitrary control: returned before corruption` / `… check reached` (before final assert) |
| perm_quadratic_kissat_negative_u64_n8 | 89 | `[P;8]` | `… initial counts`; v7=Q; `… sortedness after overwrite`; **`permsolver negative: quadratic count`** | 2: `permsolver quadratic control: returned before corruption` / `… check reached` (before final assert) |

P=1<<40, Q=1<<41 only in controls. `[P;8]` stays `[P;8]` after the entry, initial checks pass; v7=Q keeps order (`Q<P` false)
and count(P) 8→7, so only the designated literal fails. Every literal in solver.rs occurs once there; neither designated literal is
a substring of another literal. Covers only in roots, none after a failing assert. Unexpected failure (UB, unwinding, coverage,
other literal) is not counted as intended-negative.

## Static inventory / format (`cleanup/source_inventory.py` imported by a scratch script on base archive and HEAD; no report written)
- Ordinary 202 → 202, sorted-name sha256 d5d55502…42e5 at both. cfg-on 393 → 397; opt-in 191 → 195. Exact delta +4 −0:
  `perm::solver::{perm_arbitrary_kissat_u64_n8:17, perm_quadratic_kissat_u64_n8:38, perm_arbitrary_kissat_negative_u64_n8:57,
  perm_quadratic_kissat_negative_u64_n8:89}`, origin direct, gates [kani_smallsort_controls].
- PFC 36 unchanged: solver.rs has no `proof_for_contract` (text sites in smallsort tree 27 = base); `integwrapfix/pfc_order.py`
  ordinary pfc sites 16 bad 0 at base and HEAD. Native inventory not run.
- rustfmt (TASK-DIRECT wrapper, `--edition 2024`, fmtcfg/rustfmt.toml) applied to solver.rs, then `--check` on network.rs,
  posts.rs, perm.rs, solver.rs: exit 0; no line > 100, no trailing whitespace, `git diff --check` clean. All bindings used
  (`pre`, `probe`, `cmp`, `P`, `Q`, both imports); no `_`-prefixed or unused variables → no new warnings expected.
  No local cargo/rustc/Kani/CBMC.

## Request (validated by `kani_k1.py validate --require-runner gcb-e2-standard-4 --max-total-minutes 720`: 4 accepted)
`RUN-REQUEST.json` = `permsolver/g1.request.json`, request_id **permsolver-g1-kissat-oracles-u64n8-20261103**, sha256
**2c2307e35ef19034b4959bc515d7e20ee914bc51a9cd234659aa5c363cff9314**. Rows: arbitrary+kissat SUCCESS, quadratic+kissat SUCCESS,
arbitrary negative FAILED `permsolver negative: arbitrary count`, quadratic negative FAILED `permsolver negative: quadratic count`.
kind measurement, agent k1-merge, runner gcb-e2-standard-4 (k1-standard4, 4 vCPU/16 GiB, swap off), controls true (rustflags
`--cfg kani_smallsort_controls`), kani_jobs 1, uninit_checks false, harness_timeout_minutes 10, full names, args
`--exact --harness-timeout 10m --jobs=1 --output-format=terse`. No highmem/new request fields/solver CLI flag (kissat only via
the root attribute).

## Budget / slots / window (k1g.sh budget, 2026-11-03T10:52Z)
- Project: 189 builds, used $83.9130, reserved by unfinished $1.4850 (expected COVERCOST 623c19b0 on k1-merge + ROUTESCD on
  k1-network — coordinator to confirm), cap $88.96. + G1 reserve (4×10+30)×$0.0135 = **$0.945** → $86.343 ≤ $88.96.
- Slots: dispatch only after COVERCOST is terminal and accounted; then project unfinished ≤ 2 (ROUTESCD may run), k1-merge 1.
  Before dispatch I re-run `k1g.sh budget` and re-check spent + reserves ≤ cap.
- Own cap $1.00: one Build $0.945; no retry/G2. A single compile-error repair only with new review/GO if own spent + reserve
  ≤ $1.00.
- Window: T0 at dispatch; main 120 min ⊇ envelope 70 min + finishing; closeout 30 min.
